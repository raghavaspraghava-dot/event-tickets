import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import Config
import hashlib
import uuid

# Global Supabase client (lazy loaded)
supabase_client = None

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

def get_supabase_client():
    """Lazy load Supabase client - avoids startup crash"""
    global supabase_client
    if supabase_client is None:
        try:
            # Check if real keys exist
            if 'dummy' not in app.config['SUPABASE_KEY']:
                import supabase
                supabase_client = supabase.create_client(
                    app.config['SUPABASE_URL'], 
                    app.config['SUPABASE_KEY']
                )
                print("✅ Supabase connected!")
            else:
                print("⚠️ Using dummy Supabase keys - add real keys in Render Environment")
                supabase_client = None
        except Exception as e:
            print(f"❌ Supabase error: {e}")
            supabase_client = None
    return supabase_client

ADMIN_EMAIL = app.config['ADMIN_EMAIL']
ADMIN_PASSWORD = app.config['ADMIN_PASSWORD']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🎯 SINGLE FRONTEND ROUTE (Replaces your home route)
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files from ../frontend folder"""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    # Protect API routes (let existing API routes handle them)
    if path.startswith('api'):
        return '', 404
    
    # Serve index.html for SPA routes
    if not path or path == 'index.html' or path.endswith('/'):
        try:
            return send_from_directory(frontend_dir, 'index.html')
        except FileNotFoundError:
            return jsonify({"error": "Frontend not found. Create frontend/index.html"}), 404
    
    # Serve other static files or fallback to index.html
    try:
        return send_from_directory(frontend_dir, path)
    except FileNotFoundError:
        return send_from_directory(frontend_dir, 'index.html')

# API ROUTES (UNCHANGED - your existing code)
@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
    client = get_supabase_client()
    if not client:
        return jsonify({'error': 'Database not configured'}), 503
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    response = client.table('users').select('*').eq('email', email).execute()
    
    if not response.data:
        client.table('users').insert({
            'email': email,
            'password': hash_password(password)
        }).execute()
        return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
    
    if response.data[0]['password'] == hash_password(password):
        return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('email') == ADMIN_EMAIL and data.get('password') == ADMIN_PASSWORD:
        return jsonify({'token': f'admin-{uuid.uuid4()}'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/events', methods=['GET'])
def get_events():
    client = get_supabase_client()
    if not client:
        return jsonify([]), 200
    
    try:
        response = client.table('events').select('*').order('date').execute()
        return jsonify(response.data), 200
    except:
        return jsonify([]), 200

@app.route('/api/events', methods=['POST'])
def create_event():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token.startswith('admin-'):
        return jsonify({'error': 'Admin required'}), 403
    
    client = get_supabase_client()
    if not client:
        return jsonify({'error': 'Database not configured'}), 503
    
    data = request.get_json()
    event = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data['description'],
        'date': data['date'],
        'total_tickets': data['total_tickets']
    }
    client.table('events').insert(event).execute()
    return jsonify({'message': 'Event created'}), 201

@app.route('/api/tickets/register', methods=['POST'])
def register_tickets():
    client = get_supabase_client()
    if not client:
        return jsonify({'error': 'Database not configured'}), 503
    
    data = request.get_json()
    event = client.table('events').select('total_tickets').eq('id', data['event_id']).execute().data[0]
    
    if event['total_tickets'] < data['tickets']:
        return jsonify({'error': 'Not enough tickets'}), 400
    
    client.table('registrations').insert({
        'user_email': data['email'],
        'event_id': data['event_id'],
        'tickets': data['tickets']
    }).execute()
    
    client.table('events').update({
        'total_tickets': event['total_tickets'] - data['tickets']
    }).eq('id', data['event_id']).execute()
    return jsonify({'message': 'Tickets registered!'}), 201

@app.route('/api/health')
def health_check():
    client = get_supabase_client()
    return jsonify({
        "message": "Event Ticket Registration API LIVE!", 
        "supabase_status": "ready" if client else "needs_config"
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
