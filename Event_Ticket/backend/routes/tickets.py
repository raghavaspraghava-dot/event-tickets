from flask import Blueprint, request, jsonify
from database import get_supabase_client

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets/register', methods=['POST'])
def register_tickets():
    try:
        data = request.get_json()
        client = get_supabase_client()
        
        # Check if event exists and has enough tickets
        event_response = client.table('events').select('total_tickets').eq('id', data['event_id']).execute()
        if not event_response.data:
            return jsonify({'error': 'Event not found'}), 404
        
        event = event_response.data[0]
        requested_tickets = data['tickets']
        
        if event['total_tickets'] < requested_tickets:
            return jsonify({'error': f'Only {event["total_tickets"]} tickets available'}), 400
        
        # Register tickets
        registration = {
            'user_email': data['email'],
            'event_id': data['event_id'],
            'tickets': requested_tickets
        }
        
        client.table('registrations').insert(registration).execute()
        
        # Update event tickets (simple decrement for demo)
        client.table('events').update({'total_tickets': event['total_tickets'] - requested_tickets}).eq('id', data['event_id']).execute()
        
        return jsonify({'message': f'Successfully registered {requested_tickets} tickets for {data["name"]}'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
