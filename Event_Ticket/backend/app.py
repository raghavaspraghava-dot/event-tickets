import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import Config
from database import db
import hashlib
import uuid
import traceback
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🎯 FRONTEND ROUTING - All 6 pages
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    VALID_PAGES = [
        'index.html', 'admin.html', 'admin_login.html', 'dashboard.html',
        'register.html', 'user_login.html'
    ]
    
    if path.startswith('api'):
        return '', 404
    
    filename = path if path.endswith('.html') else f"{path}.html"
    if filename in VALID_PAGES:
        try:
            return send_from_directory(frontend_dir, filename)
        except FileNotFoundError:
            pass
    
    if path.startswith(('css/', 'js/')):
        try:
            return send_from_directory(frontend_dir, path)
        except FileNotFoundError:
            pass
    
    try:
        return send_from_directory(frontend_dir, 'index.html')
    except:
        return jsonify({"error": "Frontend not found"}), 404

# 👤 USER LOGIN
@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
    client = db.get_client()
    if not client:
        return jsonify({'error': 'Database connection failed'}), 503
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"🔍 User login attempt: {email}")
        
        # Check existing user
        response = client.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            # Auto-create new user
            client.table('users').insert({
                'email': email,
                'password': hash_password(password),
                'created_at': datetime.now().isoformat()
            }).execute()
            print(f"✅ Created new user: {email}")
        else:
            # Verify password
            if response.data[0]['password'] != hash_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401
        
        print(f"✅ User authenticated: {email}")
        return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
        
    except Exception as e:
        print(f"❌ User login error: {e}")
        return jsonify({'error': str(e)}), 500

# 👨‍💼 ADMIN LOGIN
@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔍 Admin login: {email}")
        
        if email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD:
            token = f'admin-{uuid.uuid4()}'
            print("✅ Admin login successful")
            return jsonify({'token': token}), 200
        return jsonify({'error': 'Invalid admin credentials'}), 401
        
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return jsonify({'error': str(e)}), 500

# 📋 GET EVENTS
@app.route('/api/events', methods=['GET'])
def get_events():
    client = db.get_client()
    if not client:
        return jsonify({'error': 'Database unavailable'}), 503
    
    try:
        response = client.table('events').select('*').order('date').execute()
        print(f"📋 Retrieved {len(response.data)} events")
        return jsonify(response.data), 200
    except Exception as e:
        print(f"❌ Events error: {e}")
        return jsonify([]), 200

# ➕ CREATE EVENT (Admin only)
@app.route('/api/events', methods=['POST'])
def create_event():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or not token.startswith('admin-'):
        return jsonify({'error': 'Admin required'}), 403
    
    client = db.get_client()
    if not client:
        return jsonify({'error': 'Database unavailable'}), 503
    
    try:
        data = request.get_json()
        event_id = str(uuid.uuid4())
        
        event = {
            'id': event_id,
            'title': data['title'],
            'description': data['description'],
            'date': data['date'],
            'total_tickets': int(data['total_tickets']),
            'created_at': datetime.now().isoformat()
        }
        
        client.table('events').insert(event).execute()
        print(f"✅ Event created: {event['title']}")
        return jsonify({'message': 'Event created!', 'id': event_id}), 201
        
    except Exception as e:
        print(f"❌ Create event error: {e}")
        return jsonify({'error': str(e)}), 500

# 🎫 REGISTER TICKETS
@app.route('/api/tickets/register', methods=['POST'])
def register_tickets():
    client = db.get_client()
    if not client:
        return jsonify({'error': 'Database unavailable'}), 503
    
    try:
        data = request.get_json()
        print(f"🎫 Registration: {data.get('name')} - {data['tickets']} tickets")
        
        # Verify event exists
        event_resp = client.table('events').select('*').eq('id', data['event_id']).execute()
        if not event_resp.data:
            return jsonify({'error': 'Event not found'}), 404
        
        event = event_resp.data[0]
        tickets = int(data['tickets'])
        
        if event['total_tickets'] < tickets:
            return jsonify({'error': f'Only {event["total_tickets"]} tickets available'}), 400
        
        # Create registration
        registration = {
            'name': data['name'],
            'user_email': data['email'],
            'event_id': data['event_id'],
            'tickets': tickets,
            'registered_at': datetime.now().isoformat()
        }
        client.table('registrations').insert(registration).execute()
        
        # Update ticket count
        client.table('events').update({
            'total_tickets': event['total_tickets'] - tickets
        }).eq('id', data['event_id']).execute()
        
        print(f"✅ Registration complete: {data['name']}")
        return jsonify({'message': f'{tickets} tickets registered for {data["name"]}!"}), 201
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({'error': str(e)}), 500

# 🩺 HEALTH CHECK
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': '🟢 LIVE',
        'database': '✅ Connected' if db.is_connected() else '❌ Failed',
        'supabase': Config.SUPABASE_URL,
        'admin': Config.ADMIN_EMAIL
    }), 200

if __name__ == '__main__':
    print("🚀 Event Ticket System - Production Ready")
    print(f"🌐 Supabase: {Config.SUPABASE_URL}")
    print(f"👤 Admin: {Config.ADMIN_EMAIL}")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
