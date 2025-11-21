# attendance.py
from db import get_conn, ensure_date_str
import pandas as pd
from utils import load_dataframe_from_file, map_columns_case_insensitive
from datetime import datetime, timedelta
import employee
import random

VALID_STATUSES = {"present": "Present", "p": "Present",
                  "absent": "Absent", "a": "Absent",
                  "leave": "Leave", "l": "Leave"}


def normalize_status(s):
    if s is None:
        return None
    s = str(s).strip().lower()
    return VALID_STATUSES.get(s, s.capitalize())


def mark_attendance(p_no, date_str, status):
    date_norm = ensure_date_str(date_str)
    status_norm = normalize_status(status)
    if not status_norm:
        raise ValueError("Invalid status")
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO attendance (p_no, date, status) VALUES (?, ?, ?)",
                    (str(p_no), date_norm, status_norm))
        conn.commit()


def update_attendance(p_no, date_str, status):
    """
    Replace existing attendance for p_no + date, then insert new record.
    """
    date_norm = ensure_date_str(date_str)
    status_norm = normalize_status(status)
    if not status_norm:
        raise ValueError("Invalid status")
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM attendance WHERE p_no = ? AND date = ?", (str(p_no), date_norm))
        cur.execute("INSERT INTO attendance (p_no, date, status) VALUES (?, ?, ?)",
                    (str(p_no), date_norm, status_norm))
        conn.commit()


def get_leave_count_for_employee(p_no, date_from=None, date_to=None):
    with get_conn() as conn:
        cur = conn.cursor()
        q = "SELECT COUNT(*) FROM attendance WHERE p_no = ? AND status = 'Leave'"
        params = [str(p_no)]
        if date_from:
            q += " AND date >= ?"
            params.append(ensure_date_str(date_from))
        if date_to:
            q += " AND date <= ?"
            params.append(ensure_date_str(date_to))
        cur.execute(q, params)
        return cur.fetchone()[0]


def get_absent_count_for_employee(p_no, date_from=None, date_to=None):
    with get_conn() as conn:
        cur = conn.cursor()
        q = "SELECT COUNT(*) FROM attendance WHERE p_no = ? AND status = 'Absent'"
        params = [str(p_no)]
        if date_from:
            q += " AND date >= ?"
            params.append(ensure_date_str(date_from))
        if date_to:
            q += " AND date <= ?"
            params.append(ensure_date_str(date_to))
        cur.execute(q, params)
        return cur.fetchone()[0]


def find_employees_with_leave_count(target_count, date_from=None, date_to=None):
    """
    Returns list of p_no with leave_count == target_count within date range.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        q = """
        SELECT e.p_no, e.name, COUNT(a.id) as leave_count
        FROM employees e
        LEFT JOIN attendance a ON e.p_no = a.p_no AND a.status = 'Leave'
        WHERE 1=1
        """
        params = []
        if date_from:
            q += " AND a.date >= ?"
            params.append(ensure_date_str(date_from))
        if date_to:
            q += " AND a.date <= ?"
            params.append(ensure_date_str(date_to))
        q += " GROUP BY e.p_no HAVING leave_count = ? ORDER BY e.name"
        params.append(int(target_count))
        cur.execute(q, params)
        rows = cur.fetchall()
    return [{"p_no": r[0], "name": r[1], "leave_count": r[2]} for r in rows]


def find_employees_with_absent_count(target_count, date_from=None, date_to=None):
    """
    Returns list of p_no with absent_count == target_count within date range.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        q = """
        SELECT e.p_no, e.name, COUNT(a.id) as absent_count
        FROM employees e
        LEFT JOIN attendance a ON e.p_no = a.p_no AND a.status = 'Absent'
        WHERE 1=1
        """
        params = []
        if date_from:
            q += " AND a.date >= ?"
            params.append(ensure_date_str(date_from))
        if date_to:
            q += " AND a.date <= ?"
            params.append(ensure_date_str(date_to))
        q += " GROUP BY e.p_no HAVING absent_count = ? ORDER BY e.name"
        params.append(int(target_count))
        cur.execute(q, params)
        rows = cur.fetchall()
    return [{"p_no": r[0], "name": r[1], "absent_count": r[2]} for r in rows]


