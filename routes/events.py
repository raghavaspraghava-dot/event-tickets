from flask import Blueprint, jsonify
from database import supabase

events_bp = Blueprint("events", __name__)

@events_bp.route("/api/events")
def get_events():
    if supabase:
        response = supabase.table("events").select("*").execute()
        return jsonify(response.data or [])
    return jsonify([])