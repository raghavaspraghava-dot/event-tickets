from flask import Blueprint, request, jsonify
from database import get_supabase_client
import uuid

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET'])
def get_events():
    try:
        client = get_supabase_client()
        response = client.table('events').select('*').order('date').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events', methods=['POST'])
def add_event():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token.startswith('admin-token-'):
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        client = get_supabase_client()
        
        new_event = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data['description'],
            'date': data['date'],
            'total_tickets': data['total_tickets']
        }
        
        client.table('events').insert(new_event).execute()
        return jsonify({'message': 'Event created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token.startswith('admin-token-'):
            return jsonify({'error': 'Admin access required'}), 403
        
        client = get_supabase_client()
        client.table('events').delete().eq('id', event_id).execute()
        return jsonify({'message': 'Event deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
