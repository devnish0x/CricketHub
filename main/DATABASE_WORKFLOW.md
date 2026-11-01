# Crickethub — Database Architecture & Workflow Guide

## Overview

**Crickethub** is a high-performance MCA Cricket Training Management System built with **Python 3.10 Flask** and **Oracle Database 21c Express Edition (XE)**. The system enforces relational integrity across 11 tables adhering to the project ER diagram.

---

## 1. Schema File Mapping & Table Creation

The database tables, constraints, sequences/triggers, and business procedures are organized into dedicated modular SQL scripts under the `database/` directory:

| Order | Script File | Purpose & Entities Defined |
| :--- | :--- | :--- |
| **01** | `01_authentication_user_management.sql` | Creates `"USER"` (account credentials, role, contact) and `CRICKETER` (DOB, batting/bowling style, experience). |
| **02** | `02_training_management.sql` | Creates `TRAINER` (coach credentials, specialization, salary), `CRICKET_PROGRAM` (training syllabus, duration), `VENUE` (grounds, net complexes, capacity, availability), and `TRAINING_SESSION` (scheduled slots linking trainer & venue). |
| **03** | `03_finance_equipment.sql` | Creates `PAYMENT` (billing invoices, fee tracking, due dates, statuses) and `EQUIPMENT` (inventory catalog, total quantity, available stock). |
| **04** | `04_attendance_participation.sql` | Creates `APPLIED_TO` (program applications linking player & program), `EQUIPMENT_ISSUED` (gear checkout/return logs), and `PARTICIPATE_IN` (session attendance & participation logs). |
| **05** | `05_advanced_queries.sql` | **Coursework Deliverable**: Contains exactly the two advanced analytical SQL queries demonstrated live on the web application at `/reports`. |
| **06** | `06_function.sql` | Defines PL/SQL stored function `calculate_attendance_pct(p_cricketer_id)` returning player attendance percentage. |
| **07** | `07_procedure.sql` | Defines PL/SQL stored procedure `issue_equipment(...)` validating inventory availability before checkout. |
| **08** | `08_cursor.sql` | Defines PL/SQL explicit cursor procedure `list_pending_payments` auditing overdue fee accounts. |
| **09** | `09_trigger.sql` | Defines database triggers (e.g. `trg_maintain_equipment_inventory`) ensuring stock integrity. |
| **10** | `10_sample_data.sql` | Seeds initial baseline accounts, programs, grounds, sessions, gear, and attendances. Uses secure Werkzeug 3.1 scrypt hashes. |
| **Ref** | `optional_reference_queries.sql` | Preserves candidate queries 3 through 8 for reference only (not part of active coursework deliverable). |

---

## 2. Safe Execution Order (SQL*Plus / Oracle SQL Developer)

When deploying or preparing a fresh Oracle database, run the scripts in the following dependency-verified sequence:

```sql
-- Connect to Oracle PDB (e.g., XEPDB1) as the application schema user
-- Example: CONNECT CRICKETHUB_USER/Crickethub_DB_2026!@localhost:1521/XEPDB1

@01_authentication_user_management.sql
@02_training_management.sql
@03_finance_equipment.sql
@04_attendance_participation.sql
@06_function.sql
@07_procedure.sql
@08_cursor.sql
@09_trigger.sql
@10_sample_data.sql
```

> **Safety Notice:** Do not run destructive drop/reset scripts against a running database. Schema creation and seeding scripts are strictly decoupled from Flask application startup.

---

## 3. End-to-End Request Flow Architecture

Every user action follows this strict pipeline:

```
HTML Form / User Action (Browser)
       ↓  (POST / GET)
Flask Route in app.py
       ↓  (Authentication & Role Authorization Checks)
Server-side Data Validation & Ownership Verification
       ↓
Repository Class in repositories.py
       ↓  (Parameterized Bind Variables :p_name, etc.)
Oracle DB Engine via db.py (python-oracledb Thin Mode)
       ↓  (Commit on Success / Rollback on Exception)
Truthful Flash Message & Updated UI Render
```

---

## 4. Complete Action-to-Repository Mapping

All runtime SQL queries are centralized inside `repositories.py`. Templates and route handlers never execute inline SQL.

### 4.1 Authentication & Registration
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / PLSQL |
| :--- | :--- | :--- | :--- | :--- |
| Player Self-Registration | `POST /register` | Public | `CricketerRepo.register_cricketer` | Atomic `INSERT INTO "USER"` (Role='Cricketer') followed by `INSERT INTO CRICKETER`. Validates unique phone. |
| Account Login | `POST /login` | Public (Throttled) | `UserRepo.authenticate` | `SELECT User_id, Password, Role FROM "USER" WHERE User_id = :p_user_id OR Phone = :p_phone`. Verifies scrypt hash. |
| Session Logout | `GET /logout` | Authenticated | N/A (Session Clear) | Terminate cookie session. |

