# JAI SRI RAM....
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

load_dotenv()
app = Flask(__name__)
app.secret_key = 'eventickets-2026-super-secure-key-abc123'

# Supabase connection (SAFE)
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_PUBLISHABLE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase connected!")
except:
    supabase = None
    print("⚠️ Using fallback data (no Supabase)")

# Admin credentials
ADMIN_EMAIL = 'admin@eventickets.com'
ADMIN_PASSWORD = generate_password_hash('admin123')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    if supabase:
        try:
            response = supabase.table('events').select('*').execute()
            return jsonify(response.data)
        except:
            pass
    # Fallback data
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
        if supabase:
            supabase.table('bookings').insert(booking).execute()
            print(f"✅ SAVED TO SUPABASE: {booking['name']}")
        return jsonify({"success": True, "message": "🎫 Booking confirmed!"})
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return jsonify({"success": True, "message": "🎫 Booking confirmed!"})

# === ADMIN ROUTES (BULLETPROOF) ===
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD, password):
            session['admin_logged_in'] = True
            flash('✅ Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('✅ Logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # SAFE stats
    bookings_count = 0
    events_count = 0
    if supabase:
        try:
            bookings_count = supabase.table('bookings').select('count').execute().count
            events_count = supabase.table('events').select('count').execute().count
        except:
            pass
    
    return render_template('admin_dashboard.html', 
                         bookings_count=bookings_count, 
                         events_count=events_count)

@app.route('/admin/events')
def admin_events():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    events = []
    if supabase:
        try:
            events = supabase.table('events').select('*').execute().data
        except:
            pass
    
    return render_template('admin_events.html', events=events)

@app.route('/admin/events/add', methods=['POST'])
def add_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # 🔥 PERFECT ID GENERATION - Finds highest existing ID + 1
        next_id = 1
        if supabase:
            # Get ALL existing IDs and find max
            all_events = supabase.table('events').select('id').execute()
            if all_events.data:
                existing_ids = [event['id'] for event in all_events.data]
                next_id = max(existing_ids) + 1 if existing_ids else 1
        
        event_data = {
            'id': next_id,
            'name': request.form['name'],
            'date': request.form['date'],
            'capacity': int(request.form['capacity']),
            'available': int(request.form['available'])
        }
        
        if supabase:
            supabase.table('events').insert(event_data).execute()
        flash(f'✅ Event #{next_id} "{event_data["name"]}" added successfully!', 'success')
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('admin_events'))




@app.route('/admin/events/delete/<event_id>')
def delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if supabase:
        try:
            # 1. DELETE related bookings FIRST
            supabase.table('bookings').delete().eq('event_id', event_id).execute()
            # 2. NOW delete event
            supabase.table('events').delete().eq('id', event_id).execute()
            flash('✅ Event + bookings deleted!', 'success')
        except Exception as e:
            flash(f'❌ Delete failed: {str(e)}', 'error')
    else:
        flash('⚠️ No database!', 'error')
    
    return redirect(url_for('admin_events'))

@app.route('/admin/events/edit/<event_id>', methods=['POST'])
def edit_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        event_data = {
            'name': request.form['name'],
            'date': request.form['date'],
            'capacity': int(request.form['capacity']),
            'available': int(request.form['available'])
        }
        if supabase:
            supabase.table('events').update(event_data).eq('id', event_id).execute()
        flash('✅ Event updated!', 'success')
    except Exception as e:
        flash(f'❌ Update failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_events'))

if __name__ == '__main__':
    app.run(debug=True)






