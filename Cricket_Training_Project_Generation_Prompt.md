# Crickethub --- Project Generation Prompt

Give this prompt to your coding AI/agent and attach your original ER
diagram image.

------------------------------------------------------------------------

## PROMPT

Create a complete, runnable **Crickethub --- Cricket Training Management
System** using **Python Flask** for the web application and **Oracle
Database with SQL/PL/SQL** for the database. The computer currently has
SQL*Plus, but Python, Flask, and the Oracle Python driver may not be
installed. Include beginner-friendly Windows setup instructions. Clearly
explain that SQL*Plus is a client and an Oracle Database server must be
installed locally or reachable over a network.

## 1. ER diagram is the source of truth

-   Inspect the supplied ER diagram before coding.
-   Preserve its exact entity/table names, attribute/column names, and
    relationships. Do not add, remove, or rename entities or attributes.
-   Do not silently guess unclear names, cardinalities, primary keys, or
    relationship constraints. Flag ambiguity instead.
-   Include primary keys, foreign keys, `NOT NULL`, `UNIQUE`, and
    `CHECK` constraints in the relevant `CREATE TABLE` statements where
    justified by the diagram and requirements. Do not create a separate
    constraints file.
-   Use Oracle-compatible SQL. If a diagram name conflicts with an
    Oracle reserved word (such as `USER`), handle it consistently and
    explain the choice rather than casually renaming schema objects.
-   The expected tables are `USER`, `CRICKETER`, `TRAINER`,
    `CRICKET_PROGRAM`, `TRAINING_SESSION`, `VENUE`, `PAYMENT`,
    `EQUIPMENT`, `APPLIED_TO`, `EQUIPMENT_ISSUED`, and `PARTICIPATE_IN`;
    the diagram itself overrides this list.

## 2. Required project structure

``` text
Crickethub/
├── app.py
├── db.py
├── repositories.py
├── requirements.txt
├── README.txt
├── .env.example
├── .gitignore
├── database/
│   ├── 01_authentication_user_management.sql
│   ├── 02_training_management.sql
│   ├── 03_finance_equipment.sql
│   ├── 04_attendance_participation.sql
│   ├── 05_advanced_queries.sql
│   ├── 06_function.sql
│   ├── 07_procedure.sql
│   ├── 08_cursor.sql
│   ├── 09_trigger.sql
│   └── 10_sample_data.sql
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── users.html
│   ├── cricketers.html
│   ├── trainers.html
│   ├── programs.html
│   ├── sessions.html
│   ├── venues.html
│   ├── payments.html
│   ├── equipment.html
│   ├── applications.html
│   ├── equipment_issues.html
│   └── participation.html
└── static/
    ├── css/style.css
    └── js/main.js
```

Create only pages that correspond to genuinely implemented
functionality. Do not add database entities or attributes to support a
page.

## 3. Frontend design --- important

Make Crickethub look polished, modern, cricket-oriented, simple, smooth,
aesthetic, and easy to use.

-   Use a tasteful cricket-inspired identity: restrained green tones,
    light/off-white backgrounds, readable dark text, subtle pitch/field
    motifs, and a small complementary accent colour.
-   Use consistent typography, spacing, responsive navigation, readable
    tables, accessible forms, helpful empty states, and clear
    success/error messages.
-   Add subtle, lightweight animations/transitions for hover/focus
    states, buttons, menus, and section entrances. Respect
    `prefers-reduced-motion`.
-   Ensure contrast, keyboard navigation, visible focus states, semantic
    HTML, and accessible form labels.
-   Avoid clutter, excessive gradients, heavy animations, broken remote
    assets, or generic-looking admin templates.
-   No fake charts, hard-coded dashboard statistics, dummy records
    presented as real, decorative controls, dead links, fake
    notifications, or buttons that do nothing.
-   Every visible action must work end-to-end. Do not add unnecessary
    features just to make the interface look bigger.
-   Keep the interface responsive on desktop, tablet, and mobile.

## 4. SQL file responsibilities

### `01_authentication_user_management.sql`

Create `USER`, `CRICKETER`, and `TRAINER` with exact diagram attributes
and constraints. Add commented module-specific ordinary SQL examples:
`INSERT`, `SELECT`, `WHERE`, `UPDATE`, safe `DELETE`, and relevant
`JOIN`s.

### `02_training_management.sql`

Create `CRICKET_PROGRAM`, `TRAINING_SESSION`, and `VENUE`. Add
constraints and basic queries for insert, view, search, update, safe
delete, and joins.

### `03_finance_equipment.sql`

Create `PAYMENT` and `EQUIPMENT`. Add constraints and basic queries for
payment records/status/totals and equipment
search/quantity/availability.

### `04_attendance_participation.sql`

Create `APPLIED_TO`, `EQUIPMENT_ISSUED`, and `PARTICIPATE_IN`. Add
constraints and basic queries for applications, equipment issue/return,
participation, and attendance. Ensure foreign keys across module files
are valid and document the exact execution order.

### `05_advanced_queries.sql`

Use ordinary SQL (not PL/SQL blocks) for multi-table `JOIN`s,
`GROUP BY`, `HAVING`, aggregate functions, subqueries, and useful
reports (applications, pending payments, attendance, equipment issue
history). Comment each query with its purpose and expected result.

