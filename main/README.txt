================================================================================
CRICKETHUB - CRICKET TRAINING & ACADEMY MANAGEMENT SYSTEM
Comprehensive Windows Setup, Database Deployment & Operational Guide
================================================================================

1. PROJECT PURPOSE & TECHNOLOGY STACK
--------------------------------------------------------------------------------
Crickethub is an enterprise-grade Cricket Training Management System built to
centralize and automate operations for cricket coaching academies. It manages
players, certified coaches, training curriculums, pitch allocations, session
schedules, academy gear inventory, player fees, and training attendance.

Technology Stack:
- Backend: Python 3.10+ with Flask 3.x
- Database: Oracle Database 19c / 21c XE (Express Edition) / Enterprise
- Oracle Driver: python-oracledb 2.x (Thin Mode - pure Python, no client binaries needed)
- Database Logic: SQL DDL/DML, Constraints, Views, PL/SQL Function, Stored Procedure,
  Explicit Cursor, Database Trigger, and Coursework Advanced Analytical SQL
- Frontend: HTML5, Accessible CSS3 (custom cricket design system with hero photography,
  serif typography, glass cards, and pill buttons), Vanilla JavaScript


2. COMPLETE FOLDER & FILE STRUCTURE
--------------------------------------------------------------------------------
CricketHub/
└── main/
    ├── app.py                         -> Flask web server, HTTP routes, role authorization
    ├── db.py                          -> Oracle connection pool, RowDict mapping & helpers
    ├── repositories.py                -> Parameterized SQL queries for all 11 tables
    ├── requirements.txt               -> Python dependencies (Flask, oracledb, python-dotenv)
    ├── README.txt                     -> This comprehensive guide and checklist
    ├── DATABASE_WORKFLOW.md           -> Detailed table, repository & SQL workflow map
    ├── DEMO_ACCOUNTS.md               -> Confidential classroom demonstration accounts guide
    ├── IMPLEMENTATION_REPORT.md       -> Complete implementation, bug fix & test report
    ├── .env                           -> Local environment credentials (DO NOT COMMIT)
    ├── .env.example                   -> Environment variable template
    ├── .gitignore                     -> Excludes venv, .env, and caches from git
    ├── database/
    │   ├── 01_authentication_user_management.sql  -> "USER", CRICKETER, TRAINER
    │   ├── 02_training_management.sql             -> CRICKET_PROGRAM, VENUE, TRAINING_SESSION
    │   ├── 03_finance_equipment.sql               -> EQUIPMENT, PAYMENT
    │   ├── 04_attendance_participation.sql        -> APPLIED_TO, EQUIPMENT_ISSUED, PARTICIPATE_IN
    │   ├── 05_advanced_queries.sql                -> 2 Coursework Advanced Queries (Multi-Table JOIN & GROUP BY)
    │   ├── 06_function.sql                        -> calculate_attendance_pct PL/SQL Function
    │   ├── 07_procedure.sql                       -> issue_equipment PL/SQL Stored Procedure
    │   ├── 08_cursor.sql                          -> list_pending_payments Explicit Cursor
    │   ├── 09_trigger.sql                         -> trg_maintain_equipment_inventory Stock Trigger
    │   ├── 10_sample_data.sql                     -> Seed data with Werkzeug 3.1 scrypt hashes
    │   └── optional_reference_queries.sql         -> Preserved candidate queries 3-8 (reference only)
    ├── templates/
    │   ├── base.html                  -> Master layout with role-aware navigation
    │   ├── landing.html               -> Cinematic public landing page with hero banner & stats
    │   ├── register.html              -> Public Cricketer self-registration page
    │   ├── login.html                 -> Clean sign-in page (no exposed credentials)
    │   ├── dashboard.html             -> 4 Role-specific dashboards (Admin, Staff, Coach, Player)
    │   ├── reports.html               -> Interactive analytical reports demonstrating 2 advanced SQL queries
    │   ├── users.html                 -> User account management ("USER" - Super Admin only)
    │   ├── cricketers.html            -> Player profiles & disciplines (CRICKETER)
    │   ├── trainers.html              -> Head coaches, credentials & salaries (TRAINER)
    │   ├── programs.html              -> Training curriculums (CRICKET_PROGRAM)
    │   ├── venues.html                -> Stadiums & turf nets (VENUE)
    │   ├── sessions.html              -> Training schedules (TRAINING_SESSION)
    │   ├── equipment.html             -> Inventory & stock tracking (EQUIPMENT)
    │   ├── payments.html              -> Player fee invoices & dues (PAYMENT)
    │   ├── applications.html          -> Program enrollments & review (APPLIED_TO)
    │   ├── equipment_issues.html      -> Checkout & return of gear (EQUIPMENT_ISSUED)
    │   └── participation.html         -> Player attendance & % rating (PARTICIPATE_IN)
    └── static/
        ├── css/style.css              -> Deep forest green palette, serif typography, pill styling
        ├── images/cricket_hero.jpg    -> Cinematic cricket stadium hero photography
        └── js/main.js                 -> Modals, form population & confirmation dialogs


3. ROLE-BASED ACCESS CONTROL & PERMISSION MATRIX
--------------------------------------------------------------------------------
The application defines four distinct roles based strictly on the project ER diagram:

