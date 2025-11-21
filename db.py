# db.py
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
import hashlib

DB_FILE = os.path.join(os.path.dirname(__file__), "employee_data.db")

def _hash_password(username, password):
    # simple username+password hash (not for production)
    return hashlib.sha256(f"{username}::{password}".encode("utf-8")).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")

    # Employees
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        p_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        dob TEXT,
        doj TEXT,
        end_date TEXT,
        ticket_no TEXT,
        shop TEXT
    )
    """)

    # Attendance records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_no TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(p_no) REFERENCES employees(p_no) ON DELETE CASCADE
    )
    """)

    # Separation records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS separation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_no TEXT NOT NULL,
        name TEXT,
        separation_date TEXT NOT NULL,
        reason TEXT,
        FOREIGN KEY(p_no) REFERENCES employees(p_no) ON DELETE CASCADE
    )
    """)

    # Exam marks
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exam_marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_no TEXT NOT NULL,
        name TEXT,
        exam_type TEXT NOT NULL,
        exam_date TEXT,
        marks REAL,
        FOREIGN KEY(p_no) REFERENCES employees(p_no) ON DELETE CASCADE
    )
    """)

    # Users table for authentication (simple)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    conn.commit()

    # ensure at least one admin user exists
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        # default admin (please change after first login)
        default_user = "admin"
        default_pass = "admin123"
        ph = _hash_password(default_user, default_pass)
        cur.execute("INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (default_user, ph, "admin"))
        conn.commit()
        print("Default admin created -> username: admin  password: admin123  (change it immediately)")

    conn.close()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    try:
        # enable foreign keys for each connection
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.commit()
        conn.close()

def ensure_date_str(dt):
    """
    Accepts date-like input (datetime/date/string) and normalizes to YYYY-MM-DD string.
    If input is already None/empty -> returns None
    """
    if not dt:
        return None
    if isinstance(dt, str):
        # try to parse common formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(dt, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        # as a fallback, return the string (user could already supply proper ISO)
        return dt
    try:
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(dt)

# ---- User helpers ----------
def create_user(username, password, role="user"):
    ph = _hash_password(username, password)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, ph, role))

def verify_user(username, password):
    ph = _hash_password(username, password)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        r = cur.fetchone()
        if not r:
            return False
        return r[0] == ph

def get_user_role(username):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = ?", (username,))
        r = cur.fetchone()
        return r[0] if r else None

def list_users():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, role FROM users")
        return cur.fetchall()
