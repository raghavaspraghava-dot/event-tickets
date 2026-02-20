from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import ADMIN_EMAIL, ADMIN_PASSWORD
from database import supabase

admin_bp = Blueprint("admin", __name__)

ADMIN_HASH = generate_password_hash(ADMIN_PASSWORD)

@admin_bp.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["email"] == ADMIN_EMAIL and check_password_hash(ADMIN_HASH, request.form["password"]):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@admin_bp.route("/admin/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    events = supabase.table("events").select("*").execute().data
    bookings = supabase.table("bookings").select("*").execute().data

    return render_template("dashboard.html",
                           events_count=len(events),
                           bookings_count=len(bookings))

@admin_bp.route("/admin/events")
def manage_events():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    events = supabase.table("events").select("*").execute().data
    return render_template("admin.html", events=events)