def get_attendance_summary(date_from=None, date_to=None, sort_by=None):
    """
    Returns summary with counts of Present/Absent/Leave per employee in range.
    sort_by: None or 'absent' or 'leave' (descending)
    """
    with get_conn() as conn:
        cur = conn.cursor()
        q = """
        SELECT e.p_no, e.name,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN a.status='Leave' THEN 1 ELSE 0 END) as leave_count
        FROM employees e
        LEFT JOIN attendance a ON e.p_no = a.p_no
        WHERE 1=1
        """
        params = []
        if date_from:
            q += " AND a.date >= ?"
            params.append(ensure_date_str(date_from))
        if date_to:
            q += " AND a.date <= ?"
            params.append(ensure_date_str(date_to))
        q += " GROUP BY e.p_no, e.name"
        if sort_by == "absent":
            q += " ORDER BY absent_count DESC"
        elif sort_by == "leave":
            q += " ORDER BY leave_count DESC"
        else:
            q += " ORDER BY e.name"
        cur.execute(q, params)
        rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({
            "p_no": r[0],
            "name": r[1],
            "present": r[2],
            "absent": r[3],
            "leave": r[4]
        })
    return results


def get_attendance_for_date(date_value):
    """
    Return list of dicts for every employee with status on given date.
    date_value may be a date string or date object. Returned status is 'Present'/'Absent'/'Leave' or 'Not Recorded'.
    """
    date_norm = ensure_date_str(date_value)
    with get_conn() as conn:
        cur = conn.cursor()
        q = """
        SELECT e.p_no, e.name, COALESCE(a.status, 'Not Recorded') as status
        FROM employees e
        LEFT JOIN attendance a ON e.p_no = a.p_no AND a.date = ?
        ORDER BY e.p_no
        """
        cur.execute(q, (date_norm,))
        rows = cur.fetchall()
    return [{"p_no": r[0], "name": r[1], "status": r[2]} for r in rows]


def _attempt_infer_column(df, want):
    """
    Helper: try to infer a column name from df.columns for required 'want' values:
    - want in ('p_no','date','status','name')
    """
    want = want.lower()
    for col in df.columns:
        c = str(col).lower()
        if want == "p_no":
            if "p_no" in c or "pno" in c or c in ("p", "id", "pn", "empid", "emp_id", "employee id", "employeeid"):
                return col
        if want == "date":
            if "date" in c or "day" in c or "attendance" in c or c in ("d",):
                return col
        if want == "status":
            if "status" in c or "att" in c or "present" in c or "absent" in c or "leave" in c:
                return col
        if want == "name":
            if "name" in c or "employee" in c:
                return col
    return None


def bulk_upload_attendance(filepath, create_missing=False):
    """
    Expects at least: p_no, date, status. Uses utils to map columns.
    If create_missing=True then missing employees (p_no not in employees table)
    will be created automatically (name column used if available).
    Returns tuple: (inserted_attendance_rows, created_employee_count)
    """
    df = load_dataframe_from_file(filepath)
    if df is None or df.empty:
        print("bulk_upload_attendance: file empty or unreadable")
        return 0, 0

    mapping = map_columns_case_insensitive(df, ["p_no", "date", "status", "name"])

    # If mapping lacks required columns, try to infer them
    for key in ("p_no", "date", "status"):
        if not mapping.get(key):
            inferred = _attempt_infer_column(df, key)
            if inferred:
                mapping[key] = inferred

    # if still missing required mapping, abort with informative message
    if not mapping.get("p_no") or not mapping.get("date") or not mapping.get("status"):
        missing = [k for k in ("p_no","date","status") if not mapping.get(k)]
        raise ValueError(f"bulk_upload_attendance: required columns missing or not detected: {missing}")

    inserted = 0
    created = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            p_raw = row.get(mapping.get("p_no")) if mapping.get("p_no") in df.columns else row.get(mapping.get("p_no"), None)
            d_raw = row.get(mapping.get("date")) if mapping.get("date") in df.columns else row.get(mapping.get("date"), None)
            s_raw = row.get(mapping.get("status")) if mapping.get("status") in df.columns else row.get(mapping.get("status"), None)

            # Skip rows missing required fields
            if pd.isna(p_raw) or pd.isna(d_raw):
                skipped += 1
                continue

            p_str = str(p_raw).strip()

            # normalize/validate date
            try:
                d_norm = ensure_date_str(d_raw)
            except Exception as e:
                skipped += 1
                print(f"bulk_upload_attendance skip row {idx}: invalid date {d_raw} -> {e}")
                continue

            # normalize/validate status
            status_norm = normalize_status(s_raw)
            if not status_norm:
                skipped += 1
                print(f"bulk_upload_attendance skip row {idx}: invalid status '{s_raw}'")
                continue

            # check if employee exists
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM employees WHERE p_no = ?", (p_str,))
                exists = cur.fetchone()[0] > 0

            if not exists and create_missing:
                # try to get name from file, otherwise create placeholder
                name = None
                name_col = mapping.get("name")
                if name_col and name_col in df.columns:
                    nm = row.get(name_col)
                    if not pd.isna(nm):
                        name = str(nm).strip()
                if not name:
                    name = f"Employee_{p_str}"
                # create minimal employee record
                try:
                    employee.add_employee(p_no=p_str, name=name)
                    created += 1
                except Exception as e:
                    # failed to create employee — skip this attendance row
                    skipped += 1
                    print(f"bulk_upload_attendance: failed to create employee {p_str}: {e}")
                    continue

            # Ensure the employee exists now
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM employees WHERE p_no = ?", (p_str,))
                exists_after = cur.fetchone()[0] > 0
            if not exists_after:
                skipped += 1
                continue

            # Use update_attendance to replace any existing entry for that p_no/date
            try:
                update_attendance(p_str, d_norm, status_norm)
                inserted += 1
            except Exception as e:
                skipped += 1
                print(f"bulk_upload_attendance skip row {idx}: {e}")

        except Exception as e:
            skipped += 1
            print("bulk_upload_attendance outer skip:", idx, e)

    if skipped:
        print(f"bulk_upload_attendance: inserted={inserted}, created={created}, skipped={skipped}")
    else:
        print(f"bulk_upload_attendance: inserted={inserted}, created={created}")
    return inserted, created


