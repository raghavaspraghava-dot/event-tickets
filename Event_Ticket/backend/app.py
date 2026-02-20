import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import Config
import hashlib
import uuid
import traceback

# Global Supabase client
supabase_client = None

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

def get_supabase_client():
    global supabase_client
    if supabase_client is None:
        try:
            if 'dummy' not in app.config['SUPABASE_KEY']:
                import supabase
                supabase_client = supabase.create_client(
                    app.config['SUPABASE_URL'], 
                    app.config['SUPABASE_KEY']
                )
                print("✅ Supabase connected!")
                
                # 🔍 TEST TABLES EXIST
                tables = supabase_client.rpc('get_tables', {}).execute()
                print(f"📋 Available tables: {tables}")
                
            else:
                print("⚠️ DUMMY KEYS - NO DATABASE OPERATIONS")
                supabase_client = None
        except Exception as e:
            print(f"❌ Supabase setup failed: {e}")
            print(traceback.format_exc())
            supabase_client = None
    return supabase_client

ADMIN_EMAIL = app.config['ADMIN_EMAIL']
ADMIN_PASSWORD = app.config['ADMIN_PASSWORD']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🎯 FIXED FRONTEND ROUTING
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    VALID_PAGES = ['index.html', 'admin.html', 'admin_login.html', 'dashboard.html', 'register.html', 'user_login.html']
    
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
    except FileNotFoundError:
        return jsonify({"error": "Frontend missing"}), 404

# 🔧 FIXED USER LOGIN (Better Error Handling)
@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
    client = get_supabase_client()
    if not client:
        return jsonify({'error': '🚫 Database not configured (check Supabase keys)'}), 503
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔍 User login attempt: {email}")
        
        # Check if user exists
        response = client.table('users').select('*').eq('email', email).execute()
        print(f"👤 Found users: {len(response.data)}")
        
        if not response.data:
            # Create new user
            client.table('users').insert({
                'email': email,
                'password': hash_password(password)
            }).execute()
            print(f"✅ New user created: {email}")
            return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
        
        # Verify password
        if response.data[0]['password'] == hash_password(password):
            print(f"✅ User login success: {email}")
            return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
        else:
            print(f"❌ Wrong password for: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"❌ User login ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# 🔧 FIXED ADMIN LOGIN
@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        print(f"🔍 Admin login attempt: {data.get('email')}")
        
        if data.get('email') == ADMIN_EMAIL and data.get('password') == ADMIN_PASSWORD:
            token = f'admin-{uuid.uuid4()}'
            print(f"✅ Admin login success")
            return jsonify({'token': token}), 200
        return jsonify({'error': 'Invalid admin credentials'}), 401
    except Exception as e:
        print(f"❌ Admin login ERROR: {e}")
        return jsonify({'error': str(e)}), 500

# 🔧 FIXED EVENTS (CREATE + READ)
@app.route('/api/events', methods=['GET'])
def get_events():
    client = get_supabase_client()
    if not client:
        print("⚠️ No Supabase - returning empty events")
        return jsonify([]), 200
    
    try:
        print("🔍 Fetching events...")
        response = client.table('events').select('*').order('date').execute()
        print(f"📋 Found {len(response.data)} events")
        return jsonify(response.data), 200
    except Exception as e:
        print(f"❌ Events fetch ERROR: {e}")
        print(traceback.format_exc())
        return jsonify([]), 200

@app.route('/api/events', methods=['POST'])
def create_event():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or not token.startswith('admin-'):
        print("🚫 Admin token missing")
        return jsonify({'error': 'Admin required'}), 403
    
    client = get_supabase_client()
    if not client:
        print("🚫 No database connection")
        return jsonify({'error': 'Database not configured'}), 503
    
    try:
        data = request.get_json()
        print(f"➕ Creating event: {data['title']}")
        
        event = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data['description'],
            'date': data['date'],
            'total_tickets': data['total_tickets']
        }
        
        # 🚀 INSERT WITH ERROR CHECKING
        response = client.table('events').insert(event).execute()
        print(f"✅ Event created! Response: {response.data}")
        
        return jsonify({'message': 'Event created successfully!'}), 201
        
    except Exception as e:
        print(f"❌ Event creation ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to create event: {str(e)}'}), 500

# 🔧 FIXED TICKET REGISTRATION
@app.route('/api/tickets/register', methods=['POST'])
def register_tickets():
    client = get_supabase_client()
    if not client:
        return jsonify({'error': 'Database not configured'}), 503
    
    try:
        data = request.get_json()
        print(f"🎫 Registering {data['tickets']} tickets for {data['email']}")
        
        # Get event
        event_response = client.table('events').select('total_tickets').eq('id', data['event_id']).execute()
        if not event_response.data:
            return jsonify({'error': 'Event not found'}), 404
        
        event = event_response.data[0]
        if event['total_tickets'] < data['tickets']:
            return jsonify({'error': 'Not enough tickets available'}), 400
        
        # Register tickets
        client.table('registrations').insert({
            'user_email': data['email'],
            'event_id': data['event_id'],
            'tickets': data['tickets']
        }).execute()
        
        # Update tickets
        client.table('events').update({
            'total_tickets': event['total_tickets'] - data['tickets']
        }).eq('id', data['event_id']).execute()
        
        print(f"✅ Tickets registered for {data['email']}")
        return jsonify({'message': 'Tickets registered successfully!'}), 201
        
    except Exception as e:
        print(f"❌ Ticket registration ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    client = get_supabase_client()
    return jsonify({
        "status": "🟢 LIVE",
        "supabase": "✅ Connected" if client else "❌ Missing keys",
        "tables_ready": "✅ Ready" if client else "⚠️ Configure Supabase"
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Event Ticket System...")
    print(f"Admin: {ADMIN_EMAIL}/{ADMIN_PASSWORD}")
    app.run(debug=True, host='0.0.0.0', port=5000)
