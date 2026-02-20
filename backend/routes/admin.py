from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import supabase
from mcp.tools import safe_count
from mcp.control import MCPController

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@admin.route('/dashboard')
def dashboard():
    if not MCPController.is_admin():
        return redirect(url_for('auth.admin_login'))
    
    events_count = safe_count('events')
    bookings_count = safe_count('bookings')
    
    return render_template('admin_dashboard.html', 
                         bookings_count=bookings_count, 
                         events_count=events_count)

@admin.route('/events/add', methods=['POST'])
def add_event():
    if not MCPController.is_admin():
        return redirect(url_for('auth.admin_login'))
    
    try:
        from mcp.tools import get_next_event_id
        next_id = get_next_event_id()
        
        event_data = {
            'id': next_id,
            'name': request.form['name'],
            'date': request.form['date'],
            'capacity': int(request.form['capacity']),
            'available': int(request.form['available'])
        }
        
        if supabase:
            supabase.table('events').insert(event_data).execute()
        
        flash(f'✅ Event #{next_id} "{event_data["name"]}" added!', 'success')
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('events.admin_events'))

@admin.route('/events/delete/<int:event_id>')
def delete_event(event_id):
    if not MCPController.is_admin():
        return redirect(url_for('auth.admin_login'))
    
    try:
        if supabase:
            supabase.table('bookings').delete().eq('event_id', event_id).execute()
            supabase.table('events').delete().eq('id', event_id).execute()
            flash('✅ Event + bookings deleted!', 'success')
    except Exception as e:
        flash(f'❌ Delete failed: {str(e)}', 'error')
    
    return redirect(url_for('events.admin_events'))
