from flask import Blueprint, request, jsonify
from database import get_supabase_client
from config import Config
import hashlib
import uuid

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/auth/user-login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        client = get_supabase_client()
        
        # Check if user exists
        response = client.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            # Auto-register user if doesn't exist
            hashed_pw = hash_password(password)
            client.table('users').insert({
                'email': email,
                'password': hashed_pw
            }).execute()
            return jsonify({'token': 'user-token-' + str(uuid.uuid4()), 'message': 'User registered and logged in'}), 200
        
        user = response.data[0]
        hashed_pw = hash_password(password)
        
        if user['password'] == hashed_pw:
            token = 'user-token-' + str(uuid.uuid4())
            return jsonify({'token': token, 'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/admin-login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if (email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD):
            token = 'admin-token-' + str(uuid.uuid4())
            return jsonify({'token': token, 'message': 'Admin login successful'}), 200
        else:
            return jsonify({'error': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
