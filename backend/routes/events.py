from flask import Blueprint, jsonify, request
from database import supabase
from mcp.tools import get_next_event_id

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events')
def get_events():
    if supabase:
        try:
            response = supabase.table('events').select('*').execute()
            return jsonify(response.data or [])
        except:
            pass
    return jsonify([
        {"id": "1", "name": "Tech Conference 2026", "date": "2026-03-15", "capacity": 100, "available": 47}
    ])

@events_bp.route('/admin/events')
def admin_events():
    from mcp.control import MCPController
    if not MCPController.is_admin():
        return redirect(url_for('auth.admin_login'))
    
    events = []
    if supabase:
        try:
            response = supabase.table('events').select('*').execute()
            events = response.data or []
        except:
            pass
    return render_template('admin_events.html', events=events)
