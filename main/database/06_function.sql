-- =====================================================================
-- CRICKETHUB - PL/SQL STORED FUNCTION
-- File: 06_function.sql
-- Description:
--   Calculates a cricketer's overall training attendance percentage
--   based on real records in the PARTICIPATE_IN table.
--
-- Logic:
--   Attendance % = (Count of 'Present' sessions / Total recorded sessions) * 100
--   Gracefully handles zero records by returning 0.00%.
-- =====================================================================

CREATE OR REPLACE FUNCTION calculate_attendance_pct(
    p_cricketer_id IN NUMBER
) RETURN NUMBER IS
    v_total_sessions    NUMBER := 0;
    v_present_sessions  NUMBER := 0;
    v_percentage        NUMBER(5, 2) := 0.00;
BEGIN
    -- Count total records and present attendances for the given cricketer
    SELECT
        COUNT(*),
        COUNT(CASE WHEN Attendance = 'Present' THEN 1 END)
    INTO
        v_total_sessions,
        v_present_sessions
    FROM PARTICIPATE_IN
    WHERE Cricketer_id = p_cricketer_id;

    -- Handle edge case: no attendance/participation records found
    IF v_total_sessions = 0 THEN
        RETURN 0.00;
    END IF;

    -- Calculate attendance percentage rounded to two decimal places
    v_percentage := ROUND((v_present_sessions / v_total_sessions) * 100, 2);

    RETURN v_percentage;

EXCEPTION
    WHEN OTHERS THEN
        -- Log or return 0 on unexpected database error
        RETURN 0.00;
END calculate_attendance_pct;
/

-- =====================================================================
-- TEST CALLS & VERIFICATION EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. Test function via standard SQL dual query:
SELECT
    c.Cricketer_id,
    u.Name AS Cricketer_Name,
    calculate_attendance_pct(c.Cricketer_id) AS Attendance_Percentage
FROM CRICKETER c
JOIN "USER" u ON c.User_id = u.User_id;

-- 2. Test via Anonymous PL/SQL block with DBMS_OUTPUT:
SET SERVEROUTPUT ON;
DECLARE
    v_pct NUMBER;
    v_cid NUMBER := 1;
BEGIN
    v_pct := calculate_attendance_pct(v_cid);
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('Attendance percentage for Cricketer #' || v_cid || ': ' || v_pct || '%');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------');
END;
/
*/
