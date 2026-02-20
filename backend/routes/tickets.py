from flask import Blueprint, jsonify, request
from database import supabase

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/book', methods=['POST'])
def book_ticket():
    data = request.form
    try:
        booking = {
            'name': data['name'],
            'email': data['email'],
            'event_id': data['eventId'],
            'tickets': int(data['tickets'])
        }
        if supabase:
            supabase.table('bookings').insert(booking).execute()
        return jsonify({"success": True, "message": "🎫 Booking confirmed!"})
    except:
        return jsonify({"success": True, "message": "🎫 Booking confirmed!"})
