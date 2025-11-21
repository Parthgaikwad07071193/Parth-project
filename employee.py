import pandas as pd
from db import get_conn, ensure_date_str
from utils import load_dataframe_from_file, map_columns_case_insensitive, save_dataframe_to_file

# ---------------------------
# Employee Management Functions
# ---------------------------

def _ensure_category_column():
    """
    Ensure the 'category' column exists in the employees table.
    If not present, add it via ALTER TABLE. Safe to call repeatedly.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(employees)")
        cols = [r[1] for r in cur.fetchall()]  # second field is column name
        if "category" not in cols:
            cur.execute("ALTER TABLE employees ADD COLUMN category TEXT")
            conn.commit()


def _normalize_category(cat):
    """
    Normalize category: if None/empty/'none' -> 'Other', otherwise return trimmed value.
    Allowed values expected: NEEM, NTTF, BTECH, MTECH, Other (or custom).
    """
    if cat is None:
        return "Other"
    s = str(cat).strip()
    if not s or s.lower() == "none":
        return "Other"
    # Keep user-provided category as-is (trimmed)
    return s


def add_employee(p_no, name, phone=None, dob=None, doj=None, end_date=None, ticket_no=None, shop=None, category=None):
    """
    Add a new employee to the database.
    category: optional, one of NEEM, NTTF, BTECH, MTECH or None.
              If None or 'none', stored as 'Other'.
    """
    dob = ensure_date_str(dob)
    doj = ensure_date_str(doj)
    end_date = ensure_date_str(end_date)
    category = _normalize_category(category)

    # make sure column exists
    _ensure_category_column()

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO employees
            (p_no, name, phone, dob, doj, end_date, ticket_no, shop, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(p_no), name, phone, dob, doj, end_date, ticket_no, shop, category))
        conn.commit()


def list_employees(order_by=None, order_dir="ascending", shop=None, category=None):
    """
    Return employees as list of dicts with optional filtering and ordering.
    - order_by: None or list/str of columns to order by (allowed: p_no,name,phone,dob,doj,end_date,ticket_no,shop,category)
    - order_dir: "ascending" or "descending"
    - shop: optional exact shop name to filter by (string). If None or empty -> no shop filter.
    - category: optional exact category name to filter by (string). If None or empty -> no category filter.
    """
    allowed = {"p_no","name","phone","dob","doj","end_date","ticket_no","shop","category"}
    order_dir_sql = "ASC" if str(order_dir).strip().lower() != "descending" else "DESC"

    with get_conn() as conn:
        cur = conn.cursor()
        # Check if 'category' exists
        cur.execute("PRAGMA table_info(employees)")
        cols_info = cur.fetchall()
        col_names = [r[1] for r in cols_info]
        has_category = "category" in col_names

        if has_category:
            select_cols = ["p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop", "category"]
        else:
            select_cols = ["p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop"]

        base_sql = "SELECT " + ", ".join(select_cols) + " FROM employees"

        # Build WHERE clause for filters
        where_clauses = []
        params = []
        if shop:
            where_clauses.append("shop = ?")
            params.append(shop)
        if category and has_category:
            where_clauses.append("category = ?")
            params.append(category)
        # if category filter requested but table lacks column, ignore category filter

        where_clause = ""
        if where_clauses:
            where_clause = " WHERE " + " AND ".join(where_clauses)

        # Build ORDER BY if requested
        order_clause = ""
        if order_by:
            # normalize to list
            if isinstance(order_by, str):
                order_list = [order_by]
            else:
                order_list = list(order_by)
            clean_order = []
            for col in order_list:
                c = str(col).strip()
                if c and c in allowed:
                    if c == "category" and not has_category:
                        continue
                    clean_order.append(c)
            if clean_order:
                order_clause = " ORDER BY " + ", ".join([f"{c} {order_dir_sql}" for c in clean_order])

        # Fallback: if no order clause, keep p_no ordering for stable output
        if not order_clause:
            order_clause = " ORDER BY p_no"

        sql = base_sql + where_clause + order_clause
        cur.execute(sql, params)
        rows = cur.fetchall()
    cols = select_cols
    return [dict(zip(cols, r)) for r in rows]


def get_employee(p_no):
    """
    Return a single employee dict or None.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        # attempt to select category if exists
        cur.execute("PRAGMA table_info(employees)")
        cols_info = cur.fetchall()
        col_names = [r[1] for r in cols_info]
        if "category" in col_names:
            cur.execute("SELECT p_no, name, phone, dob, doj, end_date, ticket_no, shop, category FROM employees WHERE p_no = ?", (str(p_no),))
            row = cur.fetchone()
            if row:
                cols = ["p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop", "category"]
                return dict(zip(cols, row))
        else:
            cur.execute("SELECT p_no, name, phone, dob, doj, end_date, ticket_no, shop FROM employees WHERE p_no = ?", (str(p_no),))
            row = cur.fetchone()
            if row:
                cols = ["p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop"]
                return dict(zip(cols, row))
    return None


def delete_employee(p_no):
    """
    Delete a single employee by p_no.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE p_no = ?", (str(p_no),))
        conn.commit()


def delete_all_employees():
    """
    Delete ALL employees from the table.
    Use with caution — this clears the employees table entirely.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees")
        conn.commit()


def bulk_upload_employees(filepath):
    """
    Bulk upload employees from a file (CSV, XLSX, JSON, etc).
    Required columns: p_no, name
    Optional: phone, dob, doj, end_date, ticket_no, shop, category

    Returns number of inserted/updated rows.
    """
    df = load_dataframe_from_file(filepath)
    if df is None or df.empty:
        return 0

    mapping = map_columns_case_insensitive(df,
        ["p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop", "category"]
    )
    inserted = 0
    for i, row in df.iterrows():
        try:
            p_col = mapping.get("p_no")
            n_col = mapping.get("name")
            if p_col is None or n_col is None:
                # required columns missing in this file
                continue
            p = row[p_col]
            n = row[n_col]
            if pd.isna(p) or pd.isna(n):
                continue
            phone = row[mapping.get("phone")] if mapping.get("phone") else None
            dob = row[mapping.get("dob")] if mapping.get("dob") else None
            doj = row[mapping.get("doj")] if mapping.get("doj") else None
            end_date = row[mapping.get("end_date")] if mapping.get("end_date") else None
            ticket = row[mapping.get("ticket_no")] if mapping.get("ticket_no") else None
            shop = row[mapping.get("shop")] if mapping.get("shop") else None
            category = row[mapping.get("category")] if mapping.get("category") else None

            # Normalize category
            category = _normalize_category(category) if category is not None else "Other"

            add_employee(p, n, phone, dob, doj, end_date, ticket, shop, category)
            inserted += 1
        except Exception as e:
            print("bulk_upload_employees skip:", i, e)
    return inserted


def export_employees(path):
    """
    Export employees list to a file (CSV, XLSX, JSON).
    """
    rows = list_employees()
    df = pd.DataFrame(rows)
    save_dataframe_to_file(df, path)
    return path
