from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from database import supabase, ADMIN_HASH
from werkzeug.security import check_password_hash
from config import Config

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if (email == Config.ADMIN_EMAIL and 
            check_password_hash(ADMIN_HASH, password)):
            session['admin_logged_in'] = True
            flash('✅ Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('❌ Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('✅ Logged out!', 'success')
    return redirect(url_for('auth.admin_login'))