### 4.2 User Management ("USER")
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| List Users | `GET /users` | Super Admin | `UserRepo.list_all` | `SELECT User_id, Name, Role, Phone, Address FROM "USER"` with optional search and role filtering. |
| Create User | `POST /users` (action=create) | Super Admin | `UserRepo.create` | `INSERT INTO "USER"` with hashed password. |
| Update User Profile | `POST /users` (action=update) | Super Admin | `UserRepo.update` | `UPDATE "USER" SET Name=..., Role=..., Phone=..., Address=...` |
| Delete User | `POST /users` (action=delete) | Super Admin | `UserRepo.delete` | `DELETE FROM "USER" WHERE User_id = :p_user_id` |

### 4.3 Cricketer Profiles (CRICKETER)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| View Cricketers | `GET /cricketers` | Login Required | `CricketerRepo.list_all` / `get_by_id` | Super Admin/System User sees all; Cricketer sees only their own profile record. |
| Staff Register Player | `POST /cricketers` (action=create) | Staff / Admin | `CricketerRepo.create` | Atomic insertion into `"USER"` and `CRICKETER`. |
| Update Cricketer | `POST /cricketers` (action=update) | Owner / Admin | `CricketerRepo.update` | Cricketer can only edit `cid == session['cricketer_id']`. Staff/Admin can edit any. |
| Delete Cricketer | `POST /cricketers` (action=delete) | Super Admin | `CricketerRepo.delete` | Cascading removal of player record. |

### 4.4 Coach & Trainer Management (TRAINER)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| List Trainers | `GET /trainers` | Login Required | `TrainerRepo.list_all` | `SELECT t.*, u.Name, u.Phone FROM TRAINER t JOIN "USER" u ON t.User_id = u.User_id` |
| Enroll Trainer | `POST /trainers` (action=create) | Super Admin | `TrainerRepo.create` | Atomic insertion into `"USER"` (Role='Trainer') and `TRAINER`. |
| Update Trainer | `POST /trainers` (action=update) | Super Admin | `TrainerRepo.update` | `UPDATE TRAINER SET Specialization=..., Qualification=..., Salary=...` |
| Remove Trainer | `POST /trainers` (action=delete) | Super Admin | `TrainerRepo.delete` | `DELETE FROM TRAINER WHERE Trainer_id = :p_trainer_id` |

### 4.5 Training Programs (CRICKET_PROGRAM)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| View Programs | `GET /programs` | Login Required | `ProgramRepo.list_all` | `SELECT * FROM CRICKET_PROGRAM ORDER BY Program_name` |
| Create Program | `POST /programs` (action=create) | Staff / Admin | `ProgramRepo.create` | `INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)` |
| Edit Program | `POST /programs` (action=update) | Staff / Admin | `ProgramRepo.update` | `UPDATE CRICKET_PROGRAM SET Program_name=..., Duration=...` |
| Delete Program | `POST /programs` (action=delete) | Super Admin | `ProgramRepo.delete` | `DELETE FROM CRICKET_PROGRAM WHERE Program_id = :p_program_id` |

### 4.6 Venues & Grounds (VENUE)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| List Venues | `GET /venues` | Login Required | `VenueRepo.list_all` | `SELECT * FROM VENUE ORDER BY Venu_name` |
| Register Ground | `POST /venues` (action=create) | Staff / Admin | `VenueRepo.create` | `INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)` |
| Update Venue | `POST /venues` (action=update) | Staff / Admin | `VenueRepo.update` | `UPDATE VENUE SET Venu_name=..., Location=..., Capacity=..., Availability=...` |
| Remove Venue | `POST /venues` (action=delete) | Super Admin | `VenueRepo.delete` | `DELETE FROM VENUE WHERE Venu_id = :p_venu_id` |

### 4.7 Training Sessions (TRAINING_SESSION)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| List Sessions | `GET /sessions` | Login Required | `SessionRepo.list_all` | Super Admin/System User: all sessions; Trainer: only sessions where `Trainer_id = :p_trainer_id`; Cricketer: only sessions participated in. |
| Schedule Session | `POST /sessions` (action=create) | Staff / Admin | `SessionRepo.create` | `INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)` |
| Update Session | `POST /sessions` (action=update) | Staff / Assigned Coach | `SessionRepo.update` | Trainers can only update status of their OWN assigned sessions. Staff/Admin can edit any. |
| Cancel Session | `POST /sessions` (action=delete) | Staff / Admin | `SessionRepo.delete` | `DELETE FROM TRAINING_SESSION WHERE Session_id = :p_session_id` |