| Module / Operation | Super Admin | System User (Staff) | Trainer (Coach) | Cricketer (Player) |
| :--- | :---: | :---: | :---: | :---: |
| **Public Landing Page** (`/`) | Full Access | Full Access | Full Access | Full Access |
| **Self-Registration** (`/register`) | Public | Public | Public | Public |
| **Personal Dashboard** (`/dashboard`) | Academy Totals | Operations View | Assigned Sessions | My Attendance & Dues |
| **User Account Management** (`/users`) | Full CRUD | Forbidden (403) | Forbidden (403) | Forbidden (403) |
| **Player Profiles** (`/cricketers`) | Full CRUD | View & Enroll | View Trainees | View/Edit Own Profile |
| **Coach Management** (`/trainers`) | Full CRUD | View Only | View Directory | View Directory |
| **Training Programs** (`/programs`) | Full CRUD | Create / Update | View Catalog | View & Apply |
| **Venues & Grounds** (`/venues`) | Full CRUD | Create / Update | View Venues | View Venues |
| **Training Sessions** (`/sessions`) | Full CRUD | Full CRUD | Assigned Only | Attending Only |
| **Equipment Inventory** (`/equipment`) | Full CRUD | Full CRUD | View Stock | View Catalog |
| **Fee Invoices** (`/payments`) | Full CRUD | Invoice & Receipt | Forbidden (403) | View Own Dues Only |
| **Applications** (`/applications`) | Review/Approve | Review/Approve | View Only | Apply for Self |
| **Gear Checkouts** (`/equipment-issues`)| Issue / Return | Issue / Return | Forbidden (403) | View Own Gear Only |
| **Attendance Records** (`/participation`)| Full CRUD | Full CRUD | Assigned Sessions | View Own Log Only |
| **Analytical Reports** (`/reports`) | View All | View All | View All | View All |


4. PREREQUISITES & ENVIRONMENT CONFIGURATION (.env)
--------------------------------------------------------------------------------
1. Python 3.10+ (64-bit).
2. Oracle Database 21c XE or Enterprise running locally on port 1521.
3. Configure your local `.env` file in `d:\study\DBMS\project\PROJECT_MAIN\CricketHub\main\.env`:

```env
# Flask Secret Key (REQUIRED - application will refuse to start without a non-empty key)
# Generate a fresh key via: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=e0f01433217d67c11f13206190ef61ee30a768bfbaa93014b63da5de57efb702

# Oracle Database Credentials
ORACLE_USER=CRICKETHUB_USER
ORACLE_PASSWORD=Crickethub_DB_2026!
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1

# Application Server Port
PORT=5000
```


5. SAFE SQL SCRIPT EXECUTION ORDER
--------------------------------------------------------------------------------
Run the following scripts in SQL*Plus or Oracle SQL Developer in order:

    CONNECT CRICKETHUB_USER/Crickethub_DB_2026!@localhost:1521/XEPDB1

    @01_authentication_user_management.sql
    @02_training_management.sql
    @03_finance_equipment.sql
    @04_attendance_participation.sql
    @06_function.sql
    @07_procedure.sql
    @08_cursor.sql
    @09_trigger.sql
    @10_sample_data.sql

Verify the 11 schema tables exist:
    SELECT table_name FROM user_tables ORDER BY table_name;

*Note*: Table `"USER"` is created with double quotes as `USER` is an Oracle reserved word.


6. STARTING THE APPLICATION
--------------------------------------------------------------------------------
From PowerShell or terminal in `D:\study\DBMS\project\PROJECT_MAIN\CricketHub\main`:

    # Activate virtual environment
    .\venv\Scripts\Activate.ps1

    # Run the server
    python app.py

Open your web browser and navigate to:
    http://localhost:5000/


7. CLASSROOM DEMONSTRATION & EVALUATION STEPS
--------------------------------------------------------------------------------
1. Open http://localhost:5000/ to experience the public cricket landing page.
2. Click "Join Academy" (`/register`) to demonstrate public player self-registration.
3. Refer to `DEMO_ACCOUNTS.md` for classroom evaluation credentials:
   - Super Admin : User ID: 1 | Password: password123
   - System User : User ID: 2 | Password: password123
   - Trainer     : User ID: 3 | Password: password123
   - Cricketer   : User ID: 6 | Password: password123
4. Log in as each role to inspect their unique, tailored dashboard experience.
5. Visit `/reports` to demonstrate the TWO coursework advanced SQL queries:
   - Query 1: Multi-Table Attendance Roster (5-Table Relational JOIN)
   - Query 2: Program Popularity & Acceptance Metrics (GROUP BY, SUM CASE, NULLIF)
   Click "View SQL Query" to display and explain the exact SQL query text for viva.


8. TROUBLESHOOTING GUIDE
--------------------------------------------------------------------------------
1. ORA-01745: invalid host/bind variable name:
   - Fixed: Named bind variables in `repositories.py` now use safe prefixes (`:p_user_id`).
   
2. ORA-12541: TNS:no listener / ORA-12514: listener does not know service:
   - Ensure 'OracleServiceXE' and 'OracleOraDB21Home1TNSListener' services are Running in Windows Services (services.msc).
   - Ensure ORACLE_SERVICE=XEPDB1 matches your Pluggable Database name.

3. Secret Key Error on Startup:
   - Ensure `SECRET_KEY` is present and non-empty in `.env`.
   - Generate a valid secret: `python -c "import secrets; print(secrets.token_hex(32))"`.

4. PL/SQL Object Fallbacks:
   - If `calculate_attendance_pct` or `issue_equipment` are not compiled, the Python repository automatically executes equivalent pure SQL queries so the website continues functioning without crash.
================================================================================
