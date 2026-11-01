-- =====================================================================
-- CRICKETHUB - OPTIONAL REFERENCE QUERIES
-- File: optional_reference_queries.sql
-- Description:
--   Contains additional exploratory queries (Queries 3 through 8)
--   preserved for reference only.
--   NOTE: These are NOT part of the active coursework deliverable.
--   The two required coursework queries are maintained in:
--   05_advanced_queries.sql and demonstrated live at /reports.
-- =====================================================================

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 3: FINANCIAL REVENUE & OUTSTANDING DUES AUDIT (GROUP BY + HAVING)
-- Purpose:
--   Summarizes total fees, paid amounts, and outstanding dues per program.
--   Filters programs having pending dues greater than 0 using HAVING.
-- ---------------------------------------------------------------------
SELECT
    cp.Program_name,
    COUNT(pay.Cricketer_id) AS Total_Billing_Records,
    SUM(pay.Amount) AS Total_Expected_Revenue,
    SUM(CASE WHEN pay.Payment_Status = 'Paid' THEN pay.Amount ELSE 0 END) AS Total_Collected,
    SUM(CASE WHEN pay.Payment_Status = 'Pending' THEN pay.Amount ELSE 0 END) AS Total_Outstanding
FROM CRICKET_PROGRAM cp
JOIN PAYMENT pay ON cp.Program_id = pay.Program_id
GROUP BY cp.Program_name
HAVING SUM(CASE WHEN pay.Payment_Status = 'Pending' THEN pay.Amount ELSE 0 END) > 0
ORDER BY Total_Outstanding DESC;

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 4: ACTIVE TRAINER WORKLOAD & CAPACITY UTILIZATION
-- Purpose:
--   Aggregates sessions conducted and total distinct players trained
--   by each coach.
-- ---------------------------------------------------------------------
SELECT
    u.Name AS Trainer_Name,
    t.Specialization,
    t.Qualification,
    COUNT(DISTINCT s.Session_id) AS Sessions_Scheduled,
    COUNT(pi.Cricketer_id) AS Total_Player_Attendances,
    COUNT(DISTINCT pi.Cricketer_id) AS Unique_Cricketers_Trained
FROM TRAINER t
JOIN "USER" u ON t.User_id = u.User_id
LEFT JOIN TRAINING_SESSION s ON t.Trainer_id = s.Trainer_id
LEFT JOIN PARTICIPATE_IN pi ON s.Session_id = pi.Session_id AND pi.Attendance = 'Present'
GROUP BY u.Name, t.Specialization, t.Qualification
ORDER BY Sessions_Scheduled DESC;

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 5: SUBQUERY (IN) - PLAYERS ENROLLED IN HIGH-INTENSITY PROGRAMS
-- Purpose:
--   Finds all cricketers who applied for programs lasting 3 months or longer.
-- ---------------------------------------------------------------------
SELECT
    c.Cricketer_id,
    u.Name AS Cricketer_Name,
    u.Phone,
    u.Address
FROM CRICKETER c
JOIN "USER" u ON c.User_id = u.User_id
WHERE c.Cricketer_id IN (
    SELECT a.Cricketer_id
    FROM APPLIED_TO a
    JOIN CRICKET_PROGRAM p ON a.Program_id = p.Program_id
    WHERE LOWER(p.Duration) LIKE '%3 month%' OR LOWER(p.Duration) LIKE '%6 month%'
);

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 6: SUBQUERY (NOT EXISTS) - CRICKETERS WITH ZERO OVERDUE PAYMENTS
-- Purpose:
--   Identifies disciplined cricketers who have no pending or failed fees.
-- ---------------------------------------------------------------------
SELECT
    c.Cricketer_id,
    u.Name AS Cricketer_Name,
    u.Phone
FROM CRICKETER c
JOIN "USER" u ON c.User_id = u.User_id
WHERE NOT EXISTS (
    SELECT 1
    FROM PAYMENT p
    WHERE p.Cricketer_id = c.Cricketer_id
      AND p.Payment_Status IN ('Pending', 'Failed')
)
ORDER BY u.Name;

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 7: INVENTORY UTILIZATION & CRITICAL STOCK ALERT
-- Purpose:
--   Reports on equipment assets, how many units are currently issued out,
--   available in store, and flags items where availability is critical (< 3).
-- ---------------------------------------------------------------------
SELECT
    eq.Equipment_id,
    eq.Equipment_name,
    eq.Equipment_type,
    eq.Total_Quantity,
    eq.Quantity AS Stock_In_Hand,
    NVL(SUM(CASE WHEN ei.Issue_status = 'Issued' THEN ei.Quantity ELSE 0 END), 0) AS Currently_Issued,
    CASE
        WHEN eq.Quantity = 0 THEN 'OUT OF STOCK'
        WHEN eq.Quantity <= 3 THEN 'CRITICAL / LOW STOCK'
        ELSE 'ADEQUATE'
    END AS Stock_Health
FROM EQUIPMENT eq
LEFT JOIN EQUIPMENT_ISSUED ei ON eq.Equipment_id = ei.Equipment_id
GROUP BY eq.Equipment_id, eq.Equipment_name, eq.Equipment_type, eq.Total_Quantity, eq.Quantity
ORDER BY eq.Quantity ASC;

-- ---------------------------------------------------------------------
-- REFERENCE QUERY 8: VENUE OCCUPANCY REPORT (AGGREGATE + GROUP BY)
-- Purpose:
--   Counts total sessions hosted across venues to evaluate utilization.
-- ---------------------------------------------------------------------
SELECT
    v.Venu_id,
    v.Venu_name,
    v.Location,
    v.Capacity,
    v.Availability,
    COUNT(s.Session_id) AS Total_Sessions_Hosted
FROM VENUE v
LEFT JOIN TRAINING_SESSION s ON v.Venu_id = s.Venu_id
GROUP BY v.Venu_id, v.Venu_name, v.Location, v.Capacity, v.Availability
ORDER BY Total_Sessions_Hosted DESC;

