# migrate_db.py
import sqlite3
import sys
import os

DB_FILE = "employees.db"
REQUIRED = [
    ("p_no", "TEXT"),
    ("name", "TEXT"),
    ("phone", "TEXT"),
    ("date_of_joining", "TEXT"),
    ("end_date", "TEXT"),
    ("dob", "TEXT"),
    ("ticket_no", "TEXT"),
    ("shop", "TEXT")
]

def get_columns(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]

def main():
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found in this folder.")
        sys.exit(1)

    try:
        conn = sqlite3.connect(DB_FILE)
    except Exception as e:
        print("Failed to open DB:", e)
        sys.exit(1)

    try:
        existing = get_columns(conn, "employees")
    except Exception as e:
        print("Error reading table info. Table 'employees' may not exist yet.")
        print("Original error:", e)
        conn.close()
        sys.exit(1)

    added = []
    cur = conn.cursor()
    for col, coltype in REQUIRED:
        if col not in existing:
            sql = f"ALTER TABLE employees ADD COLUMN {col} {coltype}"
            print("Adding column:", col)
            cur.execute(sql)
            added.append(col)
    conn.commit()
    conn.close()

    if added:
        print("Migration complete. Added columns:", ", ".join(added))
    else:
        print("No missing columns found. Nothing to do.")

if __name__ == "__main__":
    main()
