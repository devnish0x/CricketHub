-- =====================================================================
-- CRICKETHUB - MODULE 2: TRAINING MANAGEMENT
-- File: 02_training_management.sql
-- Description:
--   Creates tables: CRICKET_PROGRAM, VENUE, TRAINING_SESSION.
--   Enforces foreign keys, data constraints, and demonstrates basic
--   queries for management, search, and scheduling.
--
-- Notes on Schema Alignment:
--   - ER Diagram entity "Crikcekt Program" is normalized to CRICKET_PROGRAM.
--   - ER Diagram entity "Venu" corresponds to VENUE, retaining exact
--     diagram attribute names Venu_id, Venu_name, Location, Capacity, Availability.
--   - ER Diagram entity "Traning Session" corresponds to TRAINING_SESSION.
-- =====================================================================

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE TRAINING_SESSION CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE VENUE CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE CRICKET_PROGRAM CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ---------------------------------------------------------------------
-- TABLE 4: CRICKET_PROGRAM
-- Description: Available training regimens (e.g. Fast Bowling Camp).
-- ---------------------------------------------------------------------
CREATE TABLE CRICKET_PROGRAM (
    Program_id      NUMBER(10)          NOT NULL,
    Program_name    VARCHAR2(100)       NOT NULL,
    Duration        VARCHAR2(50)        NOT NULL,
    CONSTRAINT pk_cricket_program PRIMARY KEY (Program_id),
    CONSTRAINT uq_program_name UNIQUE (Program_name)
);

-- ---------------------------------------------------------------------
-- TABLE 5: VENUE
-- Description: Practice nets, main stadiums, indoor facilities.
-- ---------------------------------------------------------------------
CREATE TABLE VENUE (
    Venu_id         NUMBER(10)          NOT NULL,
    Venu_name       VARCHAR2(100)       NOT NULL,
    Location        VARCHAR2(100)       NOT NULL,
    Capacity        NUMBER(6)           DEFAULT 50,
    Availability    VARCHAR2(20)        DEFAULT 'Available',
    CONSTRAINT pk_venue PRIMARY KEY (Venu_id),
    CONSTRAINT chk_venue_capacity CHECK (Capacity > 0),
    CONSTRAINT chk_venue_avail CHECK (Availability IN ('Available', 'Unavailable', 'Maintenance'))
);

-- ---------------------------------------------------------------------
-- TABLE 6: TRAINING_SESSION
-- Description: Scheduled training slot conducted by a Trainer at a Venue.
-- ---------------------------------------------------------------------
CREATE TABLE TRAINING_SESSION (
    Session_id      NUMBER(10)          NOT NULL,
    Session_date    DATE                NOT NULL,
    Session_time    VARCHAR2(20)        NOT NULL,
    Status          VARCHAR2(30)        DEFAULT 'Scheduled',
    Trainer_id      NUMBER(10)          NOT NULL,
    Venu_id         NUMBER(10)          NOT NULL,
    CONSTRAINT pk_training_session PRIMARY KEY (Session_id),
    CONSTRAINT fk_session_trainer FOREIGN KEY (Trainer_id) REFERENCES TRAINER (Trainer_id) ON DELETE CASCADE,
    CONSTRAINT fk_session_venue FOREIGN KEY (Venu_id) REFERENCES VENUE (Venu_id) ON DELETE CASCADE,
    CONSTRAINT chk_session_status CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- =====================================================================
-- MODULE-SPECIFIC ORDINARY SQL EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. INSERT a cricket program:
INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)
VALUES (1, 'Fast Bowling Excellence', '3 Months');

-- 2. INSERT a venue:
INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
VALUES (1, 'Main Turf Nets - Oval A', 'North Wing Ground', 25, 'Available');

-- 3. INSERT a training session:
INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (1, TO_DATE('2026-11-05', 'YYYY-MM-DD'), '06:30 AM - 08:30 AM', 'Scheduled', 1, 1);

-- 4. VIEW & SEARCH training sessions with joined trainer and venue names:
SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
       u.Name AS Trainer_Name, t.Specialization,
       v.Venu_name, v.Location
FROM TRAINING_SESSION s
JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
JOIN "USER" u ON t.User_id = u.User_id
JOIN VENUE v ON s.Venu_id = v.Venu_id
WHERE s.Status = 'Scheduled'
ORDER BY s.Session_date, s.Session_time;

-- 5. UPDATE session status:
UPDATE TRAINING_SESSION
SET Status = 'Completed'
WHERE Session_id = 1;

-- 6. Safe DELETE of a session:
DELETE FROM TRAINING_SESSION WHERE Session_id = 999;
*/
