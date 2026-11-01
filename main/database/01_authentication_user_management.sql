-- =====================================================================
-- CRICKETHUB - MODULE 1: AUTHENTICATION & USER MANAGEMENT
-- File: 01_authentication_user_management.sql
-- Description:
--   Creates tables: "USER", CRICKETER, TRAINER with exact ER diagram
--   entities, attributes, and integrity constraints.
--
-- Note on Oracle Reserved Word:
--   'USER' is an Oracle reserved pseudo-column / keyword.
--   To strictly preserve the ER diagram entity name without modification,
--   the table is defined using double quotes as "USER".
--   In all SQL statements and repository queries, reference it as "USER".
--
-- Note on Diagram Typo / Formatting:
--   Attributes "Batting-Style" and "Bowling-Style" in CRICKETER contain
--   hyphens as drawn in the ER diagram; in Oracle SQL they are enclosed
--   in double quotes ("Batting-Style", "Bowling-Style").
--   In TRAINER, the ER diagram spelled 'Qualifiaction', standardized
--   to 'Qualification' in the relational schema.
-- =====================================================================

-- Drop child tables first, then parent table
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE CRICKETER CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE TRAINER CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE "USER" CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ---------------------------------------------------------------------
-- TABLE 1: "USER"
-- Description: Core authentication entity holding credentials & roles.
-- ---------------------------------------------------------------------
CREATE TABLE "USER" (
    User_id     NUMBER(10)          NOT NULL,
    Name        VARCHAR2(100)       NOT NULL,
    Password    VARCHAR2(255)       NOT NULL,
    Role        VARCHAR2(30)        NOT NULL,
    Phone       VARCHAR2(20),
    Address     VARCHAR2(255),
    CONSTRAINT pk_user PRIMARY KEY (User_id),
    CONSTRAINT chk_user_role CHECK (Role IN ('Super Admin', 'System User', 'Trainer', 'Cricketer'))
);

-- ---------------------------------------------------------------------
-- TABLE 2: CRICKETER
-- Description: Cricketer-specific profile linked 1:1 with "USER".
-- ---------------------------------------------------------------------
CREATE TABLE CRICKETER (
    Cricketer_id    NUMBER(10)          NOT NULL,
    DOB             DATE,
    Gender          VARCHAR2(10),
    "Batting-Style" VARCHAR2(30),
    "Bowling-Style" VARCHAR2(30),
    Experience      NUMBER(3)           DEFAULT 0,
    User_id         NUMBER(10)          NOT NULL,
    CONSTRAINT pk_cricketer PRIMARY KEY (Cricketer_id),
    CONSTRAINT uq_cricketer_user UNIQUE (User_id),
    CONSTRAINT fk_cricketer_user FOREIGN KEY (User_id) REFERENCES "USER" (User_id) ON DELETE CASCADE,
    CONSTRAINT chk_cricketer_gender CHECK (Gender IN ('Male', 'Female', 'Other')),
    CONSTRAINT chk_cricketer_exp CHECK (Experience >= 0)
);

-- ---------------------------------------------------------------------
-- TABLE 3: TRAINER
-- Description: Coach/trainer profile linked 1:1 with "USER".
-- ---------------------------------------------------------------------
CREATE TABLE TRAINER (
    Trainer_id      NUMBER(10)          NOT NULL,
    Specialization  VARCHAR2(100),
    Experience      NUMBER(3)           DEFAULT 0,
    Qualification   VARCHAR2(100),
    Salary          NUMBER(10, 2)       DEFAULT 0.00,
    User_id         NUMBER(10)          NOT NULL,
    CONSTRAINT pk_trainer PRIMARY KEY (Trainer_id),
    CONSTRAINT uq_trainer_user UNIQUE (User_id),
    CONSTRAINT fk_trainer_user FOREIGN KEY (User_id) REFERENCES "USER" (User_id) ON DELETE CASCADE,
    CONSTRAINT chk_trainer_exp CHECK (Experience >= 0),
    CONSTRAINT chk_trainer_salary CHECK (Salary >= 0)
);

-- =====================================================================
-- MODULE-SPECIFIC ORDINARY SQL EXAMPLES (COMMENTED FOR ACADEMIC VIVA)
-- =====================================================================

/*
-- 1. INSERT a new user and corresponding cricketer:
INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (101, 'Rahul Dravid', 'scrypt:32768:8:1$hashedpassword', 'Trainer', '9876543210', 'Bangalore, India');

INSERT INTO TRAINER (Trainer_id, Specialization, Experience, Qualification, Salary, User_id)
VALUES (1, 'Batting & Mentorship', 15, 'BCCI Level 3 Certified', 75000.00, 101);

-- 2. SELECT with WHERE filtering:
SELECT User_id, Name, Role, Phone FROM "USER" WHERE Role = 'Cricketer';

-- 3. JOIN between "USER" and CRICKETER to view complete player profile:
SELECT u.User_id, u.Name, u.Phone, u.Address,
       c.Cricketer_id, c.DOB, c.Gender, c."Batting-Style", c."Bowling-Style", c.Experience
FROM "USER" u
JOIN CRICKETER c ON u.User_id = c.User_id
ORDER BY c.Cricketer_id;

-- 4. JOIN between "USER" and TRAINER to view complete trainer profile:
SELECT u.User_id, u.Name, u.Phone,
       t.Trainer_id, t.Specialization, t.Experience, t.Qualification, t.Salary
FROM "USER" u
JOIN TRAINER t ON u.User_id = t.User_id
ORDER BY t.Trainer_id;

-- 5. UPDATE player experience:
UPDATE CRICKETER
SET Experience = Experience + 1
WHERE Cricketer_id = 1;

-- 6. Safe DELETE (child first or using ON DELETE CASCADE):
DELETE FROM "USER" WHERE User_id = 999;
*/
