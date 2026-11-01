# Crickethub — Antigravity Implementation and Redesign Prompt

## Goal

Modify the **existing Crickethub project** in place. It is an MCA Cricket Training Management System built with **Flask + Oracle SQL/PLSQL**. Fix the real backend/database workflow, authentication, authorization, role-specific functionality, and UI/UX.

The uploaded screenshot is the visual reference for the landing/login experience: a premium cricket-training website with a large full-width cricket photograph, dark forest-green atmosphere, elegant large typography, clear calls to action, rounded/glass-like navigation, and subtle motion. Use it as inspiration for visual direction, not as a pixel-perfect copy. Use the project name **Crickethub**.

**No prompt has been given to Antigravity yet. Treat this as the single, complete implementation request for all changes below. Do not assume earlier prompts or prior instructions exist. Do not only provide recommendations: inspect the existing files, implement the changes, run available checks, and report exactly what was changed and what still needs manual testing.**

---

## 1. Rules Before Editing

1. Inspect the complete existing project and understand its current architecture before changing anything.
2. Preserve working features and the existing Flask + Oracle technology stack. Do not replace Oracle with SQLite/MySQL or replace Flask with another framework.
3. The supplied ER diagram is the source of truth for database entities, attributes, and relationships. Preserve the existing schema contract:
   - `USER`
   - `CRICKETER`
   - `TRAINER`
   - `CRICKET_PROGRAM`
   - `TRAINING_SESSION`
   - `VENUE`
   - `PAYMENT`
   - `EQUIPMENT`
   - `APPLIED_TO`
   - `EQUIPMENT_ISSUED`
   - `PARTICIPATE_IN`
4. Verify exact columns, datatypes, keys, constraints, and relationship cardinalities against the actual diagram and existing SQL files. Do not invent column names or assume attributes not in the schema.
5. Do not add or rename tables, columns, or relationships just to make the UI easier. If a requested feature is unsupported by the schema, explain the limitation and implement only a truthful, schema-compatible alternative.
6. Do not delete the user's database, drop tables, reset data, or run destructive scripts as part of app startup or testing.
7. Keep database setup/sample scripts separate from runtime application queries.
8. Keep secrets in `.env`; do not overwrite local credentials. Keep `.env` out of source control.
9. Do not claim tests passed unless they were actually run. Do not claim Oracle integration was tested if no Oracle connection was available.
10. Work incrementally and preserve existing user changes. Avoid broad rewrites where a focused fix is safer.

---

## 2. Fix the Current Oracle Login Error

The application currently logs:

`ORA-01745: invalid host/bind variable name`

Trace the login request from the Flask route into the repository and identify the exact SQL statement and bind parameter causing this error.

- Fix the actual invalid bind-variable name or SQL syntax; do not guess blindly.
- Ensure bind names in SQL match the parameter dictionary exactly.
- Use named bind variables supported by the Oracle driver and parameterized queries for all user-supplied values.
- Never concatenate login input directly into SQL.
- Add useful server-side diagnostic logging without exposing raw Oracle errors, SQL text, passwords, or secrets to the browser.
- Verify successful login and invalid-login behavior if Oracle is available.
- Do not change or recreate tables to work around this error.

---

## 3. Environment Configuration and Secret Key

Inspect `db.py`, `app.py`, and the environment-loading code. The current `.env` uses these names:

- `SECRET_KEY`
- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_HOST`
- `ORACLE_PORT`
- `ORACLE_SERVICE`

Make sure the application reads the same variable names consistently.

- Remove any hardcoded or predictable fallback Flask secret key.
- Require a non-empty secret key from environment configuration and show a clear startup error if missing.
- Do not print secrets in logs.
- Keep local `.env` values intact.
- Document how to generate a strong key with Python's `secrets` module.
- Do not rotate or overwrite the user's current secret automatically.
- Ensure Oracle connection errors are handled cleanly and database connections/cursors are closed reliably.

---

## 4. Database Safety and SQL File Organization

### 4.1 Prevent accidental data loss

The sample data script currently deletes rows before inserting baseline data, and setup scripts may contain destructive DDL.

- Review every SQL file for `DROP`, broad `DELETE`, and other destructive statements.
- Never run schema-creation or sample-data scripts automatically when Flask starts.
- Make destructive reset behavior opt-in, clearly labelled, and separate from normal setup.
- Prefer a separate explicitly named reset/demo-data script when a reset is genuinely needed.
- For ordinary sample-data setup, either make it safely repeatable without deleting existing user data or clearly label it as a one-time/demo-only script and explain the risks.
- Do not run destructive scripts against the user's current database.
- Check primary keys, foreign keys, insert order, status constraints, and sample data consistency.

### 4.2 Runtime SQL queries must be easy to locate

The academic SQL scripts and the runtime web-app queries serve different purposes. Keep this distinction clear.

- Keep table/schema setup and seed data in the `database/` SQL files.
- Keep the function, procedure, cursor, and trigger scripts in dedicated SQL files, organized by module as already intended.
- **The coursework needs two advanced queries, and both must be demonstrated through the website.** The current `05_advanced_queries.sql` contains eight candidate queries; do not retain all eight by default.
- Review the eight current candidates and choose the two best aligned with the assignment requirements and actual Crickethub features. Prefer queries that visibly demonstrate meaningful advanced SQL, such as a multi-table attendance JOIN and a program-enrollment aggregate, unless the assignment requirements make other choices more appropriate.
- Keep the selected two as clearly labelled SQL statements in `05_advanced_queries.sql`, and connect the same query logic to real repository functions and frontend report pages. Avoid maintaining a disconnected SQL*Plus-only copy and a different, unrelated implementation in Python.
- Each selected query must be executed when an authorized user opens the relevant report page (or applies its filters). Display real Oracle results in the browser, with useful empty/error states and role-based access. A user must be able to demonstrate the query by opening the website and explaining the SQL, not by manually running it in SQL*Plus.
- Remove the other six from the active deliverable unless a separate explicit coursework requirement needs them. If you move them to an optional reference file, make clear they are not required and are not presented as implemented features. Do not inflate the academic query count.
- Runtime SQL used when a user submits a frontend form or opens a report must be in the application's repository/data-access layer, not hidden inside templates or scattered throughout route handlers.
- Organize runtime repository operations clearly by feature/module. Preserve `repositories.py` if it already centralizes the queries; otherwise, refactor carefully into a simple module-oriented structure, without creating needless complexity.
- Give each database operation a descriptive function name and a short comment explaining its purpose.
- Use parameterized SQL throughout.
- Use transactions correctly: commit successful writes, roll back failed writes, and close cursors/connections.
- Return meaningful results/errors to the route layer instead of silently pretending success.

Create or update a concise `DATABASE_WORKFLOW.md` explaining:
- which SQL files create/prepare each module's tables;
- which file contains sample data;
- where runtime SELECT/INSERT/UPDATE/DELETE queries live;
- which repository function is called for each form/action;
- which PL/SQL function/procedure/cursor/trigger is used and how it is invoked, if applicable;
- how a form request flows through Flask to Oracle;
- safe commands for running the scripts in the correct order.

Do not duplicate runtime queries in multiple places. Basic and advanced academic SQL examples should remain ordinary SQL where appropriate, not be unnecessarily wrapped in PL/SQL.

---

## 5. Correct End-to-End Form and Database Workflows

Trace every visible form, button, link, table action, and filter. For each one, confirm that it is connected to a real backend route and the intended Oracle operation.

Use this workflow as the design standard:

`HTML form / JavaScript → Flask route in app.py → validation + authorization → repository function → parameterized Oracle SQL via db.py → commit/rollback → truthful response → updated frontend`

For each operation:
- Validate required fields, data types, allowed status values, and IDs on the server.
- Enforce the current user's permissions on the server before reading or changing records.
- Use parameterized SQL.
- Show success only after the database operation succeeds.
- Show a clear, safe error if it fails.
- Refresh or update the visible data after successful writes.
- Never use hardcoded frontend arrays or fake dashboard numbers as a substitute for database data.
- Make empty states and error states understandable.
- Remove or disable dead buttons, fake links, and actions that do nothing.
- Avoid silently swallowing exceptions.
- Ensure failed transactions are rolled back.

At minimum, test and document the supported CRUD/query workflows for:
- user/account management;
- cricketer profile management;
- trainer management;
- cricket programs and applications;
- training sessions and venues;
- payments and dues;
- equipment inventory and equipment issue/return;
- attendance/participation;
- dashboard and reporting queries.

Do not promise a CRUD operation if the schema, foreign keys, or permissions do not support it.

---

## 6. Authentication, Registration, and Passwords

The current login template visibly lists four demo accounts and the same general dashboard/navigation is presented across roles. There is no proper public registration flow. Replace this with a usable, secure account flow and genuinely role-specific screens.

### Registration

- Add a polished registration page for new **Cricketer** accounts.
- Collect only information supported by the actual schema. Verify how login identity is represented before deciding whether to use name, phone, or another existing field; do not invent an email/username column.
- Create the `USER` and related `CRICKETER` records in a single safe transaction, using the correct parent/child insertion order and generated IDs only if supported by the current schema.
- Validate fields server-side and reject duplicate login identifiers/phone values according to the schema and project rules.
- Never allow public registration to choose `Super Admin`, `System User`, or `Trainer`.
- New public registrations must receive the `Cricketer` role only.
- If the schema cannot safely support unique login identity or ID generation, explain the exact limitation and propose the smallest schema-compatible fix for approval rather than silently inventing a design.
- Provide helpful validation errors and a link back to login.

### Login/logout/password handling

- Remove demo credentials/passwords from the public login page.
- Verify that passwords are securely hashed and verified using a suitable password-hashing library; never compare or store plaintext passwords as the normal authentication method.
- Existing sample rows may use old/demo hashes. Handle these accounts safely and document any required password reset or migration. Do not silently accept plaintext passwords.
- Add logout and reliable session handling.
- Regenerate the session after successful login.
- Use secure cookie settings appropriate for local development and document production considerations.
- Protect state-changing form submissions against CSRF where applicable.
- Add reasonable login throttling if it can be implemented safely without locking users out permanently.
- Never log passwords, secret keys, or complete sensitive records.

### Demo accounts

- Remove credential disclosure from the normal UI.
- If demo accounts are needed for a classroom demonstration, document them in a separate local-only developer/demo guide and never present them as a public login shortcut.
- Do not assume all sample accounts share the same password without verifying the current hash and login implementation.

---

## 7. Role-Based Authorization — Critical

The current app appears to show very similar interfaces to all roles and does not adequately restrict access to records/actions. Implement role-specific navigation, dashboards, routes, and server-side authorization.

Use the roles already present in the current project/schema:
- `Super Admin`
- `System User`
- `Trainer`
- `Cricketer`

Do not add a new role unless the existing schema and project owner explicitly approve it.

### Super Admin

May manage the academy across supported modules:
- users and role assignments;
- cricketers and trainers;
- programs and applications;
- sessions and venues;
- payments and financial reports;
- equipment and issue/return records;
- attendance records;
- relevant reports and administration.

Restrict role changes and sensitive actions to this role. Add confirmation for destructive actions.

### System User

The existing role's meaning is unclear. Define it explicitly in `README.txt` and the UI as a limited **operations/staff** role, not as another unrestricted administrator.

Suggested default scope, only where supported:
- view operational information needed to run the academy;
- manage schedules/program/session logistics;
- assist with applications or equipment workflows only if permitted by the implemented business rules;
- record operational data only when explicitly authorized.

Do not grant unrestricted user-role management or access to all financial records by default. Clearly document its exact permission matrix.

### Trainer

- See only their assigned sessions and relevant training information.
- View the cricketers assigned/participating in those sessions as permitted by the schema.
- Record/update attendance only for sessions they are authorized to manage.
- Cannot change payment status, fees, global user roles, or unrelated sessions.
- Cannot edit another trainer's profile or assigned sessions unless explicitly authorized.

### Cricketer

- View and update only their own permitted profile fields.
- View their own program applications, training schedule, attendance, equipment issue/return history, and payment status/due details.
- May apply to programs if supported by `APPLIED_TO`.
- Must not create or edit official payment records or mark their own dues as paid.
- Must not create/update/delete their own attendance records.
- Must not view other cricketers' personal records, attendance, payment dues, or financial history.
- Must not edit another user's records by changing an ID in a URL, form, or HTTP request.

### Authorization implementation requirements

- Build a centralized role/permission helper or decorators.
- Enforce authorization on every protected Flask route and every state-changing backend action.
- Check record ownership/assignment in database queries and route logic; hiding a button is not security.
- Return appropriate 403/404 responses for unauthorized requests.
- Test direct URL access and manipulated IDs, not only the visible navigation.
- Create a permission matrix in `README.txt` and test each role against it.
- Ensure dashboards and navigation differ meaningfully by role.

---

## 8. Business Logic and Data Integrity

### Attendance

- Official attendance must be entered/updated by an authorized trainer for their assigned session or by an authorized administrator.
- Cricketers can view their own attendance only.
- Validate that the session exists and that the cricketer is legitimately associated with it where the schema/business rules require this.
- Prevent duplicate participation rows where prohibited by the actual key/constraints.
- Attendance percentages must be calculated from real participation data, with sensible handling of no records.

### Payments

- Payment records and payment status are controlled by authorized staff/admin only.
- Cricketers may see only their own dues/status.
- Validate amount, dates, status, and cricketer/program references.
- Do not treat a frontend click as proof of payment.
- Do not invent an online payment gateway if none exists.

### Equipment

- Review the current `EQUIPMENT` columns, especially `Total_Quantity`, `Quantity`, and `Availability`, and define their meaning based on existing project logic.
- Issuing equipment must validate available quantity.
- Returning equipment must update inventory exactly once.
- Prevent negative quantities and duplicate returns.
- Avoid double-updating inventory in both a procedure and a trigger.
- Use a transaction so a failed issue/return leaves inventory and issue records consistent.
- Restrict stock administration to authorized roles; cricketers may view only their own issue history.

### Applications and sessions

- Validate allowed application/session statuses against database constraints.
- Users must not approve their own applications unless the explicitly approved rules allow it.
- Enforce trainer/session assignments and program relationships.
- Use database constraints and transactions as the final integrity layer where appropriate.

### IDs and foreign keys

- Check how IDs are generated. Do not assume identity columns or sequences exist.
- If IDs are manually assigned, do not generate collisions. Implement a safe strategy only after examining the actual schema.
- Respect foreign-key dependencies and existing composite keys.
- Do not change the schema contract casually.

---

## 9. Equipment Logic, PL/SQL Objects, and SQL Academic Requirements

Inspect and test all existing SQL files and PL/SQL objects rather than assuming they are correct.

- Function: attendance percentage, based on real attendance columns and statuses.
- Procedure: equipment issue with validation, if this matches the current agreed design.
- Cursor: list pending payment details.
- Trigger: inventory/availability maintenance only if appropriate to the existing design.
- Implement exactly two advanced SQL queries for the coursework. Select the best two from the existing eight based on assignment fit and schema correctness.
- Connect both required advanced queries to real Crickethub frontend report pages through repository functions and Flask routes. Do not treat an SQL*Plus-only query as a completed website feature.
- In the final report, name each query, identify the exact repository function/route/template that uses it, and explain how to demonstrate it in the browser. Explain why any of the other six candidates were removed or kept only as optional references.
- Keep ordinary SQL queries as ordinary SQL; use PL/SQL only where appropriate.
- Do not double-update inventory from a procedure and trigger.
- Add clear comments for MCA-level explanation/viva.
- Test objects using valid sample data, but never run destructive test calls against existing user data.
- Clearly report compilation errors and invalid database objects.

Preserve the intended 10-file organization unless a necessary change is explained:
1. `01_authentication_user_management.sql`
2. `02_training_management.sql`
3. `03_finance_equipment.sql`
4. `04_attendance_participation.sql`
5. `05_advanced_queries.sql`
6. `06_function.sql`
7. `07_procedure.sql`
8. `08_cursor.sql`
9. `09_trigger.sql`
10. `10_sample_data.sql`

Verify the actual dependency order before documenting the execution order. Sample data and PL/SQL test calls may require objects to be created first. Never tell the user to run files in an order that has not been checked.

---

## 10. Frontend Redesign — Use the Uploaded Screenshot as Inspiration

The current UI is too plain. Redesign it into a coherent, premium cricket academy website with a consistent style across landing, authentication, dashboards, forms, and tables.

### Visual direction

Use the supplied screenshot as the primary visual reference:
- full-bleed cricket ground / player photography in a large hero section;
- deep forest-green and natural pitch-green palette;
- warm off-white typography and light surfaces where appropriate;
- oversized elegant serif display typography for major landing headings, paired with a clean readable sans-serif for controls/body;
- rounded pill-shaped buttons and navigation;
- tasteful translucent/glass-like elements over photography when contrast remains accessible;
- generous spacing, clear visual hierarchy, strong photography, polished cards and data tables;
- subtle cricket-themed details such as pitch lines, field shapes, or ball/seam motifs—do not clutter the interface;
- use the product name **Crickethub** consistently.

Do not copy unrelated text, fake player counts, fake testimonials, or the exact branding from the reference image. Use real database figures for academy statistics; if no real data is available, omit the metric or display a truthful empty state.

### Landing page

The current project has a login page but does not provide a proper public registration flow. Add a public landing route as the site's first impression; do not redirect every unauthenticated visitor straight to the plain login form. Keep the login route available and make the landing page's Join/Register and Log in buttons navigate to working routes.

Create a strong public landing page with:
- a cricket-themed hero image;
- headline and short introduction to the academy;
- clear `Join / Register` and `Log in` actions;
- sections linking to available programs, training schedules, and coaching information only where backed by real data/features;
- clear navigation and footer;
- responsive layout for desktop, tablet, and mobile.

Use properly licensed/available assets or remote image URLs only if they are reliable and permitted. Provide a sensible fallback if an image fails to load. Do not embed enormous base64 images in HTML or use broken asset links. Keep local assets organized in `static/images/` where appropriate.

### Login and registration

- Create dedicated, visually polished login and registration pages in the same design system.
- Use an image/photographic panel or background inspired by the screenshot, balanced with a readable form panel.
- Ensure the form remains readable on mobile and over any image overlay.
- Include proper labels, validation messages, password visibility toggle if implemented accessibly, and links between login and registration.
- Never display passwords or secret credentials in the interface.

### Role-specific dashboards

Keep the shared design system but give each role a useful, different dashboard:
- Super Admin: system overview, management shortcuts, and real operational/financial summaries permitted to this role.
- System User: limited operations-focused view.
- Trainer: assigned sessions, attendance tasks, and relevant cricketer lists.
- Cricketer: own upcoming sessions, application statuses, attendance summary, equipment history, and own payment status.

Only show metrics and actions that exist and can be backed by Oracle queries and permissions. No fake cards, dead links, or fake charts.

### Forms, tables, and feedback

- Consistent input styles, field spacing, focus states, inline validation, error banners, and success feedback.
- Responsive tables with useful empty states, status badges, filters, and search where practical.
- Confirm destructive actions and show useful result messages.
- Provide loading/disabled states while an action is being submitted to prevent duplicate submissions.

### Animation and transitions

Add restrained, polished motion:
- hero text/image fade or rise-in on initial load;
- subtle card entrance/hover transitions;
- smooth button, navigation, and form focus transitions;
- modest section reveal animations if implemented without hurting accessibility or performance;
- avoid excessive bouncing, parallax, or animation that makes the site feel distracting.
- Respect `prefers-reduced-motion: reduce`.
- Do not make functionality dependent on animation or JavaScript effects.

### Accessibility and responsiveness

- Semantic HTML and correct heading hierarchy.
- Keyboard navigation and visible focus indicators.
- Adequate color contrast and form labels.
- Accessible names for icon-only buttons.
- Do not communicate status by color alone.
- Responsive behavior at common desktop/tablet/mobile widths.
- Avoid horizontal overflow and text over photographs with insufficient contrast.

Keep CSS maintainable. Do not add a large frontend framework unless the project already uses one or there is a clear need.

---

## 11. Architecture and Code Quality

- Keep routes in `app.py` or the current route structure.
- Keep Oracle connection logic in `db.py`.
- Keep SQL queries in repository/data-access functions.
- Keep templates free of direct SQL.
- Keep HTML, CSS, and JavaScript organized in their existing folders.
- Use parameterized Oracle SQL for every user-controlled value.
- Avoid duplicated queries and business rules.
- Use consistent naming, comments where they clarify non-obvious logic, and beginner-friendly code appropriate for an MCA project.
- Avoid adding unnecessary packages.
- Add/adjust dependencies only when required and document them.
- Ensure a missing environment variable, database outage, or missing PL/SQL object produces a clear and safe message.

---

## 12. Required Testing

Perform the checks possible in the current environment. Clearly separate automated checks from manual tests requiring a running Oracle server.

### Code checks

- Python syntax/compile checks.
- Import/dependency checks where possible.
- Template rendering and route checks where possible.
- Verify that no runtime query relies on nonexistent columns.
- Verify every visible form/action points to a real route.
- Check links, navigation, responsive CSS, and browser console errors if a browser test environment is available.

### Authentication/authorization tests

Test:
- successful login and incorrect password;
- registration success and duplicate registration;
- logout and protected-page access after logout;
- each role's permitted and forbidden routes/actions;
- cricketer trying to modify their own attendance/payment;
- cricketer attempting to access another person's record by changing an ID;
- trainer attempting to edit an unassigned session;
- unauthorized role change and admin-only action;
- missing/invalid form values and database failures.

### Database tests

When a safe Oracle test schema is available:
- confirm all SQL scripts compile/run in the verified order;
- verify FK/constraint behavior;
- test each supported INSERT/SELECT/UPDATE/DELETE flow;
- test rollback behavior after a failed write;
- verify inventory quantities on issue/return;
- test attendance calculations and pending-payment cursor;
- check PL/SQL object validity and errors;
- confirm the app works with the exact `.env` variable names.

**Do not delete or reset the user's existing database to run these tests.** Use a separate test schema or ask before any potentially destructive operation.

### UI tests

- Landing/login/registration on desktop and mobile widths.
- Role-specific dashboards.
- Form validation and success/failure states.
- No broken images or dead buttons.
- Keyboard focus and reduced-motion behavior.
- No fake figures or records.

---

## 13. Documentation to Deliver

Update `README.txt` or the existing README with:
- project purpose and stack;
- folder/file explanation;
- Python/virtual environment/dependency setup;
- Oracle server versus SQL*Plus explanation;
- `.env` variable names (never real secret values);
- how to connect to Oracle and verify the service;
- SQL file execution order verified against actual dependencies;
- how to start and stop Flask;
- registration/login process;
- the four roles and their exact permissions;
- how each module's forms connect to repository queries and database operations;
- function/procedure/cursor/trigger purpose and testing;
- known limitations and troubleshooting.

Create/update `DATABASE_WORKFLOW.md` as described above. Add a concise `IMPLEMENTATION_REPORT.md` listing:
- files changed;
- bugs fixed;
- features implemented;
- tests actually run and their results;
- tests that require the user's Oracle instance/manual checking;
- remaining limitations or decisions needing approval.

Do not include actual credentials or generated secret keys in documentation.

---

## 14. Implementation Order

Work in this order to avoid cosmetic changes masking critical bugs:

1. Inspect the project and map routes, repository functions, templates, SQL scripts, and schema.
2. Fix login bind-variable error and environment configuration.
3. Protect existing data and verify SQL script safety.
4. Implement registration, login/logout, password handling, and session safety.
5. Implement role-based authorization and record ownership checks.
6. Fix every form-to-database workflow and module-specific queries.
7. Fix attendance, payments, applications, and equipment business rules.
8. Redesign the landing page, login/register, and role dashboards.
9. Add transitions, responsive behavior, and accessibility improvements.
10. Run tests, update documentation, and provide a precise report.

Do not stop after producing a plan. Implement the changes in the existing project and report any blocker instead of silently skipping it.

---

## 15. Final Response Required from Antigravity

When implementation is complete, provide a short, structured summary:
1. Critical bugs fixed.
2. Authentication/registration changes.
3. Role permissions implemented.
4. Database operations/modules connected or corrected.
5. UI/UX changes.
6. Exact files changed/created.
7. Tests run and their actual outcomes.
8. Any manual Oracle testing still required.
9. Any unresolved schema/design limitation.

Be honest about incomplete items. Do not mark an item complete merely because code was written.