### 4.8 Payments & Finances (PAYMENT)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| View Invoices | `GET /payments` | Super Admin / Staff / Cricketer | `PaymentRepo.list_all` | Staff/Admin: all invoices; Cricketer: only `Cricketer_id = :p_cid`. Trainers denied access. |
| Create Fee Invoice | `POST /payments` (action=create) | Staff / Admin | `PaymentRepo.create` | `INSERT INTO PAYMENT (Cricketer_id, Program_id, Amount, Due_Date, Payment_Status, Payment_Date)` |
| Mark Fee Paid | `POST /payments` (action=mark_paid) | Staff / Admin | `PaymentRepo.update_status` | `UPDATE PAYMENT SET Payment_Status = 'Paid', Payment_Date = TRUNC(SYSDATE)` |
| Delete Invoice | `POST /payments` (action=delete) | Super Admin | `PaymentRepo.delete` | `DELETE FROM PAYMENT WHERE Cricketer_id=... AND Program_id=... AND Due_Date=...` |

### 4.9 Program Applications (APPLIED_TO)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| View Applications | `GET /applications` | Login Required | `ApplicationRepo.list_all` | Cricketer sees only own applications; Staff/Admin sees all. |
| Apply for Program | `POST /applications` (action=apply) | Cricketer / Staff | `ApplicationRepo.create` | `INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status) VALUES (:p_cid, :p_pid, 'Pending')` |
| Approve / Reject | `POST /applications` (action=update_status) | Staff / Admin | `ApplicationRepo.update_status` | `UPDATE APPLIED_TO SET Applied_status = :p_status`. Players cannot approve themselves. |

### 4.10 Equipment Depot (EQUIPMENT & EQUIPMENT_ISSUED)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| Catalog Gear | `POST /equipment` | Staff / Admin | `EquipmentRepo.create` | `INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)` |
| Issue Equipment | `POST /equipment-issues` (action=issue) | Staff / Admin | `EquipmentIssueRepo.issue_gear` | Checks stock availability (`Quantity >= :p_qty`), updates stock, inserts into `EQUIPMENT_ISSUED`. |
| Return Equipment | `POST /equipment-issues` (action=return) | Staff / Admin | `EquipmentIssueRepo.return_gear` | Updates `Issue_status = 'Returned'`, restores available stock. |

### 4.11 Attendance & Participation (PARTICIPATE_IN)
| Action / Form | Route | Authorization | Repository Function | Oracle SQL / Operation |
| :--- | :--- | :--- | :--- | :--- |
| View Attendance | `GET /participation` | Login Required | `ParticipationRepo.list_all` | Cricketer sees own attendance log; Trainer sees attendance for their sessions; Staff/Admin sees all. |
| Record Attendance | `POST /participation` (action=record) | Assigned Coach / Admin | `ParticipationRepo.record` | `INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)` |
| Calculate Attendance % | In Dashboard & Participation | All Roles | `ParticipationRepo.get_attendance_percentage` | Calls PL/SQL function `calculate_attendance_pct(cid)` with robust pure-SQL fallback. |

---

## 5. Coursework Advanced Queries & Analytical Reports

The application connects the two required coursework queries from `database/05_advanced_queries.sql` to live web report views at `/reports`:

### Query 1: Multi-Table Attendance Roster (5-Table Relational JOIN)
- **Repository Method**: `ReportRepo.get_advanced_attendance_roster()`
- **Route**: `GET /reports` (Section 1)
- **Tables Joined**: `PARTICIPATE_IN`, `CRICKETER`, `"USER"` (for player name), `TRAINING_SESSION`, `TRAINER`, `"USER"` (for coach name), `VENUE`.
- **Academic Relevance**: Demonstrates complex relational joining across 5 core entities with sorting by session date and player name.

### Query 2: Program Popularity & Acceptance Metrics (GROUP BY + Aggregations)
- **Repository Method**: `ReportRepo.get_advanced_program_popularity_report()`
- **Route**: `GET /reports` (Section 2)
- **SQL Constructs**: `GROUP BY cp.Program_id, cp.Program_name, cp.Duration`, `COUNT(a.Cricketer_id)`, `SUM(CASE WHEN a.Applied_status = 'Approved' THEN 1 ELSE 0 END)`, and zero-division protection via `NULLIF(COUNT(a.Cricketer_id), 0)`.
- **Academic Relevance**: Demonstrates conditional aggregation, rate computation, and aggregate data summarization.

