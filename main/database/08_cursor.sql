-- =====================================================================
-- CRICKETHUB - PL/SQL EXPLICIT CURSOR DEMONSTRATION
-- File: 08_cursor.sql
-- Description:
--   Demonstrates the complete lifecycle of a PL/SQL explicit cursor:
--     1. DECLARATION: Cursor definition with multi-table join query
--     2. OPENING: Memory allocation and query execution
--     3. FETCHING: Row-by-row retrieval into PL/SQL variables/records
--     4. LOOP & EXIT: Evaluating cursor attributes (%FOUND, %NOTFOUND, %ROWCOUNT)
--     5. CLOSING: Releasing context area resources
-- =====================================================================

SET SERVEROUTPUT ON SIZE 1000000;

DECLARE
    -- =================================================================
    -- STEP 1: EXPLICIT CURSOR DECLARATION
    -- Identifies pending payments joined with cricketer name, phone,
    -- and program name.
    -- =================================================================
    CURSOR cur_pending_payments IS
        SELECT
            c.Cricketer_id,
            u.Name             AS Cricketer_Name,
            u.Phone            AS Contact_Number,
            cp.Program_name    AS Enrolled_Program,
            p.Amount           AS Due_Amount,
            p.Due_Date         AS Payment_Deadline,
            p.Payment_Status   AS Current_Status
        FROM PAYMENT p
        JOIN CRICKETER c       ON p.Cricketer_id = c.Cricketer_id
        JOIN "USER" u          ON c.User_id = u.User_id
        JOIN CRICKET_PROGRAM cp ON p.Program_id = cp.Program_id
        WHERE p.Payment_Status = 'Pending'
        ORDER BY p.Due_Date ASC;

    -- Record variable matching cursor row structure
    v_rec cur_pending_payments%ROWTYPE;

    -- Running tally accumulators
    v_total_pending_count NUMBER := 0;
    v_total_pending_amt   NUMBER(12, 2) := 0.00;

BEGIN
    DBMS_OUTPUT.PUT_LINE('==============================================================================');
    DBMS_OUTPUT.PUT_LINE('             CRICKETHUB ACADEMY - OUTSTANDING FEES AUDIT REPORT               ');
    DBMS_OUTPUT.PUT_LINE('==============================================================================');
    DBMS_OUTPUT.PUT_LINE(
        RPAD('ID', 5) || ' ' ||
        RPAD('Player Name', 22) || ' ' ||
        RPAD('Program', 24) || ' ' ||
        RPAD('Due Date', 12) || ' ' ||
        LPAD('Amount (INR)', 12)
    );
    DBMS_OUTPUT.PUT_LINE('------------------------------------------------------------------------------');

    -- =================================================================
    -- STEP 2: OPENING THE CURSOR
    -- Evaluates the query and sets the active result set pointer.
    -- =================================================================
    IF NOT cur_pending_payments%ISOPEN THEN
        OPEN cur_pending_payments;
    END IF;

    -- =================================================================
    -- STEP 3: FETCHING ROWS IN A LOOP
    -- Iteratively transfers the current row from the cursor into v_rec.
    -- =================================================================
    LOOP
        FETCH cur_pending_payments INTO v_rec;

        -- =============================================================
        -- STEP 4: LOOP EXIT CONDITION
        -- When all rows have been fetched, %NOTFOUND becomes TRUE.
        -- =============================================================
        EXIT WHEN cur_pending_payments%NOTFOUND;

        -- Accumulate totals
        v_total_pending_count := v_total_pending_count + 1;
        v_total_pending_amt   := v_total_pending_amt + v_rec.Due_Amount;

        -- Format output line
        DBMS_OUTPUT.PUT_LINE(
            RPAD(TO_CHAR(v_rec.Cricketer_id), 5) || ' ' ||
            RPAD(SUBSTR(v_rec.Cricketer_Name, 1, 22), 22) || ' ' ||
            RPAD(SUBSTR(v_rec.Enrolled_Program, 1, 24), 24) || ' ' ||
            RPAD(TO_CHAR(v_rec.Payment_Deadline, 'DD-MON-YYYY'), 12) || ' ' ||
            LPAD(TO_CHAR(v_rec.Due_Amount, '999,990.00'), 12)
        );
    END LOOP;

    -- =================================================================
    -- STEP 5: CLOSING THE CURSOR
    -- Always close explicitly opened cursors to release cursor memory!
    -- =================================================================
    IF cur_pending_payments%ISOPEN THEN
        CLOSE cur_pending_payments;
    END IF;

    DBMS_OUTPUT.PUT_LINE('------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('SUMMARY:');
    DBMS_OUTPUT.PUT_LINE('  Total Pending Invoices : ' || v_total_pending_count);
    DBMS_OUTPUT.PUT_LINE('  Total Overdue Amount   : INR ' || TO_CHAR(v_total_pending_amt, '999,990.00'));
    DBMS_OUTPUT.PUT_LINE('==============================================================================');

EXCEPTION
    WHEN OTHERS THEN
        -- Defensive cleanup: ensure cursor is closed in case of exception
        IF cur_pending_payments%ISOPEN THEN
            CLOSE cur_pending_payments;
        END IF;
        DBMS_OUTPUT.PUT_LINE('Error executing cursor audit: ' || SQLERRM);
END;
/