def _iter_dates_inclusive(start_date, end_date):
    """
    Helper generator returning date strings (YYYY-MM-DD) from start_date to end_date inclusive.
    Accepts date objects or strings.
    """
    start = datetime.strptime(ensure_date_str(start_date), "%Y-%m-%d").date()
    end = datetime.strptime(ensure_date_str(end_date), "%Y-%m-%d").date()
    cur = start
    while cur <= end:
        yield cur.strftime("%Y-%m-%d")
        cur = cur + timedelta(days=1)


def auto_generate_attendance(date_from, date_to, present_pct=85, absent_pct=10, leave_pct=5,
                             shop=None, category=None, create_missing=False, seed=None):
    """
    Auto-generate attendance for employees in the given shop/category (or all if None).
    - date_from/date_to: date strings or date objects (inclusive).
    - present_pct, absent_pct, leave_pct: integer percentages (do not need to sum to 100).
    - shop/category: optional exact strings to filter employees (use employee.list_employees(shop=..., category=...))
    - create_missing: unused normally because we read employees from DB; kept for parity with bulk_upload.
    - seed: optional integer to seed randomness (useful for reproducible datasets)

    Returns: dict with keys: inserted (rows written), employees_count, dates_count
    """
    if seed is not None:
        random.seed(seed)

    # validate & form weights
    try:
        p = float(present_pct)
        a = float(absent_pct)
        l = float(leave_pct)
    except Exception:
        raise ValueError("present/absent/leave percentages must be numbers")

    total = p + a + l
    if total <= 0:
        raise ValueError("At least one of present/absent/leave percentages must be > 0")

    weights = [p / total, a / total, l / total]
    status_choices = ["Present", "Absent", "Leave"]

    # get employees to generate for
    employees = employee.list_employees(shop=shop, category=category)
    if not employees:
        # nothing to do
        return {"inserted": 0, "employees_count": 0, "dates_count": 0}

    dates = list(_iter_dates_inclusive(date_from, date_to))
    inserted = 0

    for emp in employees:
        p_no = emp.get("p_no")
        # for each date assign status by weighted random
        for d in dates:
            status = random.choices(status_choices, weights=weights, k=1)[0]
            try:
                # update_attendance will replace existing entry for that date
                update_attendance(p_no, d, status)
                inserted += 1
            except Exception as e:
                # skip problematic rows silently, but could log if needed
                print(f"auto_generate_attendance: skip {p_no} {d}: {e}")
                continue

    return {"inserted": inserted, "employees_count": len(employees), "dates_count": len(dates)}
