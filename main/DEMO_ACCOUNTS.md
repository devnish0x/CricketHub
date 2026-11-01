# Crickethub — Classroom Demonstration Accounts Guide

> **Confidential — For Coursework Evaluation & Local Development Only**
>
> This document details pre-seeded demo accounts present in the Oracle database for evaluator and faculty demonstration of Crickethub.

---

## 1. Demo User Accounts Matrix (Live Database Seeded)

All accounts below can be authenticated using either their numeric **User ID** or their registered **Phone Number**.

| Role | User ID | Phone Number | Account Name | Default Password | Dashboard Capabilities & Access Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | `1` | `9876543210` | **Kavana Admin** | `password123` | Complete administrative authority. Full CRUD across all 11 tables, role reassignments, financial invoice generation, user account deletion, and analytical reporting. |
| **System User** | `2` | `9876543211` | **Nishan Maindan** | `password123` | Academy operations & ground staff. Schedules training sessions, manages venue allocations, reviews program applications, issues/returns gear, and accesses analytical reports. Cannot delete user accounts or alter fee structures. |
| **Trainer** | `3` | `9876543212` | **Rahul Dravid** | `password123` | Head coach. Scoped exclusively to assigned training sessions (`Trainer_id = 1`). Enters attendance for participating players, reviews supervised trainee directory, and accesses attendance roster reports. Cannot alter fees, venues, or unrelated sessions. |
| **Cricketer** | `6` | `9876543215` | **Vaibhav Tamboli** | `password123` | Active player account (`Cricketer_id = 1`). Scoped exclusively to own data: personal attendance % (via PL/SQL calculation), scheduled training sessions, program applications, gear checkout history, and pending fee dues. Cannot alter official attendance or payment records. |

---

## 2. Additional Seeded Player & Coach Accounts

For multi-user testing or attendance roster demonstration:

| Account Name | Role | User ID | Phone | Cricket Discipline |
| :--- | :--- | :--- | :--- | :--- |
| **Zaheer Khan** | Trainer | `4` | `9876543213` | Fast Bowling Coach |
| **Jonty Rhodes** | Trainer | `5` | `9876543214` | Fielding & Fitness Coach |
| **Meghraj Hegde** | Cricketer | `7` | `9876543216` | Left Hand Bat / Right-arm leg break |
| **Shubman Gill** | Cricketer | `8` | `9876543217` | Right-hand bat / Right-arm off break |
| **Smriti Mandhana** | Cricketer | `9` | `9876543218` | Left Hand Bat / Right-arm medium |
| **Rishabh Pant** | Cricketer | `10` | `9876543219` | Left Hand Bat / Wicketkeeper |

*Default password for all seeded accounts:* `password123`

---

## 3. Recommended Classroom Demonstration Sequence

### Step 1: Public Landing Page & Player Registration
1. Navigate to `http://localhost:5000/`.
2. Review the cricket photography hero section, real Oracle statistics strip, and training curriculum cards.
3. Click **"Join Academy"** or **"Register as a Player"** (`/register`).
4. Register a new cricketer (e.g., "Arjun Tendulkar", phone `9811223344`, password `password123`).
5. Notice that the player is automatically logged in and redirected to their personal **Player Dashboard** (`/dashboard`).

### Step 2: Cricketer Experience & Program Application
1. View the personal attendance percentage gauge and empty states for new players.
2. Click **"Apply for a Program"** or navigate to `http://localhost:5000/programs`.
3. Submit an application for an active program.
4. Verify the application appears as `Pending` under **My Applications** (`/applications`).
5. Sign out.

### Step 3: System User (Operations Staff) Workflow
1. Sign in as System User: ID `2`, password `password123`.
2. Notice the dashboard is customized for operations: ground slots, venue availability, pending application queue.
3. Open **Applications** (`/applications`), locate the pending application, and click **"Approve"**.
4. Navigate to **Equipment Depot** (`/equipment-issues`) and check out gear for a player.
5. Sign out.

### Step 4: Trainer (Coach) Workflow & Attendance Marking
1. Sign in as Trainer: ID `3`, password `password123`.
2. Notice the dashboard displays only Coach Rahul Dravid's assigned sessions and trainees under his supervision.
3. Click **"Mark Attendance"** for a session.
4. Record attendance (`Present` or `Absent`) for assigned players.
5. Notice the Trainer cannot access financial fee accounts (`/payments` redirects with access warning).
6. Sign out.

### Step 5: Super Admin & Coursework Advanced SQL Demonstration
1. Sign in as Super Admin: ID `1`, password `password123`.
2. Review full academy financial totals, user accounts, and operational metrics.
3. Navigate to **Analytical Reports** (`/reports`).
4. **Demonstrate Query 1**: Multi-Table Attendance Roster (5-Table Relational JOIN). Click *"View SQL Query"* to explain the JOIN logic for viva.
5. **Demonstrate Query 2**: Program Popularity & Acceptance Analytics (GROUP BY, SUM CASE, NULLIF).
