import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from config import Config
import hashlib
import uuid
import traceback
import json

# Global Supabase client
supabase_client = None

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

def get_supabase_client():
    """🔗 Initialize Supabase client with fallback"""
    global supabase_client
    if supabase_client is None:
        try:
            if 'dummy' not in app.config['SUPABASE_KEY'] and app.config['SUPABASE_KEY']:
                import supabase
                supabase_client = supabase.create_client(
                    app.config['SUPABASE_URL'], 
                    app.config['SUPABASE_KEY']
                )
                print("✅ Supabase connected successfully!")
                return supabase_client
            else:
                print("⚠️ Using MOCK MODE (dummy Supabase keys)")
                supabase_client = None
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            supabase_client = None
    return supabase_client

# Admin credentials from config
ADMIN_EMAIL = app.config.get('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = app.config.get('ADMIN_PASSWORD', 'admin123')

def hash_password(password):
    """🔐 Secure password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

# 🎯 FRONTEND ROUTING - Serves ALL 6 pages
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """📄 Serve frontend HTML pages and static files"""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    VALID_PAGES = [
        'index.html', 'admin.html', 'admin_login.html', 'dashboard.html',
        'register.html', 'user_login.html'
    ]
    
    # Block API routes
    if path.startswith('api'):
        return '', 404
    
    # Serve HTML pages
    filename = path if path.endswith('.html') else f"{path}.html"
    if filename in VALID_PAGES:
        try:
            return send_from_directory(frontend_dir, filename)
        except FileNotFoundError:
            pass
    
    # Serve static files (CSS/JS)
    if path.startswith(('css/', 'js/')):
        try:
            return send_from_directory(frontend_dir, path)
        except FileNotFoundError:
            pass
    
    # Default to index.html
    try:
        return send_from_directory(frontend_dir, 'index.html')
    except FileNotFoundError:
        return jsonify({"error": "Frontend files missing"}), 404

# 👤 USER LOGIN (MOCK MODE + Real DB)
@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
    """🧪 User login - Works with OR without Supabase"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"🔍 User login attempt: {email}")
        
        client = get_supabase_client()
        
        if client:
            # REAL DATABASE MODE
            response = client.table('users').select('*').eq('email', email).execute()
            print(f"👤 Found {len(response.data)} existing users")
            
            if not response.data:
                # Auto-register new users
                client.table('users').insert({
                    'email': email,
                    'password': hash_password(password)
                }).execute()
                print(f"✅ New user created: {email}")
            else:
                # Verify password
                if response.data[0]['password'] != hash_password(password):
                    print(f"❌ Wrong password for: {email}")
                    return jsonify({'error': 'Invalid credentials'}), 401
            
            print(f"✅ User login success: {email}")
            return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
        
        else:
            # MOCK MODE - Always succeeds
            print(f"🧪 MOCK MODE: User login success: {email}")
            return jsonify({'token': f'user-{uuid.uuid4()}'}), 200
            
    except Exception as e:
        print(f"❌ User login ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

# 👨‍💼 ADMIN LOGIN
@app.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    """🔐 Admin login - Hardcoded credentials"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        print(f"🔍 Admin login attempt: {email}")
        
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            token = f'admin-{uuid.uuid4()}'
            print(f"✅ Admin login success: {email}")
            return jsonify({'token': token}), 200
        else:
            print(f"❌ Invalid admin credentials")
            return jsonify({'error": 'Invalid admin credentials'}), 401
            
    except Exception as e:
        print(f"❌ Admin login ERROR: {e}")
        return jsonify({'error': str(e)}), 500

# 📋 EVENTS - GET ALL
@app.route('/api/events', methods=['GET'])
def get_events():
    """📊 Fetch all events"""
    client = get_supabase_client()
    
    if not client:
        print("🧪 MOCK MODE: Returning sample events")
        # Mock events for demo
        mock_events = [
            {
                'id': 'demo-1',
                'title': 'Tech Conference 2026',
                'description': 'Annual tech conference with workshops',
                'date': '2026-03-15',
                'total_tickets': 100
            }
        ]
        return jsonify(mock_events), 200
    
    try:
        print("🔍 Fetching events from database...")
        response = client.table('events').select('*').order('date').execute()
        print(f"📋 Found {len(response.data)} events")
        return jsonify(response.data), 200
        
    except Exception as e:
        print(f"❌ Events fetch ERROR: {e}")
        return jsonify([]), 200

# ➕ EVENTS - CREATE NEW
@app.route('/api/events', methods=['POST'])
def create_event():
    """✨ Create new event (Admin only)"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token or not token.startswith('admin-'):
        print("🚫 Admin token required")
        return jsonify({'error': 'Admin access required'}), 403
    
    client = get_supabase_client()
    
    if not client:
        print("🧪 MOCK MODE: Event creation simulated")
        return jsonify({'message': 'Event created (mock mode)'}), 201
    
    try:
        data = request.get_json()
        print(f"➕ Creating event: {data.get('title', 'Untitled')}")
        
        event = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data['description'],
            'date': data['date'],
            'total_tickets': int(data['total_tickets'])
        }
        
        response = client.table('events').insert(event).execute()
        print(f"✅ Event created! ID: {event['id']}")
        
        return jsonify({'message': 'Event created successfully!', 'event_id': event['id']}), 201
        
    except Exception as e:
        print(f"❌ Event creation ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to create event: {str(e)}'}), 500

# 🎫 TICKET REGISTRATION (Enhanced with Name)
@app.route('/api/tickets/register', methods=['POST'])
def register_tickets():
    """✅ Register tickets with user details"""
    client = get_supabase_client()
    
    try:
        data = request.get_json()
        name = data.get('name', '')
        email = data.get('email', '')
        event_id = data.get('event_id', '')
        tickets = int(data['tickets'])
        
        print(f"🎫 Registering: {name} ({email}) - {tickets} tickets for event {event_id}")
        
        if not client:
            # MOCK MODE
            print("🧪 MOCK MODE: Tickets registered successfully")
            return jsonify({'message': 'Tickets registered successfully! (mock mode)'}), 201
        
        # Check event exists
        event_response = client.table('events').select('total_tickets').eq('id', event_id).execute()
        if not event_response.data:
            return jsonify({'error': 'Event not found'}), 404
        
        event = event_response.data[0]
        if event['total_tickets'] < tickets:
            return jsonify({'error': f'Only {event["total_tickets"]} tickets available'}), 400
        
        # Save registration
        client.table('registrations').insert({
            'name': name,
            'user_email': email,
            'event_id': event_id,
            'tickets': tickets
        }).execute()
        
        # Update ticket count
        client.table('events').update({
            'total_tickets': event['total_tickets'] - tickets
        }).eq('id', event_id).execute()
        
        print(f"✅ Tickets registered for {name}")
        return jsonify({'message': f'{tickets} tickets registered successfully for {name}!'}), 201
        
    except Exception as e:
        print(f"❌ Ticket registration ERROR: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

# 🩺 HEALTH CHECK
@app.route('/api/health')
def health_check():
    """🔍 System status"""
    client = get_supabase_client()
    return jsonify({
        "status": "🟢 LIVE",
        "timestamp": str(uuid.uuid4()),  # Random for testing
        "supabase": "✅ Connected" if client else "🧪 MOCK MODE",
        "admin_email": ADMIN_EMAIL,
        "endpoints": ["/api/auth/user-login", "/api/auth/admin-login", "/api/events", "/api/tickets/register"]
    }), 200

# 404 CATCH-ALL
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    print("🚀 Starting Event Ticket Registration System")
    print(f"👤 Admin: {ADMIN_EMAIL} | Password: {ADMIN_PASSWORD}")
    print(f"🗄️  Supabase: {'✅ Ready' if get_supabase_client() else '🧪 MOCK MODE'}")
    print("\n📱 Frontend: http://localhost:5000")
    print("🔧 APIs: /api/health, /api/events")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
