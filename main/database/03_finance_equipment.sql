-- =====================================================================
-- CRICKETHUB - MODULE 3: FINANCE & EQUIPMENT
-- File: 03_finance_equipment.sql
-- Description:
--   Creates tables: EQUIPMENT and PAYMENT.
--   Enforces constraints, stock consistency, payment status tracking,
--   and demonstrates finance/equipment queries.
--
-- Notes on Schema Alignment:
--   - In EQUIPMENT: 'Total_Quantity' represents total registered assets,
--     'Quantity' represents current available in-stock items, and
--     'Availability' ('Available' / 'Unavailable') indicates if stock > 0.
--   - In PAYMENT: The ER diagram models payment as a relationship diamond
--     between Cricketer and Cricket Program. To allow flexible installment
--     schedules while preserving diagram attributes, the primary key is
--     composite (Cricketer_id, Program_id, Due_Date).
-- =====================================================================

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE PAYMENT CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE EQUIPMENT CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ---------------------------------------------------------------------
-- TABLE 7: EQUIPMENT
-- Description: Inventory of cricket gear (bats, balls, pads, bowling machines).
-- ---------------------------------------------------------------------
CREATE TABLE EQUIPMENT (
    Equipment_id    NUMBER(10)          NOT NULL,
    Equipment_name  VARCHAR2(100)       NOT NULL,
    Equipment_type  VARCHAR2(50)        NOT NULL,
    Total_Quantity  NUMBER(6)           DEFAULT 0,
    Availability    VARCHAR2(20)        DEFAULT 'Available',
    Quantity        NUMBER(6)           DEFAULT 0,
    CONSTRAINT pk_equipment PRIMARY KEY (Equipment_id),
    CONSTRAINT chk_equip_tot_qty CHECK (Total_Quantity >= 0),
    CONSTRAINT chk_equip_qty CHECK (Quantity >= 0 AND Quantity <= Total_Quantity),
    CONSTRAINT chk_equip_avail CHECK (Availability IN ('Available', 'Unavailable', 'Maintenance'))
);

-- ---------------------------------------------------------------------
-- TABLE 8: PAYMENT
-- Description: Fee records for cricketers enrolled in cricket programs.
-- ---------------------------------------------------------------------
CREATE TABLE PAYMENT (
    Cricketer_id    NUMBER(10)          NOT NULL,
    Program_id      NUMBER(10)          NOT NULL,
    Payment_Status  VARCHAR2(30)        DEFAULT 'Pending',
    Amount          NUMBER(10, 2)       NOT NULL,
    Due_Date        DATE                NOT NULL,
    Payment_Date    DATE,
    CONSTRAINT pk_payment PRIMARY KEY (Cricketer_id, Program_id, Due_Date),
    CONSTRAINT fk_payment_cricketer FOREIGN KEY (Cricketer_id) REFERENCES CRICKETER (Cricketer_id) ON DELETE CASCADE,
    CONSTRAINT fk_payment_program FOREIGN KEY (Program_id) REFERENCES CRICKET_PROGRAM (Program_id) ON DELETE CASCADE,
    CONSTRAINT chk_payment_status CHECK (Payment_Status IN ('Paid', 'Pending', 'Failed')),
    CONSTRAINT chk_payment_amount CHECK (Amount >= 0)
);

-- =====================================================================
-- MODULE-SPECIFIC ORDINARY SQL EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. INSERT new equipment item:
INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (1, 'SG English Willow Grade 1 Bat', 'Bat', 15, 'Available', 15);

-- 2. INSERT a payment record:
INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (1, 1, 'Paid', 12000.00, TO_DATE('2026-11-01', 'YYYY-MM-DD'), TO_DATE('2026-10-28', 'YYYY-MM-DD'));

-- 3. SEARCH equipment by type and availability:
SELECT Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Quantity, Availability
FROM EQUIPMENT
WHERE Availability = 'Available' AND Equipment_type = 'Bat'
ORDER BY Equipment_name;

-- 4. VIEW pending payments with player contact and program details:
SELECT u.Name AS Cricketer_Name, u.Phone, p.Program_name,
       pay.Amount, pay.Due_Date, pay.Payment_Status
FROM PAYMENT pay
JOIN CRICKETER c ON pay.Cricketer_id = c.Cricketer_id
JOIN "USER" u ON c.User_id = u.User_id
JOIN CRICKET_PROGRAM p ON pay.Program_id = p.Program_id
WHERE pay.Payment_Status = 'Pending'
ORDER BY pay.Due_Date ASC;

-- 5. AGGREGATE total collected vs pending revenue:
SELECT Payment_Status, COUNT(*) AS Total_Count, SUM(Amount) AS Total_Sum
FROM PAYMENT
GROUP BY Payment_Status;

-- 6. UPDATE payment upon successful receipt:
UPDATE PAYMENT
SET Payment_Status = 'Paid', Payment_Date = SYSDATE
WHERE Cricketer_id = 1 AND Program_id = 1 AND Payment_Status = 'Pending';
*/
