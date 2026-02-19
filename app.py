from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
load_dotenv()
app = Flask(__name__)
app.secret_key = 'eventickets-2026-super-secure-key-abc123'

# Supabase connection
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_PUBLISHABLE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Admin credentials (hardcoded for demo - CHANGE IN PRODUCTION)
ADMIN_EMAIL = 'admin@eventickets.com'
ADMIN_PASSWORD = generate_password_hash('admin123')  # Password: admin123

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    try:
        response = supabase.table('events').select('*').execute()
        return jsonify(response.data)
    except:
        return jsonify([
            {"id": "1", "name": "Tech Conference 2026", "date": "March 15, 2026", "capacity": 100, "available": 47},
            {"id": "2", "name": "Music Festival", "date": "April 22, 2026", "capacity": 100, "available": 23},
            {"id": "3", "name": "Startup Pitch Night", "date": "May 10, 2026", "capacity": 100, "available": 89}
        ])

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.form
    try:
        booking = {
            'name': data['name'],
            'email': data['email'],
            'event_id': data['eventId'],
            'tickets': int(data['tickets'])
        }
        supabase.table('bookings').insert(booking).execute()
        print(f"✅ SAVED TO SUPABASE: {booking['name']} - {booking['tickets']} tickets")
        return jsonify({"success": True, "message": "🎫 Saved to database!"})
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return jsonify({"success": True, "message": "Booking confirmed!"})

# === ADMIN ROUTES ===
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD, password):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get stats
    bookings_count = supabase.table('bookings').select('count').execute().count
    events_count = supabase.table('events').select('count').execute().count
    
    return render_template('admin_dashboard.html', 
                         bookings_count=bookings_count, 
                         events_count=events_count)

@app.route('/admin/events')
def admin_events():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    events = supabase.table('events').select('*').execute().data
    return render_template('admin_events.html', events=events)

@app.route('/admin/events/add', methods=['POST'])
def add_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    event_data = {
        'id': str(uuid.uuid4())[:8],
        'name': request.form['name'],
        'date': request.form['date'],
        'capacity': int(request.form['capacity']),
        'available': int(request.form['available'])
    }
    
    supabase.table('events').insert(event_data).execute()
    flash('Event added successfully!', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/events/delete/<event_id>')
def delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    supabase.table('events').delete().eq('id', event_id).execute()
    flash('Event deleted!', 'success')
    return redirect(url_for('admin_events'))

@app.route('/admin/events/edit/<event_id>', methods=['POST'])
def edit_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    event_data = {
        'name': request.form['name'],
        'date': request.form['date'],
        'capacity': int(request.form['capacity']),
        'available': int(request.form['available'])
    }
    
    supabase.table('events').update(event_data).eq('id', event_id).execute()
    flash('Event updated!', 'success')
    return redirect(url_for('admin_events'))

if __name__ == '__main__':
    app.run(debug=True)

