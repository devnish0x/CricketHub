-- =====================================================================
-- CRICKETHUB - PL/SQL DATABASE TRIGGER
-- File: 09_trigger.sql
-- Description:
--   Automatically synchronizes EQUIPMENT inventory stock and availability
--   status whenever gear is checked out, returned, or cancelled in EQUIPMENT_ISSUED.
--
-- Column Semantics (ER Diagram Alignment):
--   - Total_Quantity : Permanent master tally of assets owned by the academy.
--   - Quantity       : Dynamic current count of gear available in the store room.
--   - Availability   : Categorical indicator ('Available' / 'Unavailable').
--
-- Coordination with Procedure 'issue_equipment' (07_procedure.sql):
--   - Procedure handles pre-validation (valid user, valid item, sufficient stock)
--     and executes INSERT into EQUIPMENT_ISSUED.
--   - This trigger executes AFTER INSERT / UPDATE / DELETE on EQUIPMENT_ISSUED
--     and performs the physical stock increment / decrement.
--   - Because stock update is encapsulated in this trigger, procedures and
--     application queries NEVER execute manual stock deductions, completely
--     eliminating the risk of double inventory updates!
-- =====================================================================

CREATE OR REPLACE TRIGGER trg_equipment_issue_update
AFTER INSERT OR UPDATE OR DELETE ON EQUIPMENT_ISSUED
FOR EACH ROW
BEGIN
    -- -----------------------------------------------------------------
    -- CASE 1: NEW EQUIPMENT CHECKOUT (INSERT)
    -- Deduct issued quantity from on-shelf stock.
    -- -----------------------------------------------------------------
    IF INSERTING THEN
        IF :NEW.Issue_status = 'Issued' THEN
            UPDATE EQUIPMENT
            SET Quantity = GREATEST(Quantity - :NEW.Quantity, 0),
                Availability = CASE
                    WHEN (Quantity - :NEW.Quantity) <= 0 THEN 'Unavailable'
                    ELSE 'Available'
                END
            WHERE Equipment_id = :NEW.Equipment_id;
        END IF;

    -- -----------------------------------------------------------------
    -- CASE 2: GEAR RETURNED (UPDATE)
    -- Restore quantity back to on-shelf stock.
    -- -----------------------------------------------------------------
    ELSIF UPDATING THEN
        -- From 'Issued' to 'Returned'
        IF :OLD.Issue_status = 'Issued' AND :NEW.Issue_status = 'Returned' THEN
            UPDATE EQUIPMENT
            SET Quantity = LEAST(Quantity + :OLD.Quantity, Total_Quantity),
                Availability = 'Available'
            WHERE Equipment_id = :NEW.Equipment_id;

        -- If quantity issued was modified while still in 'Issued' status
        ELSIF :OLD.Issue_status = 'Issued' AND :NEW.Issue_status = 'Issued' AND :OLD.Quantity <> :NEW.Quantity THEN
            UPDATE EQUIPMENT
            SET Quantity = GREATEST(Quantity + :OLD.Quantity - :NEW.Quantity, 0),
                Availability = CASE
                    WHEN (Quantity + :OLD.Quantity - :NEW.Quantity) <= 0 THEN 'Unavailable'
                    ELSE 'Available'
                END
            WHERE Equipment_id = :NEW.Equipment_id;
        END IF;

    -- -----------------------------------------------------------------
    -- CASE 3: RECORD DELETED (DELETE)
    -- If an unreturned issue record is deleted, replenish stock safely.
    -- -----------------------------------------------------------------
    ELSIF DELETING THEN
        IF :OLD.Issue_status = 'Issued' THEN
            UPDATE EQUIPMENT
            SET Quantity = LEAST(Quantity + :OLD.Quantity, Total_Quantity),
                Availability = 'Available'
            WHERE Equipment_id = :OLD.Equipment_id;
        END IF;
    END IF;

END trg_equipment_issue_update;
/

-- =====================================================================
-- TRIGGER VERIFICATION & TESTING STEPS (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. Check baseline stock for Equipment #1:
SELECT Equipment_id, Equipment_name, Total_Quantity, Quantity, Availability
FROM EQUIPMENT WHERE Equipment_id = 1;

-- 2. Insert test issue row (simulate gear checkout):
INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Quantity, Issue_status)
VALUES (1, 1, SYSDATE, 2, 'Issued');

-- 3. Verify stock decreased by 2:
SELECT Equipment_id, Equipment_name, Quantity, Availability
FROM EQUIPMENT WHERE Equipment_id = 1;

-- 4. Mark gear as returned:
UPDATE EQUIPMENT_ISSUED
SET Issue_status = 'Returned', Return_Date = SYSDATE
WHERE Cricketer_id = 1 AND Equipment_id = 1 AND Issue_status = 'Issued';

-- 5. Verify stock restored to original level:
SELECT Equipment_id, Equipment_name, Quantity, Availability
FROM EQUIPMENT WHERE Equipment_id = 1;
*/
