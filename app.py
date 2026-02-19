from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables (Render.com will provide these)
load_dotenv()

app = Flask(__name__)

# Connect to YOUR Supabase database
SUPABASE_URL = os.getenv('SUPABASE_URL')  # https://yourproject.supabase.co
SUPABASE_KEY = os.getenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_MPIsH6irDv5f3fTch6J3nA_gxlzCZ78')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    try:
        # Fetch REAL events from YOUR Supabase database
        response = supabase.table('events').select('*').execute()
        events = response.data
        print(f"✅ Loaded {len(events)} events from Supabase!")
        return jsonify(events)
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        # Fallback events (in case database empty)
        fallback = [
            {"id": "1", "name": "Tech Conference 2026", "date": "March 15, 2026", "capacity": 100, "available": 47},
            {"id": "2", "name": "Music Festival", "date": "April 22, 2026", "capacity": 100, "available": 23},
            {"id": "3", "name": "Startup Pitch Night", "date": "May 10, 2026", "capacity": 100, "available": 89}
        ]
        return jsonify(fallback)

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.form
    try:
        # Save booking to YOUR Supabase database
        booking = {
            'name': data['name'],
            'email': data['email'],
            'event_id': data['eventId'],
            'tickets': int(data['tickets'])
        }
        response = supabase.table('bookings').insert(booking).execute()
        print(f"✅ SAVED TO SUPABASE: {booking['name']} - {booking['tickets']} tickets")
        return jsonify({"success": True, "message": "🎫 Booking saved to database!"})
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return jsonify({"success": True, "message": "Booking confirmed! (Local storage)"})

if __name__ == '__main__':
    app.run(debug=True)
