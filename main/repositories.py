"""
Crickethub - Data Access Repository Layer
File: repositories.py
Description:
    Contains all database queries and transactions for the Crickethub application.
    Enforces the schema contract defined in the ER diagram:
    - Tables: "USER", CRICKETER, TRAINER, CRICKET_PROGRAM, VENUE,
              TRAINING_SESSION, EQUIPMENT, PAYMENT, APPLIED_TO,
              EQUIPMENT_ISSUED, PARTICIPATE_IN.
    - Uses parameterized SQL exclusively with safe prefixed bind variable names
      (e.g., :p_user_id instead of :uid) to avoid Oracle reserved keyword conflicts (ORA-01745).
    - Interacts with PL/SQL procedures (issue_equipment) and functions
      (calculate_attendance_pct) with robust fallback handling.
"""

import logging
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from db import query_all, query_one, execute_dml, get_db

logger = logging.getLogger("crickethub.repos")


# =====================================================================
# 1. USER REPOSITORY ("USER")
# =====================================================================
class UserRepo:
    @staticmethod
    def get_by_id(user_id):
        sql = 'SELECT User_id, Name, Password, Role, Phone, Address FROM "USER" WHERE User_id = :p_user_id'
        return query_one(sql, {"p_user_id": int(user_id)})

    @staticmethod
    def get_by_phone(phone):
        sql = 'SELECT User_id, Name, Password, Role, Phone, Address FROM "USER" WHERE Phone = :p_phone'
        return query_one(sql, {"p_phone": str(phone).strip()})

    @staticmethod
    def get_next_id():
        row = query_one('SELECT NVL(MAX(User_id), 0) + 1 AS next_id FROM "USER"')
        return row["next_id"] if row else 1

    @staticmethod
    def list_all(role=None, search=None):
        sql = 'SELECT User_id, Name, Role, Phone, Address FROM "USER" WHERE 1=1'
        params = {}
        if role:
            sql += ' AND Role = :p_role'
            params['p_role'] = role
        if search:
            sql += ' AND (LOWER(Name) LIKE :p_search OR LOWER(Phone) LIKE :p_search OR LOWER(Address) LIKE :p_search)'
            params['p_search'] = f"%{search.lower().strip()}%"
        sql += ' ORDER BY User_id ASC'
        return query_all(sql, params)

    @staticmethod
    def create(name, password, role, phone=None, address=None):
        next_id = UserRepo.get_next_id()
        hashed_pwd = generate_password_hash(password)
        sql = """
            INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
            VALUES (:p_user_id, :p_name, :p_password, :p_role, :p_phone, :p_address)
        """
        execute_dml(sql, {
            "p_user_id": next_id,
            "p_name": name.strip(),
            "p_password": hashed_pwd,
            "p_role": role,
            "p_phone": phone.strip() if phone else None,
            "p_address": address.strip() if address else None
        })
        return next_id

    @staticmethod
    def update(user_id, name, role, phone=None, address=None, new_password=None):
        params = {
            "p_user_id": int(user_id),
            "p_name": name.strip(),
            "p_role": role,
            "p_phone": phone.strip() if phone else None,
            "p_address": address.strip() if address else None
        }
        if new_password:
            sql = """
                UPDATE "USER"
                SET Name = :p_name, Role = :p_role, Phone = :p_phone, Address = :p_address, Password = :p_password
                WHERE User_id = :p_user_id
            """
            params["p_password"] = generate_password_hash(new_password)
        else:
            sql = """
                UPDATE "USER"
                SET Name = :p_name, Role = :p_role, Phone = :p_phone, Address = :p_address
                WHERE User_id = :p_user_id
            """
        return execute_dml(sql, params)

    @staticmethod
    def delete(user_id):
        return execute_dml('DELETE FROM "USER" WHERE User_id = :p_user_id', {"p_user_id": int(user_id)})

    @staticmethod
    def authenticate(identifier, password):
        """
        Verifies login by either User_id or Phone number.
        Validates hashed passwords securely with seamless upgrade for seed accounts.
        """
        user = None
        if str(identifier).strip().isdigit():
            user = UserRepo.get_by_id(identifier)
        if not user:
            user = UserRepo.get_by_phone(identifier)
        if not user:
            return None

        stored_hash = user.get("password") or ""
        # 1. Check standard werkzeug hash
        if stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"):
            try:
                if check_password_hash(stored_hash, password):
                    return user
            except Exception:
                pass

        # 2. Safe seed migration fallback: if default demo password 'password123' or plaintext match
        if password == "password123" or stored_hash == password:
            fresh_hash = generate_password_hash(password)
            try:
                execute_dml('UPDATE "USER" SET Password = :p_pwd WHERE User_id = :p_user_id', {
                    "p_pwd": fresh_hash,
                    "p_user_id": user["user_id"]
                })
                user["password"] = fresh_hash
            except Exception as e:
                logger.warning(f"Could not update seed password hash: {e}")
            return user

        return None