### `06_function.sql`

Create a useful PL/SQL function to calculate attendance percentage using
actual attendance/participation columns. Handle no attendance records
and include a commented test call.

### `07_procedure.sql`

Create a procedure to issue equipment with quantity/availability
validation. Avoid double inventory updates if a trigger performs the
update.

### `08_cursor.sql`

Demonstrate an explicit cursor listing pending payment details. Comment
declaration, opening, fetching, loop exit, and closing.

### `09_trigger.sql`

Maintain equipment availability/quantity on issue and return only if
supported by the diagram's columns and agreed business rules. Explain
the meaning of existing quantity/availability columns and avoid double
updates by both procedure and trigger.

### `10_sample_data.sql`

Insert a small, realistic, consistent dataset for every table. Insert
parent rows before dependent rows. Include valid variations in
payment/application status, equipment availability, and attendance. Use
only diagram attributes. Explain whether the script is one-time or safe
to rerun. Ensure data supports testing queries and PL/SQL objects.

## 5. Keep SQL scripts replaceable without breaking the app

This is important:

-   Treat `database/` scripts as schema setup, sample data, and academic
    demonstration scripts. The basic and advanced queries in these files
    must not need to run every time the web app starts.
-   Put all Flask database operations in `repositories.py`, using
    parameterized SQL and a clearly named function per operation. Keep
    connection setup in `db.py` and HTTP routes in `app.py`.
-   The app must depend on the **schema contract**: exact table names,
    column names, primary keys, foreign-key relationships, and agreed
    meanings from the ER diagram---not on a particular physical SQL
    script's comments or formatting.
-   If the team replaces/re-writes manual `CREATE TABLE` scripts but
    produces the same schema contract (same entities, attributes,
    relationships, compatible data types and constraints), the Flask app
    should continue working without code changes.
-   Clearly explain that if table/column names, relationships, data
    types, or business meanings change, the related repository queries
    and PL/SQL objects must also be updated. Do not promise
    compatibility when the schema itself changes.
-   Keep function/procedure/trigger calls isolated in repository
    functions. If a required database object is missing, show a clear
    error; never pretend the action succeeded.
-   Avoid duplicating query logic across routes. Use transactions
    appropriately and close cursors/connections reliably.

## 6. Flask functionality

-   Implement only functionality that actually works with the supplied
    schema.
-   Provide real view/add/edit/delete actions where appropriate and
    allowed by foreign keys, plus useful search/filter options.
-   Show real Oracle data; never hard-code dashboard totals or sample
    records into the frontend.
-   Use parameterized SQL to prevent SQL injection.
-   Load database credentials and Flask secret key from environment
    variables; never hard-code real credentials.
-   If login is implemented, hash passwords and use safe session
    handling. Never store or compare plaintext passwords as a secure
    login method.
-   Do not invent database columns to simplify the UI. If the schema
    does not support an action, do not fake it; explain the limitation
    in `README.txt`.

## 7. Comments and code quality

Add useful comments throughout all SQL files, Python modules, repository
functions, Flask routes, relevant HTML, JavaScript, CSS, and setup
guide. Explain purpose and non-obvious decisions without commenting
every trivial line. Keep code understandable for an MCA student viva.

## 8. `README.txt` setup guide

Write a beginner-friendly plain-text guide for Windows covering:

1.  Project purpose and technology stack.
2.  What every folder/file contains.
3.  All prerequisites and why they are needed.
4.  Installing Python and verifying `python --version` or
    `py --version`.
5.  Creating and activating a virtual environment.
6.  Installing dependencies from `requirements.txt`.
7.  SQL\*Plus versus Oracle Database server; explain that a server must
    be installed/running or reachable.
8.  Connecting to Oracle using SQL\*Plus.
9.  Creating a dedicated Oracle project user/schema in an existing
    database and granting required privileges. Explain that generating
    files does not itself install Oracle or create the database user.
10. Configuring `.env` from `.env.example`.
11. Running SQL files in the correct order, including sample data, and
    verifying success.
12. Starting Flask and opening it in a browser.
13. Testing implemented modules and function/procedure/cursor/trigger.
14. Troubleshooting Oracle connections, credentials, missing tables,
    foreign keys, Python packages, and missing database objects.
15. Stopping Flask.
16. Which steps are manual and which are optional.

Use Windows commands and placeholders where local connection details
vary. Do not assume Python, Flask, or Oracle Database server is already
installed. Never instruct the user to use an example password unchanged.

## 9. Final validation

Before delivery: - Verify every table/column against the supplied
diagram. - Verify primary/foreign keys and table creation order. -
Verify sample data satisfies constraints. - Verify PL/SQL objects
compile against the actual schema. - Keep ordinary SQL separate from
PL/SQL. - Verify repository queries match the schema and all visible
frontend actions really work. - Test validation, error handling, and
responsive layout where possible. - Do not claim testing that was not
performed. - Deliver complete project files, not just snippets. - List
unresolved ambiguities and anything that could not be tested. - End
`README.txt` with a concise run checklist.

Start by inspecting the attached ER diagram, then create the complete
**Crickethub** project and its `README.txt`.
