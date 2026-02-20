import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config  # ← Your config.py
import supabase
import hashlib
import uuid

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase client
client = supabase.create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return jsonify({"message": "Event Ticket Registration API LIVE!"}), 200

@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
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
    if data.get('email') == app.config['ADMIN_EMAIL'] and data.get('password') == app.config['ADMIN_PASSWORD']:
        return jsonify({'token': f'admin-{uuid.uuid4()}'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/events', methods=['GET'])
def get_events():
    response = client.table('events').select('*').order('date').execute()
    return jsonify(response.data), 200

@app.route('/api/events', methods=['POST'])
def create_event():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token.startswith('admin-'):
        return jsonify({'error': 'Admin required'}), 403
    
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
    data = request.get_json()
    event = client.table('events').select('total_tickets').eq('id', data['event_id']).execute().data[0]
    
    if event['total_tickets'] < data['tickets']:
        return jsonify({'error': 'Not enough tickets'}), 400
    
    client.table('registrations').insert({
        'user_email': data['email'],
        'event_id': data['event_id'],
        'tickets': data['tickets']
    }).execute()
    
    client.table('events').update({'total_tickets': event['total_tickets'] - data['tickets']}).eq('id', data['event_id']).execute()
    return jsonify({'message': 'Tickets registered!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
