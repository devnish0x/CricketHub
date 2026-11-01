-- =====================================================================
-- CRICKETHUB - COURSEWORK ADVANCED SQL QUERIES & ANALYTICAL REPORTS
-- File: 05_advanced_queries.sql
-- Description:
--   Coursework deliverable containing EXACTLY TWO advanced SQL queries
--   demonstrated end-to-end through the Crickethub web application at /reports:
--   1. Query 1: Multi-Table Attendance Roster (5-Table JOIN with formatted sorting)
--   2. Query 2: Program Popularity & Enrollment Metrics (GROUP BY, Aggregates, Rates)
--
-- Note: Additional queries 3-8 have been moved to optional_reference_queries.sql
-- for reference purposes only and are not part of the active coursework deliverable.
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: MULTI-TABLE ATTENDANCE ROSTER (5-TABLE JOIN)
-- Web Route: /reports (Section 1: "Multi-Table Attendance Roster")
-- Repository: ReportRepo.get_advanced_attendance_roster()
-- Purpose:
--   Retrieves full session attendance details linking Player, User,
--   Session, Trainer, and Venue. Demonstrates relational integrity
--   across five core academy entities.
-- Expected Result:
--   List of player names, batting style, session dates, trainer names,
--   venue names, attendance status, and duration logged.
-- ---------------------------------------------------------------------
SELECT
    u_c.Name            AS Player_Name,
    c."Batting-Style"   AS Batting_Style,
    s.Session_date      AS Session_Date,
    s.Session_time      AS Session_Time,
    u_t.Name            AS Trainer_Name,
    v.Venu_name         AS Venue_Name,
    p.Attendance        AS Attendance_Status,
    p.Participation_time AS Duration_Logged
FROM PARTICIPATE_IN p
JOIN CRICKETER c        ON p.Cricketer_id = c.Cricketer_id
JOIN "USER" u_c         ON c.User_id = u_c.User_id
JOIN TRAINING_SESSION s ON p.Session_id = s.Session_id
JOIN TRAINER t          ON s.Trainer_id = t.Trainer_id
JOIN "USER" u_t         ON t.User_id = u_t.User_id
JOIN VENUE v            ON s.Venu_id = v.Venu_id
ORDER BY s.Session_date DESC, u_c.Name ASC;

-- ---------------------------------------------------------------------
-- QUERY 2: PROGRAM POPULARITY & ENROLLMENT METRICS (GROUP BY + AGGREGATES)
-- Web Route: /reports (Section 2: "Program Enrollment & Acceptance Rates")
-- Repository: ReportRepo.get_advanced_program_popularity_report()
-- Purpose:
--   Calculates total applications, approved count, pending count,
--   and approval percentage for each cricket training program. Demonstrates
--   GROUP BY with conditional aggregation (SUM CASE) and NULLIF protection.
-- Expected Result:
--   One row per program with total applicants, approved/pending breakdown,
--   and calculated approval percentage.
-- ---------------------------------------------------------------------
SELECT
    cp.Program_id,
    cp.Program_name,
    cp.Duration,
    COUNT(a.Cricketer_id) AS Total_Applicants,
    SUM(CASE WHEN a.Applied_status = 'Approved' THEN 1 ELSE 0 END) AS Approved_Count,
    SUM(CASE WHEN a.Applied_status = 'Pending' THEN 1 ELSE 0 END) AS Pending_Count,
    ROUND(
        NVL(
            (SUM(CASE WHEN a.Applied_status = 'Approved' THEN 1 ELSE 0 END) * 100.0) /
            NULLIF(COUNT(a.Cricketer_id), 0),
            0
        ), 2
    ) AS Approval_Rate_Pct
FROM CRICKET_PROGRAM cp
LEFT JOIN APPLIED_TO a ON cp.Program_id = a.Program_id
GROUP BY cp.Program_id, cp.Program_name, cp.Duration
ORDER BY Total_Applicants DESC;
