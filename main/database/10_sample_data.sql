-- =====================================================================
-- CRICKETHUB - SAMPLE DATA INITIALIZATION SCRIPT
-- File: 10_sample_data.sql
-- Description:
--   Populates all 11 tables with consistent, realistic cricket academy data.
--
-- Rerun Safety:
--   This script is SAFE TO RERUN multiple times. It deletes dependent child
--   records first in proper reverse-referential order, then cleanly repopulates
--   the baseline data.
--
-- Passwords:
--   Sample users are configured with both a standard Werkzeug scrypt hash
--   and a clean fallback for password: 'password123'.
-- =====================================================================

-- ---------------------------------------------------------------------
-- STEP 1: CLEAN UP EXISTING DATA IN REVERSE DEPENDENCY ORDER
-- ---------------------------------------------------------------------
DELETE FROM PARTICIPATE_IN;
DELETE FROM EQUIPMENT_ISSUED;
DELETE FROM APPLIED_TO;
DELETE FROM PAYMENT;
DELETE FROM TRAINING_SESSION;
DELETE FROM VENUE;
DELETE FROM EQUIPMENT;
DELETE FROM CRICKET_PROGRAM;
DELETE FROM CRICKETER;
DELETE FROM TRAINER;
DELETE FROM "USER";

-- ---------------------------------------------------------------------
-- STEP 2: INSERT "USER" RECORDS (Parent of Cricketer and Trainer)
-- ---------------------------------------------------------------------
-- Common hash for 'password123':
-- scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909
INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (1, 'Kavana Admin', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Super Admin', '9876543210', 'MIT Manipal Campus, Manipal');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (2, 'Nishan Maindan', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'System User', '9876543211', 'Udupi Central, Karnataka');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (3, 'Rahul Dravid', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Trainer', '9876543212', 'Indiranagar, Bangalore');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (4, 'Zaheer Khan', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Trainer', '9876543213', 'Bandra West, Mumbai');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (5, 'Jonty Rhodes', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Trainer', '9876543214', 'Durban / Manipal Sports Club');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (6, 'Vaibhav Tamboli', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Cricketer', '9876543215', 'Hostel Block 15, MIT Manipal');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (7, 'Meghraj Hegde', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Cricketer', '9876543216', 'Sirsi / MIT Manipal');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (8, 'Shubman Gill', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Cricketer', '9876543217', 'Fazilka, Punjab');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (9, 'Smriti Mandhana', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Cricketer', '9876543218', 'Sangli, Maharashtra');

INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
VALUES (10, 'Rishabh Pant', 'scrypt:32768:8:1$Rj5G8jBN6g0ZAeR2$f5a6514a0e9252a79a8be6a2afa4d7f308121c9af87702e1ad3904dcb162240e09b1879bde2e6cf0e82d4f9ead912747edcae755a3f8bfaa8f59aff9df69d909', 'Cricketer', '9876543219', 'Roorkee, Uttarakhand');

-- ---------------------------------------------------------------------
-- STEP 3: INSERT CRICKETER RECORDS
-- ---------------------------------------------------------------------
INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
VALUES (1, TO_DATE('2002-05-14', 'YYYY-MM-DD'), 'Male', 'Right Hand Bat', 'Right Arm Fast Medium', 3, 6);

INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
VALUES (2, TO_DATE('2001-11-20', 'YYYY-MM-DD'), 'Male', 'Left Hand Bat', 'Left Arm Orthodox', 4, 7);

INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
VALUES (3, TO_DATE('1999-09-08', 'YYYY-MM-DD'), 'Male', 'Right Hand Bat', 'Right Arm Off Break', 5, 8);

INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
VALUES (4, TO_DATE('1996-07-18', 'YYYY-MM-DD'), 'Female', 'Left Hand Bat', 'Right Arm Medium', 6, 9);

INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
VALUES (5, TO_DATE('1997-10-04', 'YYYY-MM-DD'), 'Male', 'Left Hand Bat', 'Wicketkeeper Batsman', 4, 10);

-- ---------------------------------------------------------------------
-- STEP 4: INSERT TRAINER RECORDS
-- ---------------------------------------------------------------------
INSERT INTO TRAINER (Trainer_id, Specialization, Experience, Qualification, Salary, User_id)
VALUES (1, 'Top-Order Batting Technique', 16, 'BCCI Level 3 Elite Coach', 85000.00, 3);

INSERT INTO TRAINER (Trainer_id, Specialization, Experience, Qualification, Salary, User_id)
VALUES (2, 'Fast Bowling & Reverse Swing', 14, 'ICC High Performance Coach', 80000.00, 4);

INSERT INTO TRAINER (Trainer_id, Specialization, Experience, Qualification, Salary, User_id)
VALUES (3, 'Dynamic Fielding & Agility', 12, 'Cricket South Africa Level 3', 72000.00, 5);

-- ---------------------------------------------------------------------
-- STEP 5: INSERT CRICKET_PROGRAM RECORDS
-- ---------------------------------------------------------------------
INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)
VALUES (1, 'Elite Fast Bowling Academy', '3 Months');

INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)
VALUES (2, 'Modern Strokeplay & Power Hitting', '6 Months');

INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)
VALUES (3, 'Wicketkeeping & Slip Catching Clinic', '1 Month');

INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration)
VALUES (4, 'Spin Variations & Match Simulation', '3 Months');

-- ---------------------------------------------------------------------
-- STEP 6: INSERT VENUE RECORDS
-- ---------------------------------------------------------------------
INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
VALUES (1, 'End Point Main Cricket Stadium', 'MIT Manipal North Campus', 100, 'Available');

INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
VALUES (2, 'Marena Indoor Turf & Practice Nets', 'Marena Sports Complex, Manipal', 40, 'Available');

INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
VALUES (3, 'KMC Ground - Pitch 2', 'KMC Greens, Manipal', 60, 'Available');

INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
VALUES (4, 'Pavilion Practice Nets', 'Valley View Road', 25, 'Maintenance');

-- ---------------------------------------------------------------------
-- STEP 7: INSERT TRAINING_SESSION RECORDS
-- ---------------------------------------------------------------------
INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (1, TO_DATE('2026-11-02', 'YYYY-MM-DD'), '06:30 AM - 08:30 AM', 'Scheduled', 1, 1);

INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (2, TO_DATE('2026-11-02', 'YYYY-MM-DD'), '04:30 PM - 06:30 PM', 'Scheduled', 2, 2);

INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (3, TO_DATE('2026-11-03', 'YYYY-MM-DD'), '07:00 AM - 09:00 AM', 'Scheduled', 3, 1);

INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (4, TO_DATE('2026-10-28', 'YYYY-MM-DD'), '06:30 AM - 08:30 AM', 'Completed', 1, 1);

INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
VALUES (5, TO_DATE('2026-10-29', 'YYYY-MM-DD'), '04:30 PM - 06:30 PM', 'Completed', 2, 3);

-- ---------------------------------------------------------------------
-- STEP 8: INSERT EQUIPMENT RECORDS
-- ---------------------------------------------------------------------
INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (1, 'SS Ton Reserve Edition Bat', 'Bat', 10, 'Available', 8);

INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (2, 'Kookaburra Turf Regulation White Ball (Box of 6)', 'Ball', 25, 'Available', 22);

INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (3, 'SG Pro Soft Batting Legguards (Pads)', 'Protective Gear', 12, 'Available', 10);

INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (4, 'Aero P1 Batting Helmet (Titanium)', 'Helmet', 8, 'Available', 6);

INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
VALUES (5, 'Bola Professional Bowling Machine', 'Training Machine', 2, 'Available', 1);

-- ---------------------------------------------------------------------
-- STEP 9: INSERT PAYMENT RECORDS
-- ---------------------------------------------------------------------
INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (1, 1, 'Paid', 15000.00, TO_DATE('2026-10-20', 'YYYY-MM-DD'), TO_DATE('2026-10-18', 'YYYY-MM-DD'));

INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (2, 2, 'Paid', 22000.00, TO_DATE('2026-10-25', 'YYYY-MM-DD'), TO_DATE('2026-10-24', 'YYYY-MM-DD'));

INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (3, 2, 'Pending', 22000.00, TO_DATE('2026-11-05', 'YYYY-MM-DD'), NULL);

INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (4, 1, 'Paid', 15000.00, TO_DATE('2026-10-22', 'YYYY-MM-DD'), TO_DATE('2026-10-20', 'YYYY-MM-DD'));

INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
VALUES (5, 3, 'Pending', 8000.00, TO_DATE('2026-11-10', 'YYYY-MM-DD'), NULL);

-- ---------------------------------------------------------------------
-- STEP 10: INSERT APPLIED_TO RECORDS
-- ---------------------------------------------------------------------
INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (1, 1, 'Approved', TO_DATE('2026-10-10', 'YYYY-MM-DD'));

INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (2, 2, 'Approved', TO_DATE('2026-10-12', 'YYYY-MM-DD'));

INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (3, 2, 'Pending', TO_DATE('2026-10-28', 'YYYY-MM-DD'));

INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (4, 1, 'Approved', TO_DATE('2026-10-15', 'YYYY-MM-DD'));

INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (5, 3, 'Pending', TO_DATE('2026-10-29', 'YYYY-MM-DD'));

INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
VALUES (1, 2, 'Pending', TO_DATE('2026-10-30', 'YYYY-MM-DD'));

-- ---------------------------------------------------------------------
-- STEP 11: INSERT EQUIPMENT_ISSUED RECORDS
-- ---------------------------------------------------------------------
INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (1, 1, TO_DATE('2026-10-25', 'YYYY-MM-DD'), TO_DATE('2026-10-26', 'YYYY-MM-DD'), 1, 'Returned');

INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (1, 1, TO_DATE('2026-10-28', 'YYYY-MM-DD'), NULL, 2, 'Issued');

INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (2, 2, TO_DATE('2026-10-29', 'YYYY-MM-DD'), NULL, 3, 'Issued');

INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (3, 3, TO_DATE('2026-10-27', 'YYYY-MM-DD'), NULL, 2, 'Issued');

INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (4, 4, TO_DATE('2026-10-24', 'YYYY-MM-DD'), NULL, 2, 'Issued');

INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Return_Date, Quantity, Issue_status)
VALUES (5, 5, TO_DATE('2026-10-20', 'YYYY-MM-DD'), NULL, 1, 'Issued');

-- ---------------------------------------------------------------------
-- STEP 12: INSERT PARTICIPATE_IN RECORDS
-- ---------------------------------------------------------------------
INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (1, 4, '2 Hours', 'Present');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (2, 4, '2 Hours', 'Present');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (3, 4, '2 Hours', 'Absent');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (4, 4, '2 Hours', 'Present');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (1, 5, '2 Hours', 'Present');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (2, 5, '2 Hours', 'Excused');

INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
VALUES (4, 5, '2 Hours', 'Present');

COMMIT;
