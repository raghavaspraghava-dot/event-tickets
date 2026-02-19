from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

EVENTS_FILE = 'events.json'
BOOKINGS_FILE = 'bookings.json'

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    events = load_data(EVENTS_FILE)
    if not events:
        events = [
            {"id": "1", "name": "Tech Conference 2026", "date": "March 15, 2026", "capacity": 100, "available": 47},
            {"id": "2", "name": "Music Festival", "date": "April 22, 2026", "capacity": 100, "available": 23},
            {"id": "3", "name": "Startup Pitch Night", "date": "May 10, 2026", "capacity": 100, "available": 89}
        ]
        save_data(EVENTS_FILE, events)
    return jsonify(events)

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.form
    bookings = load_data(BOOKINGS_FILE)
    
    booking = {
        'id': len(bookings) + 1,
        'name': data['name'],
        'email': data['email'],
        'event_id': data['eventId'],
        'tickets': int(data['tickets']),
        'created_at': '2026-02-19'
    }
    
    bookings.append(booking)
    save_data(BOOKINGS_FILE, bookings)
    
    print(f"✅ NEW BOOKING: {booking['name']} - {booking['tickets']} tickets")
    return jsonify({"success": True, "message": "Booking confirmed! 🎫"})

if __name__ == '__main__':
    app.run(debug=True)
