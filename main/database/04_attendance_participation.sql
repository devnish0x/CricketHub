-- =====================================================================
-- CRICKETHUB - MODULE 4: ATTENDANCE & PARTICIPATION
-- File: 04_attendance_participation.sql
-- Description:
--   Creates relationship tables: APPLIED_TO, EQUIPMENT_ISSUED, PARTICIPATE_IN.
--   Enforces multi-table foreign keys and attendance tracking.
--
-- EXECUTION ORDER DOCUMENTATION:
--   The schema scripts must be executed in this exact order:
--     1. 01_authentication_user_management.sql (Creates "USER", CRICKETER, TRAINER)
--     2. 02_training_management.sql (Creates CRICKET_PROGRAM, VENUE, TRAINING_SESSION)
--     3. 03_finance_equipment.sql (Creates EQUIPMENT, PAYMENT)
--     4. 04_attendance_participation.sql (Creates APPLIED_TO, EQUIPMENT_ISSUED, PARTICIPATE_IN)
--   This ensures that all parent primary keys exist before dependent foreign
--   keys are referenced.
--
-- Notes on Schema Alignment:
--   - In PARTICIPATE_IN: The ER diagram written attribute is "Attendence"
--     (standardized to "Attendance" in relational schema PDF).
--   - In EQUIPMENT_ISSUED: The primary key is composite (Cricketer_id, Equipment_id, Issue_date)
--     allowing a cricketer to borrow the same item on different dates.
-- =====================================================================

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE PARTICIPATE_IN CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE EQUIPMENT_ISSUED CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE APPLIED_TO CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ---------------------------------------------------------------------
-- TABLE 9: APPLIED_TO
-- Description: Cricketer applications for enrollment in cricket programs.
-- ---------------------------------------------------------------------
CREATE TABLE APPLIED_TO (
    Cricketer_id    NUMBER(10)          NOT NULL,
    Program_id      NUMBER(10)          NOT NULL,
    Applied_status  VARCHAR2(30)        DEFAULT 'Pending',
    Applied_date    DATE                DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_applied_to PRIMARY KEY (Cricketer_id, Program_id),
    CONSTRAINT fk_applied_cricketer FOREIGN KEY (Cricketer_id) REFERENCES CRICKETER (Cricketer_id) ON DELETE CASCADE,
    CONSTRAINT fk_applied_program FOREIGN KEY (Program_id) REFERENCES CRICKET_PROGRAM (Program_id) ON DELETE CASCADE,
    CONSTRAINT chk_applied_status CHECK (Applied_status IN ('Pending', 'Approved', 'Rejected'))
);

-- ---------------------------------------------------------------------
-- TABLE 10: EQUIPMENT_ISSUED
-- Description: Gear borrowed by cricketers for net practice or matches.
-- ---------------------------------------------------------------------
CREATE TABLE EQUIPMENT_ISSUED (
    Cricketer_id    NUMBER(10)          NOT NULL,
    Equipment_id    NUMBER(10)          NOT NULL,
    Issue_date      DATE                DEFAULT SYSDATE NOT NULL,
    Return_Date     DATE,
    Quantity        NUMBER(6)           DEFAULT 1,
    Issue_status    VARCHAR2(30)        DEFAULT 'Issued',
    CONSTRAINT pk_equipment_issued PRIMARY KEY (Cricketer_id, Equipment_id, Issue_date),
    CONSTRAINT fk_eq_issue_cricketer FOREIGN KEY (Cricketer_id) REFERENCES CRICKETER (Cricketer_id) ON DELETE CASCADE,
    CONSTRAINT fk_eq_issue_equipment FOREIGN KEY (Equipment_id) REFERENCES EQUIPMENT (Equipment_id) ON DELETE CASCADE,
    CONSTRAINT chk_eq_issue_qty CHECK (Quantity > 0),
    CONSTRAINT chk_eq_issue_status CHECK (Issue_status IN ('Issued', 'Returned', 'Overdue'))
);

-- ---------------------------------------------------------------------
-- TABLE 11: PARTICIPATE_IN
-- Description: Player attendance and participation record in scheduled sessions.
-- ---------------------------------------------------------------------
CREATE TABLE PARTICIPATE_IN (
    Cricketer_id        NUMBER(10)          NOT NULL,
    Session_id          NUMBER(10)          NOT NULL,
    Participation_time  VARCHAR2(20)        DEFAULT '2 Hours',
    Attendance          VARCHAR2(20)        DEFAULT 'Present',
    CONSTRAINT pk_participate_in PRIMARY KEY (Cricketer_id, Session_id),
    CONSTRAINT fk_part_cricketer FOREIGN KEY (Cricketer_id) REFERENCES CRICKETER (Cricketer_id) ON DELETE CASCADE,
    CONSTRAINT fk_part_session FOREIGN KEY (Session_id) REFERENCES TRAINING_SESSION (Session_id) ON DELETE CASCADE,
    CONSTRAINT chk_part_attendance CHECK (Attendance IN ('Present', 'Absent', 'Excused'))
);

-- =====================================================================
-- MODULE-SPECIFIC ORDINARY SQL EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. APPLY a cricketer for a program:
INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (1, 1, 'Pending', TO_DATE('2026-10-25', 'YYYY-MM-DD'));

-- 2. ISSUE equipment to a cricketer:
INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Quantity, Issue_status)
VALUES (1, 1, TO_DATE('2026-10-30', 'YYYY-MM-DD'), 1, 'Issued');

-- 3. RECORD participation/attendance in a training session:
INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (1, 1, '2 Hours', 'Present');

-- 4. VIEW program applications with applicant player name and program name:
SELECT u.Name AS Cricketer_Name, u.Phone, p.Program_name, a.Applied_date, a.Applied_status
FROM APPLIED_TO a
JOIN CRICKETER c ON a.Cricketer_id = c.Cricketer_id
JOIN "USER" u ON c.User_id = u.User_id
JOIN CRICKET_PROGRAM p ON a.Program_id = p.Program_id
ORDER BY a.Applied_date DESC;

-- 5. VIEW active gear checkouts with borrower details:
SELECT u.Name AS Borrower_Name, eq.Equipment_name, eq.Equipment_type,
       ei.Issue_date, ei.Quantity, ei.Issue_status
FROM EQUIPMENT_ISSUED ei
JOIN CRICKETER c ON ei.Cricketer_id = c.Cricketer_id
JOIN "USER" u ON c.User_id = u.User_id
JOIN EQUIPMENT eq ON ei.Equipment_id = eq.Equipment_id
WHERE ei.Issue_status = 'Issued';

-- 6. VIEW session roster and attendance:
SELECT s.Session_id, s.Session_date, s.Session_time,
       u.Name AS Cricketer_Name, pi.Attendance, pi.Participation_time
FROM PARTICIPATE_IN pi
JOIN CRICKETER c ON pi.Cricketer_id = c.Cricketer_id
JOIN "USER" u ON c.User_id = u.User_id
JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
ORDER BY s.Session_date DESC, u.Name;
*/
