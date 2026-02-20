from flask import Blueprint, jsonify
from database import get_supabase_client

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token.startswith('admin-token-'):
            return jsonify({'error': 'Admin access required'}), 403
        
        client = get_supabase_client()
        
        # Total events
        events = client.table('events').select('count', count='exact').execute()
        total_events = events.count
        
        # Total tickets booked
        registrations = client.table('registrations').select('sum(tickets)', count='exact').execute()
        total_tickets = sum([r['tickets'] for r in registrations.data]) if registrations.data else 0
        
        return jsonify({
            'total_events': total_events,
            'total_tickets': total_tickets
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
