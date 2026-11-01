# Crickethub — Antigravity Overhaul & Redesign Implementation Report

**Project:** Crickethub — MCA Cricket Training & Academy Management System  
**Stack:** Python 3.10 Flask + Oracle Database 21c Express Edition (XE) (Thin Mode)  
**Date:** November 2026  

---

## 1. Critical Bugs Fixed

1. **`ORA-01745: invalid host/bind variable name` Resolved**:
   - **Root Cause**: `repositories.py` utilized `:uid` in SQL parameter dictionaries. In Oracle SQL, `UID` is a reserved system function that returns the integer user ID of the current database session (`SELECT UID FROM DUAL`). Using `:uid` as a named bind variable triggers `ORA-01745`.
   - **Resolution**: Refactored all bind variables across all repository functions to safe, descriptive prefixed names (`:p_user_id`, `:p_cricketer_id`, `:p_trainer_id`, `:p_session_id`, `:p_equipment_id`, etc.).
   
2. **Insecure Hardcoded Flask Fallback Secret Key Removed**:
   - **Root Cause**: `app.py` previously had `app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "crickethub_production_secret_key_2026")`.
   - **Resolution**: Implemented strict validation on startup. If `SECRET_KEY` is not present in `.env`, Flask raises a `RuntimeError` immediately with instructions to generate a cryptographic key using `secrets.token_hex(32)`.

3. **Public Exposure of Plaintext Demo Credentials on Login Screen**:
   - **Root Cause**: `login.html` prominently displayed demo IDs and passwords in an unsecured public card.
   - **Resolution**: Removed all credential disclosures from `login.html`. Documented pre-seeded accounts in a confidential developer guide (`DEMO_ACCOUNTS.md`).

4. **Missing Public Self-Registration for Players**:
   - **Root Cause**: Previously, cricketers had to be manually created by administrators in backend screens.
   - **Resolution**: Built a dedicated, secure `/register` route and `register.html` template. Player self-registration creates parent `"USER"` and child `CRICKETER` records atomically with unique phone validation and role fixed to `Cricketer`.

5. **Lack of Role-Based Navigation & Data Ownership Security**:
   - **Root Cause**: All roles previously shared identical navigation links and dashboards. Players could view other players' records, and coaching staff could access academy financial books.
   - **Resolution**: Built role-based decorators (`@admin_required`, `@staff_or_admin_required`, `@trainer_or_admin_required`), scoped query filters, and server-side record ownership checks.

6. **SQL Script Query Count Compliance**:
   - **Root Cause**: Coursework requirement specifies exactly two advanced queries, but `05_advanced_queries.sql` contained eight candidates.
   - **Resolution**: Retained exactly two advanced queries in `05_advanced_queries.sql` (Multi-Table Attendance Roster and Program Popularity Aggregation) and connected both directly to `ReportRepo` and `/reports`. Relocated the other six queries to `optional_reference_queries.sql` for reference only.

---

## 2. Features Implemented

1. **Cinematic Cricket Landing Page (`/`)**:
   - High-resolution atmospheric cricket photography hero banner (`static/images/cricket_hero.jpg`).
   - Elegant serif display typography (Playfair Display / Cinzel) with forest-green palette.
   - Live academy metrics strip (enrolled players, coaches, curriculums, venues) pulling from real Oracle aggregates.
   - Training curriculum highlights and responsive navigation.

2. **Public Cricketer Registration (`/register`)**:
   - Responsive multi-section registration form for new players.
   - Collects personal details, contact info, DOB, gender, batting style, bowling style, and experience.
   - Atomic transaction preventing orphaned user/cricketer records.
   - Instant auto-login upon successful registration.

3. **Four Distinct Role-Specific Dashboards (`/dashboard`)**:
   - **Super Admin**: Academy financials, collected vs. outstanding revenue, user accounts, ground slots, pending queues, and administrative action buttons.
   - **System User (Operations Staff)**: Operations-focused view of ground slots, venue availability, pending application queue, and gear checkout actions (no sensitive financial data).
   - **Trainer (Coach)**: Scoped exclusively to assigned training sessions, trainee player directory, and attendance marking shortcuts.
   - **Cricketer (Player)**: Personal attendance % (calculated via PL/SQL function), scheduled sessions, application statuses, active gear checked out, and invoice dues.

4. **Coursework Advanced SQL Analytical Reports (`/reports`)**:
   - Direct web-based demonstration of Query 1 (5-Table Relational JOIN) and Query 2 (GROUP BY with conditional `SUM(CASE ...)` and `NULLIF`).
   - Expandable SQL source viewer allowing students and faculty to inspect and explain the exact query during MCA project viva.
   - Real-time Oracle 21c table rendering with progress bars and status badges.

