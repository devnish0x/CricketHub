"""
Crickethub - Database Connection & Oracle Utility Module
File: db.py
Description:
    Manages connections to the Oracle Database using the official `oracledb`
    Python driver in pure Thin Mode (no Oracle Instant Client required).
    Provides connection pooling, normalized dictionary row mapping, transaction
    handling, and invocation helpers for PL/SQL procedures and functions.
"""

import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import oracledb

# Load environment configuration from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crickethub.db")

# Load configuration with safe defaults
ORACLE_USER = os.getenv("ORACLE_USER", "crickethub_admin")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "XE")
ORACLE_DSN = os.getenv("ORACLE_DSN", None)


class RowDict(dict):
    """
    Case-insensitive dictionary wrapper for Oracle result rows.
    Allows accessing columns as row['name'], row['NAME'], or row.get('name'),
    as well as mapping hyphenated columns like 'Batting-Style' to 'batting_style'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._normalized_keys = {
            self._normalize(k): k for k in self.keys()
        }

    @staticmethod
    def _normalize(key):
        return str(key).lower().replace("-", "_").replace(" ", "_")

    def __getitem__(self, key):
        norm = self._normalize(key)
        if norm in self._normalized_keys:
            return super().__getitem__(self._normalized_keys[norm])
        return super().__getitem__(key)

    def get(self, key, default=None):
        norm = self._normalize(key)
        if norm in self._normalized_keys:
            return super().get(self._normalized_keys[norm], default)
        return super().get(key, default)

    def __contains__(self, key):
        norm = self._normalize(key)
        return norm in self._normalized_keys or super().__contains__(key)


def get_connection():
    """
    Establishes and returns a direct connection to the Oracle Database.
    Raises oracledb.DatabaseError with descriptive contextual details.
    """
    try:
        if ORACLE_DSN:
            conn = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                dsn=ORACLE_DSN
            )
        else:
            conn = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                host=ORACLE_HOST,
                port=int(ORACLE_PORT),
                service_name=ORACLE_SERVICE
            )
        return conn
    except oracledb.DatabaseError as e:
        error, = e.args
        logger.error(f"Oracle Connection Error [ORA-{error.code}]: {error.message}")
        raise


@contextmanager
def get_db():
    """
    Context manager providing a safe transaction scope.
    Automatically commits on success or rolls back on exception.
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception as exc:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.error(f"Transaction rolled back due to error: {exc}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def query_all(sql, params=None):
    """
    Executes a SELECT query and returns all rows as a list of RowDict objects.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or {})
            if not cursor.description:
                return []
            col_names = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                row_dict = RowDict(zip(col_names, row))
                result.append(row_dict)
            return result


def query_one(sql, params=None):
    """
    Executes a SELECT query and returns the first row as a RowDict, or None.
    """
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute_dml(sql, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE statement within a transaction.
    Returns the number of affected rows.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or {})
            return cursor.rowcount


def call_function(func_name, return_type, params=None):
    """
    Executes a PL/SQL stored function and returns the computed scalar value.
    Example:
        pct = call_function("calculate_attendance_pct", float, [cricketer_id])
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            return cursor.callfunc(func_name, return_type, params or [])


def call_procedure(proc_name, in_out_params):
    """
    Executes a PL/SQL stored procedure with IN and OUT parameters.
    Example:
        res = call_procedure("issue_equipment", [cid, eid, qty, status_var, msg_var])
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            return cursor.callproc(proc_name, in_out_params)


def check_db_health():
    """
    Tests connectivity to the Oracle database and schema table presence.
    Returns a dict with status: 'ok' or 'error' and diagnostic messages.
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1 FROM DUAL')
                res = cursor.fetchone()
                if res and res[0] == 1:
                    # Check for schema contract tables
                    cursor.execute("""
                        SELECT table_name
                        FROM user_tables
                        WHERE table_name IN (
                            'USER', 'CRICKETER', 'TRAINER', 'CRICKET_PROGRAM',
                            'VENUE', 'TRAINING_SESSION', 'EQUIPMENT', 'PAYMENT',
                            'APPLIED_TO', 'EQUIPMENT_ISSUED', 'PARTICIPATE_IN'
                        )
                    """)
                    found = [r[0] for r in cursor.fetchall()]
                    return {
                        "status": "ok",
                        "connected": True,
                        "tables_found": len(found),
                        "message": f"Successfully connected to Oracle. Found {len(found)}/11 project tables."
                    }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "tables_found": 0,
            "message": str(e)
        }
