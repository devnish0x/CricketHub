"""
Crickethub - Flask Application Entrypoint
File: app.py
Description:
    Main Flask web application providing secure routes, authentication,
    form processing, role-based authorization, and template rendering
    for the Cricket Training Management System.
    Connects to Oracle Database 21c via thin-mode oracledb.
"""

import os
import logging
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)
from db import check_db_health
from repositories import (
    UserRepo, CricketerRepo, TrainerRepo, ProgramRepo,
    VenueRepo, SessionRepo, EquipmentRepo, PaymentRepo,
    ApplicationRepo, EquipmentIssueRepo, ParticipationRepo,
    DashboardRepo, ReportRepo
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crickethub.app")

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Strict secret key enforcement: NO hardcoded or predictable fallbacks allowed
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "CRITICAL STARTUP ERROR: SECRET_KEY environment variable is not set. "
        "Flask requires a secure SECRET_KEY in your .env file. "
        "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
    )
app.config["SECRET_KEY"] = secret_key

# Cookie and session security
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =====================================================================
# AUTHENTICATION & ROLE-BASED AUTHORIZATION DECORATORS
# =====================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your academy account.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Restricts access to users holding one of the specified roles.
    Allowed roles: 'Super Admin', 'System User', 'Trainer', 'Cricketer'.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in first.", "warning")
                return redirect(url_for("login", next=request.path))
            user_role = session.get("role")
            if user_role not in allowed_roles:
                logger.warning(
                    f"Access denied for user {session.get('user_id')} ({user_role}) "
                    f"attempting to access {request.path}. Required: {allowed_roles}"
                )
                flash("Access denied: You do not possess the required permissions for this action.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Restricts route to Super Admin only."""
    return role_required("Super Admin")(f)


def staff_or_admin_required(f):
    """Restricts route to academy administrative staff (Super Admin, System User)."""
    return role_required("Super Admin", "System User")(f)


def trainer_or_admin_required(f):
    """Restricts route to coaching staff or academy administration."""
    return role_required("Super Admin", "System User", "Trainer")(f)


@app.context_processor
def inject_global_vars():
    """Inject current user details and timestamp into all Jinja templates."""
    return {
        "current_user": {
            "id": session.get("user_id"),
            "name": session.get("name"),
            "role": session.get("role"),
            "cricketer_id": session.get("cricketer_id"),
            "trainer_id": session.get("trainer_id")
        },
        "now": datetime.now()
    }


# =====================================================================
# PUBLIC LANDING PAGE (VISUAL REFERENCE DESIGN)
# =====================================================================
@app.route("/")
def landing():
    """
    Public landing page for Crickethub:
    Features high-resolution cinematic cricket photography, academy intro,
    real database metrics, program offerings, and calls to action.
    """
    try:
        metrics = DashboardRepo.get_metrics()
        counts = metrics.get("counts", {})
    except Exception as e:
        logger.error(f"Error loading public landing metrics: {e}")
        counts = {}

    try:
        programs = ProgramRepo.list_all()
    except Exception as e:
        logger.error(f"Error loading programs for landing page: {e}")
        programs = []

    return render_template(
        "landing.html",
        counts=counts,
        programs=programs[:4]
    )


# =====================================================================
# AUTHENTICATION & REGISTRATION ROUTES
# =====================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Public self-registration for new Cricketers.
    Collects player personal profile and cricket specialization.
    Role is strictly hardcoded to 'Cricketer' to prevent privilege escalation.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        address = request.form.get("address", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "Male")
        batting_style = request.form.get("batting_style", "Right-hand bat")
        bowling_style = request.form.get("bowling_style", "Right-arm medium")
        experience = request.form.get("experience", 0)

        # Basic validations
        if not name or not phone or not password:
            flash("Please fill in all required fields (Name, Phone, and Password).", "danger")
            return render_template("register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters in length.", "danger")
            return render_template("register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match. Please re-enter your password.", "danger")
            return render_template("register.html", form_data=request.form)

        try:
            new_player = CricketerRepo.register_cricketer(
                name=name,
                password=password,
                phone=phone,
                address=address,
                dob=dob,
                gender=gender,
                batting_style=batting_style,
                bowling_style=bowling_style,
                experience=experience
            )

            # Regenerate session and log player in immediately
            session.clear()
            session["user_id"] = new_player["user_id"]
            session["name"] = new_player["name"]
            session["role"] = new_player["role"]
            session["cricketer_id"] = new_player["cricketer_id"]

            flash(f"Welcome to Crickethub, {new_player['name']}! Your player account (ID: {new_player['user_id']}) is ready.", "success")
            return redirect(url_for("dashboard"))

        except ValueError as ve:
            flash(str(ve), "danger")
            return render_template("register.html", form_data=request.form)
        except Exception as e:
            logger.error(f"Error during cricketer registration: {e}")
            flash("A database error occurred during registration. Please verify your details and try again.", "danger")
            return render_template("register.html", form_data=request.form)

    return render_template("register.html", form_data={})


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Sign-in route with session regeneration and brute-force throttling protection.
    Accepts User ID or Phone Number as the login identifier.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Check throttling
        failed_count = session.get("failed_login_attempts", 0)
        if failed_count >= 8:
            flash("Too many failed sign-in attempts. Please close and re-open your browser or wait a moment.", "danger")
            return render_template("login.html")

        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Please enter both User ID / Phone number and your password.", "danger")
            return render_template("login.html")

        try:
            user = UserRepo.authenticate(identifier, password)
            if user:
                # Successful sign in: clear failed attempts and regenerate session
                session.clear()
                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                session["role"] = user["role"]

                # Resolve associated profile IDs for Cricketers and Trainers
                if user["role"] == "Cricketer":
                    cricketer = CricketerRepo.get_by_user_id(user["user_id"])
                    if cricketer:
                        session["cricketer_id"] = cricketer["cricketer_id"]
                elif user["role"] == "Trainer":
                    trainer = TrainerRepo.get_by_user_id(user["user_id"])
                    if trainer:
                        session["trainer_id"] = trainer["trainer_id"]

                flash(f"Welcome back, {user['name']}! Signed in as {user['role']}.", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                session["failed_login_attempts"] = failed_count + 1
                flash("Invalid credentials. Please verify your User ID or Phone and password.", "danger")
        except Exception as e:
            logger.error(f"Database error during authentication: {e}")
            flash("Unable to reach the database for authentication. Please try again later.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Safely terminates user session."""
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("landing"))


# =====================================================================
# ROLE-SPECIFIC DASHBOARD ROUTE
# =====================================================================
@app.route("/dashboard")
@login_required
def dashboard():
    """
    Role-tailored academy dashboard:
    Dispatches role-specific Oracle aggregations and operational tables:
    - Super Admin: Academy-wide financials, user totals, quick admin actions.
    - System User: Operational ground overview, logistics, pending items.
    - Trainer: Assigned sessions, coached trainees, attendance shortcuts.
    - Cricketer: Personal attendance %, scheduled sessions, dues, gear history.
    """
    role = session.get("role")
    health = check_db_health()

    if role == "Trainer":
        tid = session.get("trainer_id")
        if not tid and session.get("user_id"):
            trainer = TrainerRepo.get_by_user_id(session.get("user_id"))
            if trainer:
                tid = trainer["trainer_id"]
                session["trainer_id"] = tid

        trainer_data = DashboardRepo.get_trainer_metrics(tid) if tid else {
            "counts": {"total_sessions": 0, "upcoming_sessions": 0, "total_trainees": 0, "total_attendances": 0},
            "my_sessions": [],
            "trainees": []
        }
        return render_template(
            "dashboard.html",
            role=role,
            trainer_data=trainer_data,
            health=health
        )

    elif role == "Cricketer":
        cid = session.get("cricketer_id")
        if not cid and session.get("user_id"):
            cricketer = CricketerRepo.get_by_user_id(session.get("user_id"))
            if cricketer:
                cid = cricketer["cricketer_id"]
                session["cricketer_id"] = cid

        cricketer_data = DashboardRepo.get_cricketer_metrics(cid) if cid else {
            "attendance_pct": 0.0,
            "counts": {"total_applications": 0, "approved_programs": 0, "upcoming_sessions": 0, "active_gear_count": 0, "pending_dues": 0},
            "my_applications": [],
            "my_sessions": [],
            "my_gear": [],
            "my_payments": []
        }
        return render_template(
            "dashboard.html",
            role=role,
            cricketer_data=cricketer_data,
            health=health
        )

    else:
        # Super Admin, System User, or other authenticated staff
        metrics = DashboardRepo.get_metrics() or {}
        if not metrics.get("counts"):
            metrics["counts"] = {}
        if not metrics.get("recent_sessions"):
            metrics["recent_sessions"] = []
        if not metrics.get("pending_payments"):
            metrics["pending_payments"] = []
        return render_template(
            "dashboard.html",
            role=role,
            metrics=metrics,
            health=health
        )


# =====================================================================
# COURSEWORK ADVANCED SQL REPORTS ROUTE (05_advanced_queries.sql)
# =====================================================================
@app.route("/reports")
@login_required
def reports():
    """
    Demonstrates the TWO required coursework advanced SQL queries:
    1. Multi-Table Attendance Roster (5-Table JOIN with Session, Cricketer, Trainer, Venue)
    2. Program Popularity & Enrollment Metrics (GROUP BY, Aggregates, Approval Rates)
    Executes live parameterized queries against Oracle 21c and renders responsive tables.
    """
    try:
        roster_data = ReportRepo.get_advanced_attendance_roster()
    except Exception as e:
        logger.error(f"Error fetching Advanced Query 1 (Attendance Roster): {e}")
        roster_data = []
        flash(f"Error loading Attendance Roster report: {str(e)}", "danger")

    try:
        program_metrics = ReportRepo.get_advanced_program_popularity_report()
    except Exception as e:
        logger.error(f"Error fetching Advanced Query 2 (Program Popularity): {e}")
        program_metrics = []
        flash(f"Error loading Program Popularity report: {str(e)}", "danger")

    return render_template(
        "reports.html",
        roster=roster_data,
        program_metrics=program_metrics
    )


# =====================================================================
# 1. USER MANAGEMENT ROUTES ("USER") - SUPER ADMIN ONLY
# =====================================================================
@app.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "create":
                name = request.form.get("name")
                password = request.form.get("password")
                role = request.form.get("role")
                phone = request.form.get("phone")
                address = request.form.get("address")
                UserRepo.create(name, password, role, phone, address)
                flash(f"User '{name}' created successfully with role {role}.", "success")

            elif action == "update":
                uid = request.form.get("user_id")
                name = request.form.get("name")
                role = request.form.get("role")
                phone = request.form.get("phone")
                address = request.form.get("address")
                pwd = request.form.get("password") or None
                UserRepo.update(uid, name, role, phone, address, pwd)
                flash("User profile updated successfully.", "success")

            elif action == "delete":
                uid = request.form.get("user_id")
                if int(uid) == session.get("user_id"):
                    flash("You cannot delete your own logged-in account.", "warning")
                else:
                    UserRepo.delete(uid)
                    flash("User account deleted successfully.", "success")
        except Exception as e:
            logger.error(f"Error in user management: {e}")
            flash(f"Error performing user action: {str(e)}", "danger")

        return redirect(url_for("users"))

    search = request.args.get("search")
    role_filter = request.args.get("role")
    try:
        user_list = UserRepo.list_all(role=role_filter, search=search)
    except Exception as e:
        logger.error(f"Database error fetching users: {e}")
        flash(f"Database error: {str(e)}. Please verify your Oracle credentials in .env.", "danger")
        user_list = []
    return render_template("users.html", users=user_list, search=search, role_filter=role_filter)


# =====================================================================
# 2. CRICKETER MANAGEMENT ROUTES (CRICKETER)
# =====================================================================
@app.route("/cricketers", methods=["GET", "POST"])
@login_required
def cricketers():
    current_role = session.get("role")
    current_cid = session.get("cricketer_id")

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "create":
                # Only Staff or Admin can create cricketer profiles here
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized to create player profiles directly.", "danger")
                    return redirect(url_for("cricketers"))

                name = request.form.get("name")
                password = request.form.get("password") or "password123"
                phone = request.form.get("phone")
                address = request.form.get("address")
                dob = request.form.get("dob")
                gender = request.form.get("gender")
                batting_style = request.form.get("batting_style")
                bowling_style = request.form.get("bowling_style")
                exp = request.form.get("experience", 0)
                CricketerRepo.create(name, password, phone, address, dob, gender, batting_style, bowling_style, exp)
                flash(f"Cricketer '{name}' registered successfully.", "success")

            elif action == "update":
                cid = int(request.form.get("cricketer_id"))
                # Cricketers can only update their own profile; Staff/Admin can update any
                if current_role == "Cricketer" and cid != current_cid:
                    flash("Unauthorized: You may only modify your own cricketer profile.", "danger")
                    return redirect(url_for("cricketers"))

                name = request.form.get("name")
                phone = request.form.get("phone")
                address = request.form.get("address")
                dob = request.form.get("dob")
                gender = request.form.get("gender")
                batting_style = request.form.get("batting_style")
                bowling_style = request.form.get("bowling_style")
                exp = request.form.get("experience", 0)
                CricketerRepo.update(cid, name, phone, address, dob, gender, batting_style, bowling_style, exp)
                flash("Cricketer details updated successfully.", "success")

            elif action == "delete":
                # Only Super Admin can delete player records
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin may delete cricketer records.", "danger")
                    return redirect(url_for("cricketers"))

                cid = request.form.get("cricketer_id")
                CricketerRepo.delete(cid)
                flash("Cricketer record deleted.", "success")
        except Exception as e:
            logger.error(f"Error managing cricketer: {e}")
            flash(f"Error managing cricketer: {str(e)}", "danger")

        return redirect(url_for("cricketers"))

    search = request.args.get("search")
    try:
        if current_role == "Cricketer":
            # Cricketer only sees their own profile
            cricketer_item = CricketerRepo.get_by_id(current_cid) if current_cid else None
            cricketer_list = [cricketer_item] if cricketer_item else []
        else:
            cricketer_list = CricketerRepo.list_all(search=search)
    except Exception as e:
        logger.error(f"Database error listing cricketers: {e}")
        flash(f"Database error: {str(e)}. Please verify Oracle connection.", "danger")
        cricketer_list = []

    return render_template("cricketers.html", cricketers=cricketer_list, search=search)


# =====================================================================
# 3. TRAINER MANAGEMENT ROUTES (TRAINER)
# =====================================================================
@app.route("/trainers", methods=["GET", "POST"])
@login_required
def trainers():
    current_role = session.get("role")

    if request.method == "POST":
        action = request.form.get("action")
        # Only Super Admin can create, modify, or delete trainers
        if current_role != "Super Admin":
            flash("Unauthorized: Only Super Admin can modify coach and trainer profiles.", "danger")
            return redirect(url_for("trainers"))

        try:
            if action == "create":
                name = request.form.get("name")
                password = request.form.get("password") or "password123"
                phone = request.form.get("phone")
                address = request.form.get("address")
                specialization = request.form.get("specialization")
                exp = request.form.get("experience", 0)
                qualification = request.form.get("qualification")
                salary = request.form.get("salary", 0)
                TrainerRepo.create(name, password, phone, address, specialization, exp, qualification, salary)
                flash(f"Trainer '{name}' enrolled successfully.", "success")

            elif action == "update":
                tid = request.form.get("trainer_id")
                name = request.form.get("name")
                phone = request.form.get("phone")
                address = request.form.get("address")
                specialization = request.form.get("specialization")
                exp = request.form.get("experience", 0)
                qualification = request.form.get("qualification")
                salary = request.form.get("salary", 0)
                TrainerRepo.update(tid, name, phone, address, specialization, exp, qualification, salary)
                flash("Trainer profile updated.", "success")

            elif action == "delete":
                tid = request.form.get("trainer_id")
                TrainerRepo.delete(tid)
                flash("Trainer record removed.", "success")
        except Exception as e:
            logger.error(f"Error managing trainer: {e}")
            flash(f"Error updating trainer: {str(e)}", "danger")

        return redirect(url_for("trainers"))

    search = request.args.get("search")
    try:
        trainer_list = TrainerRepo.list_all(search=search)
    except Exception as e:
        logger.error(f"Database error listing trainers: {e}")
        flash(f"Database error: {str(e)}", "danger")
        trainer_list = []
    return render_template("trainers.html", trainers=trainer_list, search=search)


# =====================================================================
# 4. CRICKET PROGRAMS (CRICKET_PROGRAM)
# =====================================================================
@app.route("/programs", methods=["GET", "POST"])
@login_required
def programs():
    current_role = session.get("role")

    if request.method == "POST":
        action = request.form.get("action")
        # Mutating programs requires Staff or Admin
        if current_role not in ["Super Admin", "System User"]:
            flash("Unauthorized: Only administrative staff may modify training curriculum.", "danger")
            return redirect(url_for("programs"))

        try:
            if action == "create":
                pname = request.form.get("program_name")
                dur = request.form.get("duration")
                ProgramRepo.create(pname, dur)
                flash(f"Program '{pname}' created.", "success")
            elif action == "update":
                pid = request.form.get("program_id")
                pname = request.form.get("program_name")
                dur = request.form.get("duration")
                ProgramRepo.update(pid, pname, dur)
                flash("Program updated.", "success")
            elif action == "delete":
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin may delete cricket programs.", "danger")
                    return redirect(url_for("programs"))
                pid = request.form.get("program_id")
                ProgramRepo.delete(pid)
                flash("Program removed.", "success")
        except Exception as e:
            logger.error(f"Error managing program: {e}")
            flash(f"Error managing program: {str(e)}", "danger")

        return redirect(url_for("programs"))

    search = request.args.get("search")
    try:
        program_list = ProgramRepo.list_all(search=search)
    except Exception as e:
        logger.error(f"Database error listing programs: {e}")
        flash(f"Database error: {str(e)}", "danger")
        program_list = []
    return render_template("programs.html", programs=program_list, search=search)


# =====================================================================
# 5. VENUES (VENUE)
# =====================================================================
@app.route("/venues", methods=["GET", "POST"])
@login_required
def venues():
    current_role = session.get("role")

    if request.method == "POST":
        action = request.form.get("action")
        # Mutating venues requires Staff or Admin
        if current_role not in ["Super Admin", "System User"]:
            flash("Unauthorized: Only academy staff may manage training venues.", "danger")
            return redirect(url_for("venues"))

        try:
            if action == "create":
                vname = request.form.get("venu_name")
                loc = request.form.get("location")
                cap = request.form.get("capacity", 50)
                avail = request.form.get("availability", "Available")
                VenueRepo.create(vname, loc, cap, avail)
                flash(f"Venue '{vname}' registered.", "success")
            elif action == "update":
                vid = request.form.get("venu_id")
                vname = request.form.get("venu_name")
                loc = request.form.get("location")
                cap = request.form.get("capacity")
                avail = request.form.get("availability")
                VenueRepo.update(vid, vname, loc, cap, avail)
                flash("Venue updated.", "success")
            elif action == "delete":
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin may remove academy venues.", "danger")
                    return redirect(url_for("venues"))
                vid = request.form.get("venu_id")
                VenueRepo.delete(vid)
                flash("Venue removed.", "success")
        except Exception as e:
            logger.error(f"Error managing venue: {e}")
            flash(f"Error managing venue: {str(e)}", "danger")

        return redirect(url_for("venues"))

    search = request.args.get("search")
    try:
        venue_list = VenueRepo.list_all(search=search)
    except Exception as e:
        logger.error(f"Database error listing venues: {e}")
        flash(f"Database error: {str(e)}", "danger")
        venue_list = []
    return render_template("venues.html", venues=venue_list, search=search)


# =====================================================================
# 6. TRAINING SESSIONS (TRAINING_SESSION)
# =====================================================================
@app.route("/sessions", methods=["GET", "POST"])
@login_required
def sessions():
    current_role = session.get("role")
    trainer_id = session.get("trainer_id")
    cricketer_id = session.get("cricketer_id")

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "create":
                # Only Staff or Admin can create training sessions
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized: Only academy staff may schedule new training sessions.", "danger")
                    return redirect(url_for("sessions"))

                sdate = request.form.get("session_date")
                stime = request.form.get("session_time")
                status = request.form.get("status", "Scheduled")
                tid = request.form.get("trainer_id")
                vid = request.form.get("venu_id")
                SessionRepo.create(sdate, stime, status, tid, vid)
                flash("Training session scheduled successfully.", "success")

            elif action == "update":
                sid = int(request.form.get("session_id"))
                existing_session = SessionRepo.get_by_id(sid)
                if not existing_session:
                    flash("Session not found.", "danger")
                    return redirect(url_for("sessions"))

                # Trainers may only update status of their OWN assigned sessions
                if current_role == "Trainer":
                    if existing_session.get("trainer_id") != trainer_id:
                        flash("Unauthorized: You may only update sessions assigned to you.", "danger")
                        return redirect(url_for("sessions"))
                    # Preserve date/time/trainer/venue, update status only
                    new_status = request.form.get("status", existing_session["status"])
                    SessionRepo.update(
                        sid,
                        existing_session["session_date"],
                        existing_session["session_time"],
                        new_status,
                        existing_session["trainer_id"],
                        existing_session["venu_id"]
                    )
                    flash("Session status updated.", "success")
                elif current_role in ["Super Admin", "System User"]:
                    sdate = request.form.get("session_date")
                    stime = request.form.get("session_time")
                    status = request.form.get("status")
                    tid = request.form.get("trainer_id")
                    vid = request.form.get("venu_id")
                    SessionRepo.update(sid, sdate, stime, status, tid, vid)
                    flash("Session details updated.", "success")
                else:
                    flash("Unauthorized to update sessions.", "danger")

            elif action == "delete":
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized: Only administrative staff may cancel sessions.", "danger")
                    return redirect(url_for("sessions"))
                sid = request.form.get("session_id")
                SessionRepo.delete(sid)
                flash("Session cancelled/deleted.", "success")
        except Exception as e:
            logger.error(f"Error managing session: {e}")
            flash(f"Error managing session: {str(e)}", "danger")

        return redirect(url_for("sessions"))

    status_filter = request.args.get("status")
    search = request.args.get("search")

    try:
        # Data scoping based on role
        if current_role == "Trainer":
            session_list = SessionRepo.list_all(status=status_filter, search=search, trainer_id=trainer_id)
        elif current_role == "Cricketer":
            session_list = SessionRepo.list_all(status=status_filter, search=search, cricketer_id=cricketer_id)
        else:
            session_list = SessionRepo.list_all(status=status_filter, search=search)

        trainer_list = TrainerRepo.list_all()
        venue_list = VenueRepo.list_all()
    except Exception as e:
        logger.error(f"Database error listing sessions: {e}")
        flash(f"Database error: {str(e)}", "danger")
        session_list, trainer_list, venue_list = [], [], []

    return render_template(
        "sessions.html",
        sessions=session_list,
        trainers=trainer_list,
        venues=venue_list,
        status_filter=status_filter,
        search=search
    )


# =====================================================================
# 7. EQUIPMENT INVENTORY (EQUIPMENT)
# =====================================================================
@app.route("/equipment", methods=["GET", "POST"])
@login_required
def equipment():
    current_role = session.get("role")

    if request.method == "POST":
        action = request.form.get("action")
        # Equipment stock changes require Staff or Admin
        if current_role not in ["Super Admin", "System User"]:
            flash("Unauthorized: Only academy staff may manage equipment inventory.", "danger")
            return redirect(url_for("equipment"))

        try:
            if action == "create":
                ename = request.form.get("equipment_name")
                etype = request.form.get("equipment_type")
                tot = request.form.get("total_quantity", 0)
                qty = request.form.get("quantity", tot)
                avail = request.form.get("availability", "Available")
                EquipmentRepo.create(ename, etype, tot, avail, qty)
                flash(f"Equipment '{ename}' cataloged.", "success")
            elif action == "update":
                eid = request.form.get("equipment_id")
                ename = request.form.get("equipment_name")
                etype = request.form.get("equipment_type")
                tot = request.form.get("total_quantity")
                qty = request.form.get("quantity")
                avail = request.form.get("availability")
                EquipmentRepo.update(eid, ename, etype, tot, avail, qty)
                flash("Equipment updated.", "success")
            elif action == "delete":
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin may delete inventory records.", "danger")
                    return redirect(url_for("equipment"))
                eid = request.form.get("equipment_id")
                EquipmentRepo.delete(eid)
                flash("Equipment record removed.", "success")
        except Exception as e:
            logger.error(f"Error managing equipment: {e}")
            flash(f"Error updating equipment: {str(e)}", "danger")

        return redirect(url_for("equipment"))

    search = request.args.get("search")
    avail_filter = request.args.get("availability")
    try:
        equip_list = EquipmentRepo.list_all(search=search, availability=avail_filter)
    except Exception as e:
        logger.error(f"Database error listing equipment: {e}")
        flash(f"Database error: {str(e)}", "danger")
        equip_list = []
    return render_template("equipment.html", equipment=equip_list, search=search, avail_filter=avail_filter)


# =====================================================================
# 8. PAYMENTS & FINANCES (PAYMENT)
# =====================================================================
@app.route("/payments", methods=["GET", "POST"])
@login_required
def payments():
    current_role = session.get("role")
    current_cid = session.get("cricketer_id")

    # Trainers have no business in financial routes
    if current_role == "Trainer":
        flash("Access denied: Coaching staff does not manage financial accounts.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action")

        # Cricketers are strictly forbidden from altering fee records
        if current_role == "Cricketer":
            flash("Unauthorized: Players cannot generate or alter payment records.", "danger")
            return redirect(url_for("payments"))

        try:
            if action == "create":
                cid = request.form.get("cricketer_id")
                pid = request.form.get("program_id")
                amt = request.form.get("amount")
                ddate = request.form.get("due_date")
                status = request.form.get("payment_status", "Pending")
                pdate = request.form.get("payment_date") or None
                PaymentRepo.create(cid, pid, amt, ddate, status, pdate)
                flash("Payment invoice created.", "success")

            elif action == "mark_paid":
                cid = request.form.get("cricketer_id")
                pid = request.form.get("program_id")
                ddate = request.form.get("due_date")
                PaymentRepo.update_status(cid, pid, ddate, "Paid")
                flash("Payment marked as PAID successfully.", "success")

            elif action == "delete":
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin may delete billing records.", "danger")
                    return redirect(url_for("payments"))
                cid = request.form.get("cricketer_id")
                pid = request.form.get("program_id")
                ddate = request.form.get("due_date")
                PaymentRepo.delete(cid, pid, ddate)
                flash("Payment record deleted.", "success")
        except Exception as e:
            logger.error(f"Error in payment transaction: {e}")
            flash(f"Error processing payment: {str(e)}", "danger")

        return redirect(url_for("payments"))

    status_filter = request.args.get("status")
    search = request.args.get("search")

    # Cricketer only views their own invoices
    cid_filter = current_cid if current_role == "Cricketer" else None

    try:
        payment_list = PaymentRepo.list_all(status=status_filter, cricketer_id=cid_filter, search=search)
        cricketers_list = CricketerRepo.list_all() if current_role in ["Super Admin", "System User"] else []
        program_list = ProgramRepo.list_all()
    except Exception as e:
        logger.error(f"Database error listing payments: {e}")
        flash(f"Database error: {str(e)}", "danger")
        payment_list, cricketers_list, program_list = [], [], []

    return render_template(
        "payments.html",
        payments=payment_list,
        cricketers=cricketers_list,
        programs=program_list,
        status_filter=status_filter,
        search=search
    )


# =====================================================================
# 9. PROGRAM APPLICATIONS (APPLIED_TO)
# =====================================================================
@app.route("/applications", methods=["GET", "POST"])
@login_required
def applications():
    current_role = session.get("role")
    current_cid = session.get("cricketer_id")

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "apply":
                pid = request.form.get("program_id")
                if current_role == "Cricketer":
                    cid = current_cid
                else:
                    cid = request.form.get("cricketer_id")

                if not cid or not pid:
                    flash("Both Cricketer and Program selection are required.", "danger")
                    return redirect(url_for("applications"))

                ApplicationRepo.create(cid, pid, "Pending")
                flash("Program enrollment application submitted successfully.", "success")

            elif action == "update_status":
                # Only Staff or Admin can approve or reject applications
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized: Only academy staff can review and approve applications.", "danger")
                    return redirect(url_for("applications"))

                cid = request.form.get("cricketer_id")
                pid = request.form.get("program_id")
                new_stat = request.form.get("applied_status")
                ApplicationRepo.update_status(cid, pid, new_stat)
                flash(f"Application marked as '{new_stat}'.", "success")

            elif action == "delete":
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized: Only academy staff may remove applications.", "danger")
                    return redirect(url_for("applications"))

                cid = request.form.get("cricketer_id")
                pid = request.form.get("program_id")
                ApplicationRepo.delete(cid, pid)
                flash("Application removed.", "success")
        except Exception as e:
            logger.error(f"Error handling application: {e}")
            flash(f"Error with application: {str(e)}", "danger")

        return redirect(url_for("applications"))

    status_filter = request.args.get("status")
    search = request.args.get("search")

    cid_filter = current_cid if current_role == "Cricketer" else None

    try:
        app_list = ApplicationRepo.list_all(status=status_filter, cricketer_id=cid_filter, search=search)
        cricketers_list = CricketerRepo.list_all() if current_role in ["Super Admin", "System User"] else []
        program_list = ProgramRepo.list_all()
    except Exception as e:
        logger.error(f"Database error listing applications: {e}")
        flash(f"Database error: {str(e)}", "danger")
        app_list, cricketers_list, program_list = [], [], []

    return render_template(
        "applications.html",
        applications=app_list,
        cricketers=cricketers_list,
        programs=program_list,
        status_filter=status_filter,
        search=search
    )


# =====================================================================
# 10. EQUIPMENT ISSUES & RETURNS (EQUIPMENT_ISSUED)
# =====================================================================
@app.route("/equipment-issues", methods=["GET", "POST"])
@login_required
def equipment_issues():
    current_role = session.get("role")
    current_cid = session.get("cricketer_id")

    if request.method == "POST":
        action = request.form.get("action")

        # Issuing and checking in gear is restricted to academy staff
        if current_role not in ["Super Admin", "System User"]:
            flash("Unauthorized: Only equipment room staff can issue or process gear returns.", "danger")
            return redirect(url_for("equipment_issues"))

        try:
            if action == "issue":
                cid = request.form.get("cricketer_id")
                eid = request.form.get("equipment_id")
                qty = request.form.get("quantity", 1)
                res = EquipmentIssueRepo.issue_gear(cid, eid, qty)
                flash(res["message"], "success" if res["status"] == "SUCCESS" else "danger")

            elif action == "return":
                cid = request.form.get("cricketer_id")
                eid = request.form.get("equipment_id")
                idate = request.form.get("issue_date")
                EquipmentIssueRepo.return_gear(cid, eid, idate)
                flash("Gear marked as RETURNED. Inventory stock restored.", "success")

            elif action == "delete":
                if current_role != "Super Admin":
                    flash("Unauthorized: Only Super Admin can delete gear checkout logs.", "danger")
                    return redirect(url_for("equipment_issues"))
                cid = request.form.get("cricketer_id")
                eid = request.form.get("equipment_id")
                idate = request.form.get("issue_date")
                EquipmentIssueRepo.delete(cid, eid, idate)
                flash("Issue log removed.", "success")
        except Exception as e:
            logger.error(f"Error processing equipment issue: {e}")
            flash(f"Error processing equipment checkout: {str(e)}", "danger")

        return redirect(url_for("equipment_issues"))

    status_filter = request.args.get("status")
    search = request.args.get("search")

    cid_filter = current_cid if current_role == "Cricketer" else None

    try:
        issue_list = EquipmentIssueRepo.list_all(status=status_filter, cricketer_id=cid_filter, search=search)
        cricketers_list = CricketerRepo.list_all() if current_role in ["Super Admin", "System User"] else []
        equip_list = EquipmentRepo.list_all(availability="Available")
    except Exception as e:
        logger.error(f"Database error listing equipment issues: {e}")
        flash(f"Database error: {str(e)}", "danger")
        issue_list, cricketers_list, equip_list = [], [], []

    return render_template(
        "equipment_issues.html",
        issues=issue_list,
        cricketers=cricketers_list,
        equipment=equip_list,
        status_filter=status_filter,
        search=search
    )


# =====================================================================
# 11. PARTICIPATION & ATTENDANCE (PARTICIPATE_IN)
# =====================================================================
@app.route("/participation", methods=["GET", "POST"])
@login_required
def participation():
    current_role = session.get("role")
    current_cid = session.get("cricketer_id")
    current_tid = session.get("trainer_id")

    if request.method == "POST":
        action = request.form.get("action")

        # Cricketers are strictly forbidden from marking attendance
        if current_role == "Cricketer":
            flash("Unauthorized: Players may not record or modify attendance.", "danger")
            return redirect(url_for("participation"))

        try:
            sid = int(request.form.get("session_id"))
            session_rec = SessionRepo.get_by_id(sid)

            # Trainers can only record/update attendance for their OWN assigned sessions
            if current_role == "Trainer":
                if not session_rec or session_rec.get("trainer_id") != current_tid:
                    flash("Unauthorized: You may only record attendance for sessions assigned to you.", "danger")
                    return redirect(url_for("participation"))

            if action == "record":
                cid = request.form.get("cricketer_id")
                ptime = request.form.get("participation_time", "2 Hours")
                att = request.form.get("attendance", "Present")
                ParticipationRepo.record(cid, sid, ptime, att)
                flash("Attendance recorded successfully.", "success")

            elif action == "update":
                cid = request.form.get("cricketer_id")
                ptime = request.form.get("participation_time")
                att = request.form.get("attendance")
                ParticipationRepo.update(cid, sid, ptime, att)
                flash("Attendance updated successfully.", "success")

            elif action == "delete":
                if current_role not in ["Super Admin", "System User"]:
                    flash("Unauthorized: Only academy administrators may remove attendance rows.", "danger")
                    return redirect(url_for("participation"))
                cid = request.form.get("cricketer_id")
                ParticipationRepo.delete(cid, sid)
                flash("Attendance entry removed.", "success")
        except Exception as e:
            logger.error(f"Error handling participation: {e}")
            flash(f"Error recording attendance: {str(e)}", "danger")

        return redirect(url_for("participation"))

    sid_filter = request.args.get("session_id")
    search = request.args.get("search")

    cid_filter = current_cid if current_role == "Cricketer" else None
    tid_filter = current_tid if current_role == "Trainer" else None

    attendance_pct = None
    if current_role == "Cricketer" and current_cid:
        try:
            attendance_pct = ParticipationRepo.get_attendance_percentage(current_cid)
        except Exception:
            attendance_pct = None

    try:
        part_list = ParticipationRepo.list_all(
            session_id=sid_filter,
            cricketer_id=cid_filter,
            trainer_id=tid_filter,
            search=search
        )
        cricketers_list = CricketerRepo.list_all() if current_role != "Cricketer" else []
        session_list = SessionRepo.list_all(trainer_id=tid_filter)
    except Exception as e:
        logger.error(f"Database error listing attendance: {e}")
        flash(f"Database error: {str(e)}", "danger")
        part_list, cricketers_list, session_list = [], [], []

    return render_template(
        "participation.html",
        participations=part_list,
        cricketers=cricketers_list,
        sessions=session_list,
        sid_filter=sid_filter,
        search=search,
        attendance_pct=attendance_pct
    )


# =====================================================================
# DIAGNOSTICS & SYSTEM HEALTH
# =====================================================================
@app.route("/system-health")
@login_required
def system_health():
    """Provides internal connectivity and table count diagnostics."""
    return jsonify(check_db_health())


# =====================================================================
# ERROR HANDLERS
# =====================================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template("base.html", error_title="403 - Forbidden", error_msg="You do not have permission to access this resource."), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", error_title="404 - Page Not Found", error_msg="The requested page does not exist."), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 Internal Error: {e}")
    return render_template("base.html", error_title="500 - Server Error", error_msg="An unexpected internal error occurred. Please contact the academy administrator."), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
