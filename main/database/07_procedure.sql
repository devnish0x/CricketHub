-- =====================================================================
-- CRICKETHUB - PL/SQL STORED PROCEDURE
-- File: 07_procedure.sql
-- Description:
--   Validates equipment stock and cricketer eligibility before issuing gear.
--
-- Coordination with Trigger (Preventing Double Inventory Update):
--   - This procedure performs pre-issue validation (valid cricketer, valid
--     equipment, stock availability, positive quantity).
--   - If validation passes, it performs an INSERT into EQUIPMENT_ISSUED.
--   - The database trigger 'trg_equipment_issue_update' (in 09_trigger.sql)
--     listens to INSERT on EQUIPMENT_ISSUED and adjusts EQUIPMENT.Quantity
--     and EQUIPMENT.Availability.
--   - To strictly PREVENT DOUBLE DEDUCTION, this procedure does NOT execute
--     a manual UPDATE on EQUIPMENT. The trigger handles physical stock deduction.
-- =====================================================================

CREATE OR REPLACE PROCEDURE issue_equipment(
    p_cricketer_id  IN  NUMBER,
    p_equipment_id  IN  NUMBER,
    p_qty           IN  NUMBER,
    p_status        OUT VARCHAR2,
    p_message       OUT VARCHAR2
) IS
    v_cricketer_exists NUMBER := 0;
    v_equip_exists     NUMBER := 0;
    v_available_qty    NUMBER := 0;
    v_availability     VARCHAR2(20);
    v_equip_name       VARCHAR2(100);
BEGIN
    -- 1. Validate requested quantity is positive
    IF p_qty IS NULL OR p_qty <= 0 THEN
        p_status  := 'ERROR';
        p_message := 'Requested quantity must be at least 1 unit.';
        RETURN;
    END IF;

    -- 2. Validate cricketer existence
    SELECT COUNT(*) INTO v_cricketer_exists
    FROM CRICKETER
    WHERE Cricketer_id = p_cricketer_id;

    IF v_cricketer_exists = 0 THEN
        p_status  := 'ERROR';
        p_message := 'Cricketer ID #' || p_cricketer_id || ' does not exist in academy records.';
        RETURN;
    END IF;

    -- 3. Validate equipment existence and check current stock
    BEGIN
        SELECT Equipment_name, Quantity, Availability
        INTO v_equip_name, v_available_qty, v_availability
        FROM EQUIPMENT
        WHERE Equipment_id = p_equipment_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            p_status  := 'ERROR';
            p_message := 'Equipment ID #' || p_equipment_id || ' not found in inventory.';
            RETURN;
    END;

    -- 4. Check if equipment is available for checkout
    IF v_availability <> 'Available' OR v_available_qty < p_qty THEN
        p_status  := 'ERROR';
        p_message := 'Insufficient stock for "' || v_equip_name || '". Requested: ' ||
                     p_qty || ', Currently in stock: ' || v_available_qty || '.';
        RETURN;
    END IF;

    -- 5. Insert issue record into EQUIPMENT_ISSUED
    -- Note: Stock deduction is delegated to trigger 'trg_equipment_issue_update'
    INSERT INTO EQUIPMENT_ISSUED (
        Cricketer_id,
        Equipment_id,
        Issue_date,
        Return_Date,
        Quantity,
        Issue_status
    ) VALUES (
        p_cricketer_id,
        p_equipment_id,
        TRUNC(SYSDATE),
        NULL,
        p_qty,
        'Issued'
    );

    p_status  := 'SUCCESS';
    p_message := 'Successfully issued ' || p_qty || ' unit(s) of "' || v_equip_name || '" to Cricketer #' || p_cricketer_id || '.';

EXCEPTION
    WHEN OTHERS THEN
        p_status  := 'ERROR';
        p_message := 'Database error during equipment checkout: ' || SQLERRM;
END issue_equipment;
/

-- =====================================================================
-- TEST CALLS & VERIFICATION EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- Test via Anonymous PL/SQL block:
SET SERVEROUTPUT ON;
DECLARE
    v_stat VARCHAR2(30);
    v_msg  VARCHAR2(255);
BEGIN
    -- Attempt checkout of 1 unit of Equipment #1 to Cricketer #1
    issue_equipment(
        p_cricketer_id => 1,
        p_equipment_id => 1,
        p_qty          => 1,
        p_status       => v_stat,
        p_message      => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Checkout Status: ' || v_stat);
    DBMS_OUTPUT.PUT_LINE('Response Message: ' || v_msg);
END;
/
*/