5. **Server-Side Authorization & Ownership Enforcement**:
   - Cricketers can view and edit only their own profile, applications, sessions, attendance, and gear.
   - Cricketers cannot edit payments, mark dues as paid, or mark attendance.
   - Trainers can only view and update attendance for sessions assigned to them.
   - Trainers cannot access financial routes (`/payments` returns 403 / redirect).
   - Only Super Admin can manage user accounts, reassign roles, or delete players, coaches, programs, or venues.

---

## 3. Files Created and Modified

| File | Status | Description |
| :--- | :--- | :--- |
| `app.py` | **Modified** | Strict `SECRET_KEY` validation, role decorators, `/` landing route, `/register` route, `/reports` route, role-based dashboard dispatching, server-side ownership checks. |
| `repositories.py` | **Modified** | Replaced all `:uid` with `:p_user_id`, added `ReportRepo`, added `CricketerRepo.register_cricketer`, added `TrainerRepo.get_by_user_id`, added `DashboardRepo.get_trainer_metrics` & `get_cricketer_metrics`, added trainer/cricketer scoping filters. |
| `database/05_advanced_queries.sql` | **Modified** | Filtered to contain EXACTLY the two required coursework queries. |
| `database/optional_reference_queries.sql` | **Created** | Preserves queries 3 through 8 for reference only. |
| `database/10_sample_data.sql` | **Modified** | Updated with valid Werkzeug 3.1 scrypt hashes for baseline demo accounts. |
| `templates/base.html` | **Modified** | Role-aware navigation headers, Google Fonts Playfair/Cinzel/Inter, links to `/reports` and `/register`. |
| `templates/landing.html` | **Created** | Public landing page with atmospheric hero photography, live Oracle metrics, curriculum cards, and call-to-actions. |
| `templates/register.html` | **Created** | Public Cricketer self-registration form with validation. |
| `templates/login.html` | **Modified** | Cleaned of plaintext credentials disclosure, added link to `/register`, styled to match theme. |
| `templates/dashboard.html` | **Modified** | Complete overhaul with four dedicated role-specific dashboard views. |
| `templates/reports.html` | **Created** | Coursework analytical reports page demonstrating both advanced SQL queries with expandable source viewers. |
| `static/css/style.css` | **Modified** | Added hero banner styles, serif display typography, pill buttons, glassmorphic elements, role badges, and responsive layouts. |
| `static/images/cricket_hero.jpg` | **Created** | Cinematic cricket stadium photograph for hero banner. |
| `DATABASE_WORKFLOW.md` | **Created** | Comprehensive guide mapping SQL files, request pipeline, CRUD actions, and PL/SQL objects. |
| `DEMO_ACCOUNTS.md` | **Created** | Confidential classroom demonstration guide for faculty evaluation. |
| `IMPLEMENTATION_REPORT.md` | **Created** | Summary of bugs fixed, features implemented, and verification results. |
| `README.txt` | **Modified** | Updated installation, execution order, environment configuration, and role permission matrix. |

---

## 4. Tests Actually Run & Results

1. **Python Syntax & Compilation Check**:
   - Executed `python -m py_compile app.py repositories.py db.py`.
   - **Result**: Zero syntax errors; all modules compiled cleanly.
2. **Oracle Database Connectivity & Route HTTP Verification**:
   - Verified live connection to Oracle Database 21c XE (`localhost:1521/XEPDB1`).
   - Verified that all 11 schema tables (`"USER"`, `CRICKETER`, `TRAINER`, `CRICKET_PROGRAM`, `VENUE`, `TRAINING_SESSION`, `EQUIPMENT`, `PAYMENT`, `APPLIED_TO`, `EQUIPMENT_ISSUED`, `PARTICIPATE_IN`) are present and healthy.
3. **Advanced Queries Execution**:
   - Query 1 (5-Table Attendance Roster) executed successfully against live Oracle instance.
   - Query 2 (Program Popularity GROUP BY) executed successfully against live Oracle instance.

---

## 5. Tests Requiring User's Local Environment / Manual Check

1. **Live Browser Demonstration**:
   - Start the Flask server: `python app.py`.
   - Open `http://localhost:5000/` in a web browser to experience the landing page, register a player, and review role dashboards.
2. **PL/SQL Stored Objects in Oracle Instance**:
   - Verify that `calculate_attendance_pct` (Function) and `issue_equipment` (Procedure) are compiled and valid in the user's Oracle schema. (The Python repository layer includes automated fallback calculations if PL/SQL stored objects are not yet compiled in the database).

