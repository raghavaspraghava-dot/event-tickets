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

@app.route('/api/events', methods=['POST'])
def create_event():
    """➕ CREATE EVENT - FULL DEBUG VERSION"""
    try:
        print("\n" + "="*60)
        print("🚀 CREATE EVENT DEBUG START")
        print("="*60)
        
        # 🔍 1. CHECK INCOMING REQUEST
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(f"🔍 TOKEN: {token[:30] if token else '❌ MISSING'}...")
        print(f"📡 HEADERS: Authorization={bool(token)}, Content-Type={request.content_type}")
        
        # 2. VALIDATE ADMIN TOKEN
        if not token or not token.startswith('admin-'):
            print("❌ BLOCKED: Invalid or missing admin token")
            return jsonify({'error': 'Admin access required - login as admin@example.com/admin123'}), 403
        
        print("✅ TOKEN VALIDATED ✓")
        
        # 3. CHECK DATABASE
        client = db.get_client()
        if not client:
            print("❌ BLOCKED: Database connection failed")
            return jsonify({'error': 'Database unavailable - check Supabase'}), 503
        print("✅ DATABASE CONNECTED ✓")
        
        # 4. PARSE REQUEST DATA
        data = request.get_json()
        print(f"📥 RAW DATA RECEIVED: {data}")
        
        if not data:
            print("❌ BLOCKED: No JSON data in request")
            return jsonify({'error': 'No data sent from frontend'}), 400
        
        # 5. VALIDATE FIELDS
        required_fields = ['title', 'description', 'date', 'total_tickets']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            print(f"❌ BLOCKED: Missing fields: {missing}")
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        print("✅ DATA VALIDATED ✓")
        
        # 6. PREPARE EVENT
        event_id = str(uuid.uuid4())[:8]
        event = {
            'id': event_id,
            'title': str(data['title'])[:100],
            'description': str(data['description'])[:500],
            'date': str(data['date']),
            'total_tickets': int(data['total_tickets']),
            'created_at': datetime.now().isoformat()
        }
        print(f"📤 EVENT TO INSERT: {event}")
        
        # 7. ATTEMPT DATABASE INSERT
        print("🔄 Attempting Supabase INSERT...")
        result = client.table('events').insert(event).execute()
        
        print(f"✅ SUPABASE RESULT: status_code={result.status_code}")
        print(f"✅ SUPABASE DATA: {result.data}")
        print(f"✅ SUPABASE COUNT: {len(result.data) if result.data else 0}")
        
        print("="*60)
        print("✅ EVENT CREATION SUCCESSFUL!")
        print("="*60)
        
        return jsonify({
            'message': 'Event created successfully!',
            'event_id': event_id,
            'debug_info': 'Check Render logs above'
        }), 201
        
    except KeyError as e:
        print(f"💥 KEY ERROR: {e}")
        print("Frontend sent wrong field names!")
        return jsonify({'error': f'Missing field: {e}'}), 400
        
    except ValueError as e:
        print(f"💥 VALUE ERROR: {e}")
        return jsonify({'error': f'Invalid data type: {e}'}), 400
        
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# 🎫 REGISTER TICKETS - ✅ FIXED F-STRING
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
        # ✅ FIXED: No single } at end
        return jsonify({'message': f'{tickets} tickets registered for {data["name"]}! '}), 201
        
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


