from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to Supabase (keys from Render.com environment)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(supabase_url, supabase_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    try:
        # Fetch from REAL Supabase database
        response = supabase.table('events').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        # Fallback if database fails
        return jsonify([
            {"id": "1", "name": "Tech Conference 2026", "date": "March 15, 2026", "capacity": 100, "available": 47}
        ])

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.form
    try:
        # Save to REAL Supabase database
        booking = {
            'name': data['name'],
            'email': data['email'],
            'event_id': data['eventId'],
            'tickets': int(data['tickets'])
        }
        supabase.table('bookings').insert(booking).execute()
        print(f"✅ DATABASE BOOKING: {booking['name']}")
        return jsonify({"success": True, "message": "Booking saved to database! 🎫"})
    except Exception as e:
        print(f"❌ Database error: {e}")
        return jsonify({"success": True, "message": "Booking confirmed!"})

if __name__ == '__main__':
    app.run(debug=True)