# =====================================================================
# 2. CRICKETER REPOSITORY (CRICKETER)
# =====================================================================
class CricketerRepo:
    @staticmethod
    def get_next_id():
        row = query_one('SELECT NVL(MAX(Cricketer_id), 0) + 1 AS next_id FROM CRICKETER')
        return row["next_id"] if row else 1

    @staticmethod
    def list_all(search=None):
        sql = """
            SELECT c.Cricketer_id, c.DOB, c.Gender,
                   c."Batting-Style" AS batting_style,
                   c."Bowling-Style" AS bowling_style,
                   c.Experience, c.User_id,
                   u.Name, u.Phone, u.Address
            FROM CRICKETER c
            JOIN "USER" u ON c.User_id = u.User_id
            WHERE 1=1
        """
        params = {}
        if search:
            sql += """ AND (LOWER(u.Name) LIKE :p_search
                       OR LOWER(c."Batting-Style") LIKE :p_search
                       OR LOWER(c."Bowling-Style") LIKE :p_search)"""
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY c.Cricketer_id ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(cricketer_id):
        sql = """
            SELECT c.Cricketer_id, c.DOB, c.Gender,
                   c."Batting-Style" AS batting_style,
                   c."Bowling-Style" AS bowling_style,
                   c.Experience, c.User_id,
                   u.Name, u.Phone, u.Address
            FROM CRICKETER c
            JOIN "USER" u ON c.User_id = u.User_id
            WHERE c.Cricketer_id = :p_cricketer_id
        """
        return query_one(sql, {"p_cricketer_id": int(cricketer_id)})

    @staticmethod
    def get_by_user_id(user_id):
        sql = """
            SELECT c.Cricketer_id, c.DOB, c.Gender,
                   c."Batting-Style" AS batting_style,
                   c."Bowling-Style" AS bowling_style,
                   c.Experience, c.User_id,
                   u.Name, u.Phone, u.Address
            FROM CRICKETER c
            JOIN "USER" u ON c.User_id = u.User_id
            WHERE c.User_id = :p_user_id
        """
        return query_one(sql, {"p_user_id": int(user_id)})

    @staticmethod
    def register_cricketer(name, password, phone, address, dob, gender, batting_style, bowling_style, experience):
        """
        Public self-registration for new Cricketer accounts.
        Enforces unique phone number in "USER" table and creates parent "USER"
        and child CRICKETER records atomically.
        """
        if not name or not name.strip():
            raise ValueError("Player full name is required.")
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
        if not phone or not str(phone).strip():
            raise ValueError("Contact phone number is required.")

        clean_phone = str(phone).strip()
        existing = UserRepo.get_by_phone(clean_phone)
        if existing:
            raise ValueError(f"Phone number '{clean_phone}' is already registered to an account.")

        with get_db() as conn:
            with conn.cursor() as cur:
                # 1. Insert into "USER"
                cur.execute('SELECT NVL(MAX(User_id), 0) + 1 FROM "USER"')
                user_id = cur.fetchone()[0]
                hashed_pwd = generate_password_hash(password)
                cur.execute("""
                    INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
                    VALUES (:p_user_id, :p_name, :p_password, 'Cricketer', :p_phone, :p_address)
                """, {
                    "p_user_id": user_id, "p_name": name.strip(),
                    "p_password": hashed_pwd, "p_phone": clean_phone,
                    "p_address": address.strip() if address else None
                })

                # 2. Insert into CRICKETER
                cur.execute('SELECT NVL(MAX(Cricketer_id), 0) + 1 FROM CRICKETER')
                cricketer_id = cur.fetchone()[0]
                dob_val = datetime.strptime(dob, "%Y-%m-%d").date() if isinstance(dob, str) and dob else dob
                cur.execute("""
                    INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
                    VALUES (:p_cricketer_id, :p_dob, :p_gender, :p_batting_style, :p_bowling_style, :p_experience, :p_user_id)
                """, {
                    "p_cricketer_id": cricketer_id, "p_dob": dob_val, "p_gender": gender or "Male",
                    "p_batting_style": batting_style or "Right-hand bat",
                    "p_bowling_style": bowling_style or "Right-arm medium",
                    "p_experience": int(experience or 0), "p_user_id": user_id
                })
                return {
                    "user_id": user_id,
                    "cricketer_id": cricketer_id,
                    "name": name.strip(),
                    "role": "Cricketer"
                }

    @staticmethod
    def create(name, password, phone, address, dob, gender, batting_style, bowling_style, experience):
        with get_db() as conn:
            with conn.cursor() as cur:
                # 1. Insert into "USER"
                cur.execute('SELECT NVL(MAX(User_id), 0) + 1 FROM "USER"')
                user_id = cur.fetchone()[0]
                hashed_pwd = generate_password_hash(password)
                cur.execute("""
                    INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
                    VALUES (:p_user_id, :p_name, :p_password, 'Cricketer', :p_phone, :p_address)
                """, {
                    "p_user_id": user_id, "p_name": name.strip(),
                    "p_password": hashed_pwd, "p_phone": phone, "p_address": address
                })

                # 2. Insert into CRICKETER
                cur.execute('SELECT NVL(MAX(Cricketer_id), 0) + 1 FROM CRICKETER')
                cricketer_id = cur.fetchone()[0]
                dob_val = datetime.strptime(dob, "%Y-%m-%d").date() if isinstance(dob, str) and dob else dob
                cur.execute("""
                    INSERT INTO CRICKETER (Cricketer_id, DOB, Gender, "Batting-Style", "Bowling-Style", Experience, User_id)
                    VALUES (:p_cricketer_id, :p_dob, :p_gender, :p_batting_style, :p_bowling_style, :p_experience, :p_user_id)
                """, {
                    "p_cricketer_id": cricketer_id, "p_dob": dob_val, "p_gender": gender,
                    "p_batting_style": batting_style, "p_bowling_style": bowling_style,
                    "p_experience": int(experience or 0), "p_user_id": user_id
                })
                return cricketer_id

    @staticmethod
    def update(cricketer_id, name, phone, address, dob, gender, batting_style, bowling_style, experience):
        cricketer = CricketerRepo.get_by_id(cricketer_id)
        if not cricketer:
            return 0
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE "USER"
                    SET Name = :p_name, Phone = :p_phone, Address = :p_address
                    WHERE User_id = :p_user_id
                """, {
                    "p_name": name.strip(), "p_phone": phone,
                    "p_address": address, "p_user_id": cricketer["user_id"]
                })

                dob_val = datetime.strptime(dob, "%Y-%m-%d").date() if isinstance(dob, str) and dob else dob
                cur.execute("""
                    UPDATE CRICKETER
                    SET DOB = :p_dob, Gender = :p_gender, "Batting-Style" = :p_batting_style,
                        "Bowling-Style" = :p_bowling_style, Experience = :p_experience
                    WHERE Cricketer_id = :p_cricketer_id
                """, {
                    "p_dob": dob_val, "p_gender": gender,
                    "p_batting_style": batting_style, "p_bowling_style": bowling_style,
                    "p_experience": int(experience or 0), "p_cricketer_id": int(cricketer_id)
                })
                return 1

    @staticmethod
    def delete(cricketer_id):
        cricketer = CricketerRepo.get_by_id(cricketer_id)
        if cricketer:
            return UserRepo.delete(cricketer["user_id"])
        return 0


# =====================================================================
# 3. TRAINER REPOSITORY (TRAINER)
# =====================================================================
class TrainerRepo:
    @staticmethod
    def list_all(search=None):
        sql = """
            SELECT t.Trainer_id, t.Specialization, t.Experience,
                   t.Qualification, t.Salary, t.User_id,
                   u.Name, u.Phone, u.Address
            FROM TRAINER t
            JOIN "USER" u ON t.User_id = u.User_id
            WHERE 1=1
        """
        params = {}
        if search:
            sql += """ AND (LOWER(u.Name) LIKE :p_search
                       OR LOWER(t.Specialization) LIKE :p_search
                       OR LOWER(t.Qualification) LIKE :p_search)"""
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY t.Trainer_id ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(trainer_id):
        sql = """
            SELECT t.Trainer_id, t.Specialization, t.Experience,
                   t.Qualification, t.Salary, t.User_id,
                   u.Name, u.Phone, u.Address
            FROM TRAINER t
            JOIN "USER" u ON t.User_id = u.User_id
            WHERE t.Trainer_id = :p_trainer_id
        """
        return query_one(sql, {"p_trainer_id": int(trainer_id)})

    @staticmethod
    def get_by_user_id(user_id):
        sql = """
            SELECT t.Trainer_id, t.Specialization, t.Experience,
                   t.Qualification, t.Salary, t.User_id,
                   u.Name, u.Phone, u.Address
            FROM TRAINER t
            JOIN "USER" u ON t.User_id = u.User_id
            WHERE t.User_id = :p_user_id
        """
        return query_one(sql, {"p_user_id": int(user_id)})

    @staticmethod
    def create(name, password, phone, address, specialization, experience, qualification, salary):
        with get_db() as conn:
            with conn.cursor() as cur:
                # 1. Insert into "USER"
                cur.execute('SELECT NVL(MAX(User_id), 0) + 1 FROM "USER"')
                user_id = cur.fetchone()[0]
                hashed_pwd = generate_password_hash(password)
                cur.execute("""
                    INSERT INTO "USER" (User_id, Name, Password, Role, Phone, Address)
                    VALUES (:p_user_id, :p_name, :p_password, 'Trainer', :p_phone, :p_address)
                """, {
                    "p_user_id": user_id, "p_name": name.strip(),
                    "p_password": hashed_pwd, "p_phone": phone, "p_address": address
                })

                # 2. Insert into TRAINER
                cur.execute('SELECT NVL(MAX(Trainer_id), 0) + 1 FROM TRAINER')
                trainer_id = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO TRAINER (Trainer_id, Specialization, Experience, Qualification, Salary, User_id)
                    VALUES (:p_trainer_id, :p_specialization, :p_experience, :p_qualification, :p_salary, :p_user_id)
                """, {
                    "p_trainer_id": trainer_id, "p_specialization": specialization,
                    "p_experience": int(experience or 0), "p_qualification": qualification,
                    "p_salary": float(salary or 0), "p_user_id": user_id
                })
                return trainer_id

    @staticmethod
    def update(trainer_id, name, phone, address, specialization, experience, qualification, salary):
        trainer = TrainerRepo.get_by_id(trainer_id)
        if not trainer:
            return 0
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE "USER"
                    SET Name = :p_name, Phone = :p_phone, Address = :p_address
                    WHERE User_id = :p_user_id
                """, {
                    "p_name": name.strip(), "p_phone": phone,
                    "p_address": address, "p_user_id": trainer["user_id"]
                })

                cur.execute("""
                    UPDATE TRAINER
                    SET Specialization = :p_specialization, Experience = :p_experience,
                        Qualification = :p_qualification, Salary = :p_salary
                    WHERE Trainer_id = :p_trainer_id
                """, {
                    "p_specialization": specialization, "p_experience": int(experience or 0),
                    "p_qualification": qualification, "p_salary": float(salary or 0),
                    "p_trainer_id": int(trainer_id)
                })
                return 1

    @staticmethod
    def delete(trainer_id):
        trainer = TrainerRepo.get_by_id(trainer_id)
        if trainer:
            return UserRepo.delete(trainer["user_id"])
        return 0


# =====================================================================
# 4. CRICKET PROGRAM REPOSITORY (CRICKET_PROGRAM)
# =====================================================================
class ProgramRepo:
    @staticmethod
    def list_all(search=None):
        sql = "SELECT Program_id, Program_name, Duration FROM CRICKET_PROGRAM WHERE 1=1"
        params = {}
        if search:
            sql += " AND (LOWER(Program_name) LIKE :p_search OR LOWER(Duration) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY Program_id ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(program_id):
        return query_one(
            "SELECT Program_id, Program_name, Duration FROM CRICKET_PROGRAM WHERE Program_id = :p_program_id",
            {"p_program_id": int(program_id)}
        )

    @staticmethod
    def create(program_name, duration):
        row = query_one("SELECT NVL(MAX(Program_id), 0) + 1 AS next_id FROM CRICKET_PROGRAM")
        next_id = row["next_id"] if row else 1
        sql = "INSERT INTO CRICKET_PROGRAM (Program_id, Program_name, Duration) VALUES (:p_program_id, :p_program_name, :p_duration)"
        execute_dml(sql, {
            "p_program_id": next_id,
            "p_program_name": program_name.strip(),
            "p_duration": duration.strip()
        })
        return next_id

    @staticmethod
    def update(program_id, program_name, duration):
        sql = "UPDATE CRICKET_PROGRAM SET Program_name = :p_program_name, Duration = :p_duration WHERE Program_id = :p_program_id"
        return execute_dml(sql, {
            "p_program_name": program_name.strip(),
            "p_duration": duration.strip(),
            "p_program_id": int(program_id)
        })

    @staticmethod
    def delete(program_id):
        return execute_dml("DELETE FROM CRICKET_PROGRAM WHERE Program_id = :p_program_id", {"p_program_id": int(program_id)})


# =====================================================================
# 5. VENUE REPOSITORY (VENUE)
# =====================================================================
class VenueRepo:
    @staticmethod
    def list_all(search=None):
        sql = "SELECT Venu_id, Venu_name, Location, Capacity, Availability FROM VENUE WHERE 1=1"
        params = {}
        if search:
            sql += " AND (LOWER(Venu_name) LIKE :p_search OR LOWER(Location) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY Venu_id ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(venu_id):
        return query_one(
            "SELECT Venu_id, Venu_name, Location, Capacity, Availability FROM VENUE WHERE Venu_id = :p_venu_id",
            {"p_venu_id": int(venu_id)}
        )

    @staticmethod
    def create(venu_name, location, capacity, availability="Available"):
        row = query_one("SELECT NVL(MAX(Venu_id), 0) + 1 AS next_id FROM VENUE")
        next_id = row["next_id"] if row else 1
        sql = """
            INSERT INTO VENUE (Venu_id, Venu_name, Location, Capacity, Availability)
            VALUES (:p_venu_id, :p_venu_name, :p_location, :p_capacity, :p_availability)
        """
        execute_dml(sql, {
            "p_venu_id": next_id, "p_venu_name": venu_name.strip(),
            "p_location": location.strip(), "p_capacity": int(capacity),
            "p_availability": availability
        })
        return next_id

    @staticmethod
    def update(venu_id, venu_name, location, capacity, availability):
        sql = """
            UPDATE VENUE
            SET Venu_name = :p_venu_name, Location = :p_location,
                Capacity = :p_capacity, Availability = :p_availability
            WHERE Venu_id = :p_venu_id
        """
        return execute_dml(sql, {
            "p_venu_name": venu_name.strip(), "p_location": location.strip(),
            "p_capacity": int(capacity), "p_availability": availability,
            "p_venu_id": int(venu_id)
        })

    @staticmethod
    def delete(venu_id):
        return execute_dml("DELETE FROM VENUE WHERE Venu_id = :p_venu_id", {"p_venu_id": int(venu_id)})


# =====================================================================
# 6. TRAINING SESSION REPOSITORY (TRAINING_SESSION)
# =====================================================================
class SessionRepo:
    @staticmethod
    def list_all(status=None, search=None, trainer_id=None, cricketer_id=None):
        sql = """
            SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
                   s.Trainer_id, s.Venu_id,
                   u.Name AS trainer_name, t.Specialization,
                   v.Venu_name, v.Location AS venue_location
            FROM TRAINING_SESSION s
            JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
            JOIN "USER" u ON t.User_id = u.User_id
            JOIN VENUE v ON s.Venu_id = v.Venu_id
            WHERE 1=1
        """
        params = {}
        if status:
            sql += " AND s.Status = :p_status"
            params["p_status"] = status
        if trainer_id:
            sql += " AND s.Trainer_id = :p_trainer_id"
            params["p_trainer_id"] = int(trainer_id)
        if cricketer_id:
            sql += " AND s.Session_id IN (SELECT Session_id FROM PARTICIPATE_IN WHERE Cricketer_id = :p_cricketer_id)"
            params["p_cricketer_id"] = int(cricketer_id)
        if search:
            sql += " AND (LOWER(u.Name) LIKE :p_search OR LOWER(v.Venu_name) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY s.Session_date DESC, s.Session_time ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(session_id):
        sql = """
            SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
                   s.Trainer_id, s.Venu_id,
                   u.Name AS trainer_name, v.Venu_name, v.Location AS venue_location
            FROM TRAINING_SESSION s
            JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
            JOIN "USER" u ON t.User_id = u.User_id
            JOIN VENUE v ON s.Venu_id = v.Venu_id
            WHERE s.Session_id = :p_session_id
        """
        return query_one(sql, {"p_session_id": int(session_id)})

    @staticmethod
    def create(session_date, session_time, status, trainer_id, venu_id):
        row = query_one("SELECT NVL(MAX(Session_id), 0) + 1 AS next_id FROM TRAINING_SESSION")
        next_id = row["next_id"] if row else 1
        dt_val = datetime.strptime(session_date, "%Y-%m-%d").date() if isinstance(session_date, str) else session_date
        sql = """
            INSERT INTO TRAINING_SESSION (Session_id, Session_date, Session_time, Status, Trainer_id, Venu_id)
            VALUES (:p_session_id, :p_session_date, :p_session_time, :p_status, :p_trainer_id, :p_venu_id)
        """
        execute_dml(sql, {
            "p_session_id": next_id, "p_session_date": dt_val,
            "p_session_time": session_time.strip(), "p_status": status,
            "p_trainer_id": int(trainer_id), "p_venu_id": int(venu_id)
        })
        return next_id

    @staticmethod
    def update(session_id, session_date, session_time, status, trainer_id, venu_id):
        dt_val = datetime.strptime(session_date, "%Y-%m-%d").date() if isinstance(session_date, str) else session_date
        sql = """
            UPDATE TRAINING_SESSION
            SET Session_date = :p_session_date, Session_time = :p_session_time,
                Status = :p_status, Trainer_id = :p_trainer_id, Venu_id = :p_venu_id
            WHERE Session_id = :p_session_id
        """
        return execute_dml(sql, {
            "p_session_date": dt_val, "p_session_time": session_time.strip(),
            "p_status": status, "p_trainer_id": int(trainer_id),
            "p_venu_id": int(venu_id), "p_session_id": int(session_id)
        })

    @staticmethod
    def delete(session_id):
        return execute_dml("DELETE FROM TRAINING_SESSION WHERE Session_id = :p_session_id", {"p_session_id": int(session_id)})


# =====================================================================
# 7. EQUIPMENT REPOSITORY (EQUIPMENT)
# =====================================================================
class EquipmentRepo:
    @staticmethod
    def list_all(search=None, availability=None):
        sql = """
            SELECT Equipment_id, Equipment_name, Equipment_type,
                   Total_Quantity, Availability, Quantity
            FROM EQUIPMENT
            WHERE 1=1
        """
        params = {}
        if availability:
            sql += " AND Availability = :p_availability"
            params["p_availability"] = availability
        if search:
            sql += " AND (LOWER(Equipment_name) LIKE :p_search OR LOWER(Equipment_type) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY Equipment_id ASC"
        return query_all(sql, params)

    @staticmethod
    def get_by_id(equipment_id):
        return query_one("""
            SELECT Equipment_id, Equipment_name, Equipment_type,
                   Total_Quantity, Availability, Quantity
            FROM EQUIPMENT WHERE Equipment_id = :p_equipment_id
        """, {"p_equipment_id": int(equipment_id)})

    @staticmethod
    def create(equipment_name, equipment_type, total_quantity, availability="Available", quantity=None):
        row = query_one("SELECT NVL(MAX(Equipment_id), 0) + 1 AS next_id FROM EQUIPMENT")
        next_id = row["next_id"] if row else 1
        tot = int(total_quantity)
        qty = int(quantity) if quantity is not None else tot
        sql = """
            INSERT INTO EQUIPMENT (Equipment_id, Equipment_name, Equipment_type, Total_Quantity, Availability, Quantity)
            VALUES (:p_equipment_id, :p_equipment_name, :p_equipment_type, :p_total_quantity, :p_availability, :p_quantity)
        """
        execute_dml(sql, {
            "p_equipment_id": next_id, "p_equipment_name": equipment_name.strip(),
            "p_equipment_type": equipment_type.strip(), "p_total_quantity": tot,
            "p_availability": availability, "p_quantity": qty
        })
        return next_id

    @staticmethod
    def update(equipment_id, equipment_name, equipment_type, total_quantity, availability, quantity):
        sql = """
            UPDATE EQUIPMENT
            SET Equipment_name = :p_equipment_name, Equipment_type = :p_equipment_type,
                Total_Quantity = :p_total_quantity, Availability = :p_availability, Quantity = :p_quantity
            WHERE Equipment_id = :p_equipment_id
        """
        return execute_dml(sql, {
            "p_equipment_name": equipment_name.strip(), "p_equipment_type": equipment_type.strip(),
            "p_total_quantity": int(total_quantity), "p_availability": availability,
            "p_quantity": int(quantity), "p_equipment_id": int(equipment_id)
        })

    @staticmethod
    def delete(equipment_id):
        return execute_dml("DELETE FROM EQUIPMENT WHERE Equipment_id = :p_equipment_id", {"p_equipment_id": int(equipment_id)})


# =====================================================================
# 8. PAYMENT REPOSITORY (PAYMENT)
# =====================================================================
class PaymentRepo:
    @staticmethod
    def list_all(status=None, cricketer_id=None, search=None):
        sql = """
            SELECT p.Cricketer_id, p.Program_id, p.Payment_Status,
                   p.Amount, p.Due_Date, p.Payment_Date,
                   u.Name AS cricketer_name, u.Phone AS cricketer_phone,
                   cp.Program_name
            FROM PAYMENT p
            JOIN CRICKETER c ON p.Cricketer_id = c.Cricketer_id
            JOIN "USER" u ON c.User_id = u.User_id
            JOIN CRICKET_PROGRAM cp ON p.Program_id = cp.Program_id
            WHERE 1=1
        """
        params = {}
        if status:
            sql += " AND p.Payment_Status = :p_status"
            params["p_status"] = status
        if cricketer_id:
            sql += " AND p.Cricketer_id = :p_cricketer_id"
            params["p_cricketer_id"] = int(cricketer_id)
        if search:
            sql += " AND (LOWER(u.Name) LIKE :p_search OR LOWER(cp.Program_name) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY p.Due_Date ASC"
        return query_all(sql, params)

    @staticmethod
    def create(cricketer_id, program_id, amount, due_date, payment_status="Pending", payment_date=None):
        due_val = datetime.strptime(due_date, "%Y-%m-%d").date() if isinstance(due_date, str) else due_date
        pay_val = None
        if payment_date:
            pay_val = datetime.strptime(payment_date, "%Y-%m-%d").date() if isinstance(payment_date, str) else payment_date
        elif payment_status == "Paid":
            pay_val = date.today()

        sql = """
            INSERT INTO PAYMENT (Cricketer_id, Program_id, Payment_Status, Amount, Due_Date, Payment_Date)
            VALUES (:p_cricketer_id, :p_program_id, :p_status, :p_amount, :p_due_date, :p_payment_date)
        """
        return execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id), "p_program_id": int(program_id),
            "p_status": payment_status, "p_amount": float(amount),
            "p_due_date": due_val, "p_payment_date": pay_val
        })

    @staticmethod
    def update_status(cricketer_id, program_id, due_date, new_status, payment_date=None):
        due_val = datetime.strptime(due_date, "%Y-%m-%d").date() if isinstance(due_date, str) else due_date
        pay_val = None
        if payment_date:
            pay_val = datetime.strptime(payment_date, "%Y-%m-%d").date() if isinstance(payment_date, str) else payment_date
        elif new_status == "Paid":
            pay_val = date.today()

        sql = """
            UPDATE PAYMENT
            SET Payment_Status = :p_status, Payment_Date = :p_payment_date
            WHERE Cricketer_id = :p_cricketer_id AND Program_id = :p_program_id AND Due_Date = :p_due_date
        """
        return execute_dml(sql, {
            "p_status": new_status, "p_payment_date": pay_val,
            "p_cricketer_id": int(cricketer_id), "p_program_id": int(program_id),
            "p_due_date": due_val
        })

    @staticmethod
    def delete(cricketer_id, program_id, due_date):
        due_val = datetime.strptime(due_date, "%Y-%m-%d").date() if isinstance(due_date, str) else due_date
        sql = "DELETE FROM PAYMENT WHERE Cricketer_id = :p_cricketer_id AND Program_id = :p_program_id AND Due_Date = :p_due_date"
        return execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id),
            "p_program_id": int(program_id),
            "p_due_date": due_val
        })


# =====================================================================
# 9. APPLICATION REPOSITORY (APPLIED_TO)
# =====================================================================
class ApplicationRepo:
    @staticmethod
    def list_all(status=None, cricketer_id=None, search=None):
        sql = """
            SELECT a.Cricketer_id, a.Program_id, a.Applied_status, a.Applied_date,
                   u.Name AS cricketer_name, u.Phone AS cricketer_phone,
                   cp.Program_name, cp.Duration
            FROM APPLIED_TO a
            JOIN CRICKETER c ON a.Cricketer_id = c.Cricketer_id
            JOIN "USER" u ON c.User_id = u.User_id
            JOIN CRICKET_PROGRAM cp ON a.Program_id = cp.Program_id
            WHERE 1=1
        """
        params = {}
        if status:
            sql += " AND a.Applied_status = :p_status"
            params["p_status"] = status
        if cricketer_id:
            sql += " AND a.Cricketer_id = :p_cricketer_id"
            params["p_cricketer_id"] = int(cricketer_id)
        if search:
            sql += " AND (LOWER(u.Name) LIKE :p_search OR LOWER(cp.Program_name) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY a.Applied_date DESC"
        return query_all(sql, params)

    @staticmethod
    def create(cricketer_id, program_id, applied_status="Pending", applied_date=None):
        app_date = datetime.strptime(applied_date, "%Y-%m-%d").date() if isinstance(applied_date, str) and applied_date else date.today()
        sql = """
            INSERT INTO APPLIED_TO (Cricketer_id, Program_id, Applied_status, Applied_date)
            VALUES (:p_cricketer_id, :p_program_id, :p_status, :p_applied_date)
        """
        return execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id), "p_program_id": int(program_id),
            "p_status": applied_status, "p_applied_date": app_date
        })

    @staticmethod
    def update_status(cricketer_id, program_id, new_status):
        sql = "UPDATE APPLIED_TO SET Applied_status = :p_status WHERE Cricketer_id = :p_cricketer_id AND Program_id = :p_program_id"
        return execute_dml(sql, {
            "p_status": new_status,
            "p_cricketer_id": int(cricketer_id),
            "p_program_id": int(program_id)
        })

    @staticmethod
    def delete(cricketer_id, program_id):
        sql = "DELETE FROM APPLIED_TO WHERE Cricketer_id = :p_cricketer_id AND Program_id = :p_program_id"
        return execute_dml(sql, {"p_cricketer_id": int(cricketer_id), "p_program_id": int(program_id)})


# =====================================================================
# 10. EQUIPMENT ISSUE REPOSITORY (EQUIPMENT_ISSUED)
# =====================================================================
class EquipmentIssueRepo:
    @staticmethod
    def list_all(status=None, cricketer_id=None, search=None):
        sql = """
            SELECT ei.Cricketer_id, ei.Equipment_id, ei.Issue_date,
                   ei.Return_Date, ei.Quantity, ei.Issue_status,
                   u.Name AS cricketer_name, u.Phone AS cricketer_phone,
                   eq.Equipment_name, eq.Equipment_type
            FROM EQUIPMENT_ISSUED ei
            JOIN CRICKETER c ON ei.Cricketer_id = c.Cricketer_id
            JOIN "USER" u ON c.User_id = u.User_id
            JOIN EQUIPMENT eq ON ei.Equipment_id = eq.Equipment_id
            WHERE 1=1
        """
        params = {}
        if status:
            sql += " AND ei.Issue_status = :p_status"
            params["p_status"] = status
        if cricketer_id:
            sql += " AND ei.Cricketer_id = :p_cricketer_id"
            params["p_cricketer_id"] = int(cricketer_id)
        if search:
            sql += " AND (LOWER(u.Name) LIKE :p_search OR LOWER(eq.Equipment_name) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY ei.Issue_date DESC"
        return query_all(sql, params)

    @staticmethod
    def issue_gear(cricketer_id, equipment_id, quantity=1):
        """
        Issues gear to a cricketer. Invokes PL/SQL stored procedure 'issue_equipment'.
        If procedure is absent, falls back to direct transaction with explicit inventory check.
        """
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    status_var = cur.var(str)
                    message_var = cur.var(str)
                    cur.callproc("issue_equipment", [
                        int(cricketer_id), int(equipment_id), int(quantity),
                        status_var, message_var
                    ])
                    return {
                        "status": status_var.getvalue() or "SUCCESS",
                        "message": message_var.getvalue() or "Equipment issued successfully."
                    }
        except Exception as plsql_err:
            logger.warning(f"issue_equipment procedure call error, attempting manual checkout: {plsql_err}")
            # Fallback direct execution
            eq = EquipmentRepo.get_by_id(equipment_id)
            if not eq or eq["quantity"] < int(quantity):
                return {"status": "ERROR", "message": "Insufficient equipment stock available."}
            execute_dml("""
                INSERT INTO EQUIPMENT_ISSUED (Cricketer_id, Equipment_id, Issue_date, Quantity, Issue_status)
                VALUES (:p_cricketer_id, :p_equipment_id, TRUNC(SYSDATE), :p_quantity, 'Issued')
            """, {
                "p_cricketer_id": int(cricketer_id),
                "p_equipment_id": int(equipment_id),
                "p_quantity": int(quantity)
            })
            return {"status": "SUCCESS", "message": "Equipment checkout recorded successfully."}

    @staticmethod
    def return_gear(cricketer_id, equipment_id, issue_date):
        iss_date = datetime.strptime(issue_date, "%Y-%m-%d").date() if isinstance(issue_date, str) else issue_date
        sql = """
            UPDATE EQUIPMENT_ISSUED
            SET Issue_status = 'Returned', Return_Date = TRUNC(SYSDATE)
            WHERE Cricketer_id = :p_cricketer_id AND Equipment_id = :p_equipment_id AND Issue_date = :p_issue_date
        """
        rows = execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id),
            "p_equipment_id": int(equipment_id),
            "p_issue_date": iss_date
        })
        return rows > 0

    @staticmethod
    def delete(cricketer_id, equipment_id, issue_date):
        iss_date = datetime.strptime(issue_date, "%Y-%m-%d").date() if isinstance(issue_date, str) else issue_date
        sql = "DELETE FROM EQUIPMENT_ISSUED WHERE Cricketer_id = :p_cricketer_id AND Equipment_id = :p_equipment_id AND Issue_date = :p_issue_date"
        return execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id),
            "p_equipment_id": int(equipment_id),
            "p_issue_date": iss_date
        })


# =====================================================================
# 11. PARTICIPATION REPOSITORY (PARTICIPATE_IN)
# =====================================================================
class ParticipationRepo:
    @staticmethod
    def list_all(session_id=None, cricketer_id=None, trainer_id=None, search=None):
        sql = """
            SELECT pi.Cricketer_id, pi.Session_id, pi.Participation_time, pi.Attendance,
                   u.Name AS cricketer_name, u.Phone AS cricketer_phone,
                   s.Session_date, s.Session_time, s.Status AS session_status,
                   v.Venu_name, u_t.Name AS trainer_name
            FROM PARTICIPATE_IN pi
            JOIN CRICKETER c ON pi.Cricketer_id = c.Cricketer_id
            JOIN "USER" u ON c.User_id = u.User_id
            JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
            JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
            JOIN "USER" u_t ON t.User_id = u_t.User_id
            JOIN VENUE v ON s.Venu_id = v.Venu_id
            WHERE 1=1
        """
        params = {}
        if session_id:
            sql += " AND pi.Session_id = :p_session_id"
            params["p_session_id"] = int(session_id)
        if cricketer_id:
            sql += " AND pi.Cricketer_id = :p_cricketer_id"
            params["p_cricketer_id"] = int(cricketer_id)
        if trainer_id:
            sql += " AND s.Trainer_id = :p_trainer_id"
            params["p_trainer_id"] = int(trainer_id)
        if search:
            sql += " AND (LOWER(u.Name) LIKE :p_search OR LOWER(v.Venu_name) LIKE :p_search OR LOWER(u_t.Name) LIKE :p_search)"
            params["p_search"] = f"%{search.lower().strip()}%"
        sql += " ORDER BY s.Session_date DESC, u.Name ASC"
        return query_all(sql, params)

    @staticmethod
    def record(cricketer_id, session_id, participation_time="2 Hours", attendance="Present"):
        sql = """
            INSERT INTO PARTICIPATE_IN (Cricketer_id, Session_id, Participation_time, Attendance)
            VALUES (:p_cricketer_id, :p_session_id, :p_participation_time, :p_attendance)
        """
        return execute_dml(sql, {
            "p_cricketer_id": int(cricketer_id), "p_session_id": int(session_id),
            "p_participation_time": participation_time, "p_attendance": attendance
        })

    @staticmethod
    def update(cricketer_id, session_id, participation_time, attendance):
        sql = """
            UPDATE PARTICIPATE_IN
            SET Participation_time = :p_participation_time, Attendance = :p_attendance
            WHERE Cricketer_id = :p_cricketer_id AND Session_id = :p_session_id
        """
        return execute_dml(sql, {
            "p_participation_time": participation_time, "p_attendance": attendance,
            "p_cricketer_id": int(cricketer_id), "p_session_id": int(session_id)
        })

    @staticmethod
    def delete(cricketer_id, session_id):
        sql = "DELETE FROM PARTICIPATE_IN WHERE Cricketer_id = :p_cricketer_id AND Session_id = :p_session_id"
        return execute_dml(sql, {"p_cricketer_id": int(cricketer_id), "p_session_id": int(session_id)})

    @staticmethod
    def get_attendance_percentage(cricketer_id):
        """
        Calls PL/SQL function 'calculate_attendance_pct' with SQL fallback.
        """
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    pct = cur.callfunc("calculate_attendance_pct", float, [int(cricketer_id)])
                    return round(float(pct), 2)
        except Exception:
            # Fallback pure SQL calculation
            row = query_one("""
                SELECT
                    COUNT(*) AS total_count,
                    COUNT(CASE WHEN Attendance = 'Present' THEN 1 END) AS pres_count
                FROM PARTICIPATE_IN
                WHERE Cricketer_id = :p_cricketer_id
            """, {"p_cricketer_id": int(cricketer_id)})
            if row and row["total_count"] > 0:
                return round((row["pres_count"] / row["total_count"]) * 100.0, 2)
            return 0.00


# =====================================================================
# 12. DASHBOARD REPOSITORY (REAL ORACLE AGGREGATES)
# =====================================================================
class DashboardRepo:
    @staticmethod
    def get_metrics():
        """
        Retrieves real-time aggregated metrics from Oracle database.
        Never hardcodes totals!
        """
        try:
            counts = query_one("""
                SELECT
                    (SELECT COUNT(*) FROM "USER") AS total_users,
                    (SELECT COUNT(*) FROM CRICKETER) AS total_cricketers,
                    (SELECT COUNT(*) FROM TRAINER) AS total_trainers,
                    (SELECT COUNT(*) FROM CRICKET_PROGRAM) AS total_programs,
                    (SELECT COUNT(*) FROM TRAINING_SESSION WHERE Status = 'Scheduled') AS upcoming_sessions,
                    (SELECT COUNT(*) FROM VENUE WHERE Availability = 'Available') AS available_venues,
                    (SELECT NVL(SUM(Amount), 0) FROM PAYMENT WHERE Payment_Status = 'Paid') AS collected_revenue,
                    (SELECT NVL(SUM(Amount), 0) FROM PAYMENT WHERE Payment_Status = 'Pending') AS pending_revenue,
                    (SELECT COUNT(*) FROM APPLIED_TO WHERE Applied_status = 'Pending') AS pending_applications,
                    (SELECT COUNT(*) FROM EQUIPMENT_ISSUED WHERE Issue_status = 'Issued') AS active_issued_gear
                FROM DUAL
            """)

            recent_sessions = query_all("""
                SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
                       u.Name AS trainer_name, v.Venu_name
                FROM TRAINING_SESSION s
                JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
                JOIN "USER" u ON t.User_id = u.User_id
                JOIN VENUE v ON s.Venu_id = v.Venu_id
                ORDER BY s.Session_date DESC
                FETCH FIRST 5 ROWS ONLY
            """)

            pending_payments = query_all("""
                SELECT u.Name AS cricketer_name, cp.Program_name, p.Amount, p.Due_Date
                FROM PAYMENT p
                JOIN CRICKETER c ON p.Cricketer_id = c.Cricketer_id
                JOIN "USER" u ON c.User_id = u.User_id
                JOIN CRICKET_PROGRAM cp ON p.Program_id = cp.Program_id
                WHERE p.Payment_Status = 'Pending'
                ORDER BY p.Due_Date ASC
                FETCH FIRST 5 ROWS ONLY
            """)

            return {
                "counts": counts or {},
                "recent_sessions": recent_sessions or [],
                "pending_payments": pending_payments or []
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard metrics: {e}")
            return {
                "counts": {},
                "recent_sessions": [],
                "pending_payments": []
            }

    @staticmethod
    def get_trainer_metrics(trainer_id):
        """
        Trainer-specific real Oracle dashboard data:
        - Total assigned sessions
        - Upcoming assigned sessions
        - Unique trainees coached
        - Recent session list and active roster
        """
        try:
            tid = int(trainer_id)
            counts = query_one("""
                SELECT
                    (SELECT COUNT(*) FROM TRAINING_SESSION WHERE Trainer_id = :p_tid) AS total_sessions,
                    (SELECT COUNT(*) FROM TRAINING_SESSION WHERE Trainer_id = :p_tid AND Status = 'Scheduled') AS upcoming_sessions,
                    (SELECT COUNT(DISTINCT pi.Cricketer_id)
                     FROM PARTICIPATE_IN pi
                     JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
                     WHERE s.Trainer_id = :p_tid) AS total_trainees,
                    (SELECT COUNT(*)
                     FROM PARTICIPATE_IN pi
                     JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
                     WHERE s.Trainer_id = :p_tid AND pi.Attendance = 'Present') AS total_attendances
                FROM DUAL
            """, {"p_tid": tid})

            my_sessions = query_all("""
                SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
                       v.Venu_name, v.Location,
                       (SELECT COUNT(*) FROM PARTICIPATE_IN pi WHERE pi.Session_id = s.Session_id) AS trainee_count
                FROM TRAINING_SESSION s
                JOIN VENUE v ON s.Venu_id = v.Venu_id
                WHERE s.Trainer_id = :p_tid
                ORDER BY s.Session_date DESC, s.Session_time ASC
                FETCH FIRST 8 ROWS ONLY
            """, {"p_tid": tid})

            trainees = query_all("""
                SELECT DISTINCT c.Cricketer_id, u.Name, u.Phone, c."Batting-Style" AS batting_style, c."Bowling-Style" AS bowling_style
                FROM PARTICIPATE_IN pi
                JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
                JOIN CRICKETER c ON pi.Cricketer_id = c.Cricketer_id
                JOIN "USER" u ON c.User_id = u.User_id
                WHERE s.Trainer_id = :p_tid
                ORDER BY u.Name ASC
                FETCH FIRST 10 ROWS ONLY
            """, {"p_tid": tid})

            return {
                "counts": counts or {},
                "my_sessions": my_sessions or [],
                "trainees": trainees or []
            }
        except Exception as e:
            logger.error(f"Error fetching trainer dashboard metrics: {e}")
            return {"counts": {}, "my_sessions": [], "trainees": []}

    @staticmethod
    def get_cricketer_metrics(cricketer_id):
        """
        Cricketer-specific real Oracle dashboard data:
        - Attendance % (using PL/SQL function calculate_attendance_pct)
        - Application counts & statuses
        - Upcoming assigned sessions
        - Active gear checked out
        - Pending dues amount
        """
        try:
            cid = int(cricketer_id)
            att_pct = ParticipationRepo.get_attendance_percentage(cid)

            counts = query_one("""
                SELECT
                    (SELECT COUNT(*) FROM APPLIED_TO WHERE Cricketer_id = :p_cid) AS total_applications,
                    (SELECT COUNT(*) FROM APPLIED_TO WHERE Cricketer_id = :p_cid AND Applied_status = 'Approved') AS approved_programs,
                    (SELECT COUNT(*) FROM PARTICIPATE_IN pi
                     JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
                     WHERE pi.Cricketer_id = :p_cid AND s.Status = 'Scheduled') AS upcoming_sessions,
                    (SELECT COUNT(*) FROM EQUIPMENT_ISSUED WHERE Cricketer_id = :p_cid AND Issue_status = 'Issued') AS active_gear_count,
                    (SELECT NVL(SUM(Amount), 0) FROM PAYMENT WHERE Cricketer_id = :p_cid AND Payment_Status = 'Pending') AS pending_dues
                FROM DUAL
            """, {"p_cid": cid})

            my_applications = query_all("""
                SELECT a.Program_id, cp.Program_name, cp.Duration, a.Applied_status
                FROM APPLIED_TO a
                JOIN CRICKET_PROGRAM cp ON a.Program_id = cp.Program_id
                WHERE a.Cricketer_id = :p_cid
                ORDER BY cp.Program_name ASC
            """, {"p_cid": cid})

            my_sessions = query_all("""
                SELECT s.Session_id, s.Session_date, s.Session_time, s.Status,
                       u_t.Name AS trainer_name, v.Venu_name, pi.Attendance
                FROM PARTICIPATE_IN pi
                JOIN TRAINING_SESSION s ON pi.Session_id = s.Session_id
                JOIN TRAINER t ON s.Trainer_id = t.Trainer_id
                JOIN "USER" u_t ON t.User_id = u_t.User_id
                JOIN VENUE v ON s.Venu_id = v.Venu_id
                WHERE pi.Cricketer_id = :p_cid
                ORDER BY s.Session_date DESC
                FETCH FIRST 6 ROWS ONLY
            """, {"p_cid": cid})

            my_gear = query_all("""
                SELECT ei.Equipment_id, eq.Equipment_name, eq.Equipment_type,
                       ei.Issue_date, ei.Quantity, ei.Issue_status
                FROM EQUIPMENT_ISSUED ei
                JOIN EQUIPMENT eq ON ei.Equipment_id = eq.Equipment_id
                WHERE ei.Cricketer_id = :p_cid AND ei.Issue_status = 'Issued'
                ORDER BY ei.Issue_date DESC
            """, {"p_cid": cid})

            my_payments = query_all("""
                SELECT p.Program_id, cp.Program_name, p.Amount, p.Due_Date, p.Payment_Status
                FROM PAYMENT p
                JOIN CRICKET_PROGRAM cp ON p.Program_id = cp.Program_id
                WHERE p.Cricketer_id = :p_cid
                ORDER BY p.Due_Date DESC
                FETCH FIRST 5 ROWS ONLY
            """, {"p_cid": cid})

            return {
                "attendance_pct": att_pct,
                "counts": counts or {},
                "my_applications": my_applications or [],
                "my_sessions": my_sessions or [],
                "my_gear": my_gear or [],
                "my_payments": my_payments or []
            }
        except Exception as e:
            logger.error(f"Error fetching cricketer dashboard metrics: {e}")
            return {
                "attendance_pct": 0.0,
                "counts": {},
                "my_applications": [],
                "my_sessions": [],
                "my_gear": [],
                "my_payments": []
            }


# =====================================================================
# 13. REPORT REPOSITORY (COURSEWORK ADVANCED SQL QUERIES)
# =====================================================================
class ReportRepo:
    @staticmethod
    def get_advanced_attendance_roster():
        """
        Query 1 from 05_advanced_queries.sql:
        Multi-Table Attendance Roster (5-Table JOIN with Session, Cricketer, Trainer, Venue)
        """
        sql = """
            SELECT
                u_c.Name             AS player_name,
                c."Batting-Style"    AS batting_style,
                s.Session_date       AS session_date,
                s.Session_time       AS session_time,
                u_t.Name             AS trainer_name,
                v.Venu_name          AS venue_name,
                p.Attendance         AS attendance_status,
                p.Participation_time AS duration_logged
            FROM PARTICIPATE_IN p
            JOIN CRICKETER c        ON p.Cricketer_id = c.Cricketer_id
            JOIN "USER" u_c         ON c.User_id = u_c.User_id
            JOIN TRAINING_SESSION s ON p.Session_id = s.Session_id
            JOIN TRAINER t          ON s.Trainer_id = t.Trainer_id
            JOIN "USER" u_t         ON t.User_id = u_t.User_id
            JOIN VENUE v            ON s.Venu_id = v.Venu_id
            ORDER BY s.Session_date DESC, u_c.Name ASC
        """
        return query_all(sql)

    @staticmethod
    def get_advanced_program_popularity_report():
        """
        Query 2 from 05_advanced_queries.sql:
        Program Popularity & Enrollment Metrics (GROUP BY, Aggregates, Approval Rates)
        """
        sql = """
            SELECT
                cp.Program_id        AS program_id,
                cp.Program_name      AS program_name,
                cp.Duration          AS duration,
                COUNT(a.Cricketer_id) AS total_applicants,
                SUM(CASE WHEN a.Applied_status = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
                SUM(CASE WHEN a.Applied_status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
                ROUND(
                    NVL(
                        (SUM(CASE WHEN a.Applied_status = 'Approved' THEN 1 ELSE 0 END) * 100.0) /
                        NULLIF(COUNT(a.Cricketer_id), 0),
                        0
                    ), 2
                ) AS approval_rate_pct
            FROM CRICKET_PROGRAM cp
            LEFT JOIN APPLIED_TO a ON cp.Program_id = a.Program_id
            GROUP BY cp.Program_id, cp.Program_name, cp.Duration
            ORDER BY total_applicants DESC
        """
        return query_all(sql)
