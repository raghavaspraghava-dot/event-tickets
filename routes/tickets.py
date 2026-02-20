from flask import Blueprint, request, jsonify
from database import supabase

tickets_bp = Blueprint("tickets", __name__)

@tickets_bp.route("/book", methods=["POST"])
def book_ticket():
    data = request.form

    booking = {
        "name": data["name"],
        "email": data["email"],
        "event_id": data["eventId"],
        "tickets": int(data["tickets"])
    }

    if supabase:
        supabase.table("bookings").insert(booking).execute()

    return jsonify({"success": True})