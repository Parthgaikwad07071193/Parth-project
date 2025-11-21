
import pandas as pd
from db import get_conn, ensure_date_str
from utils import load_dataframe_from_file, map_columns_case_insensitive, save_dataframe_to_file

def add_separation(p_no, name, separation_date, reason=None):
    """Insert a single separation record"""
    sd = ensure_date_str(separation_date)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO separation (p_no, name, separation_date, reason) VALUES (?, ?, ?, ?)",
            (str(p_no), name, sd, reason)
        )

def list_separations():
    """Return all separation records"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, p_no, name, separation_date, reason FROM separation ORDER BY separation_date DESC")
        rows = cur.fetchall()
    cols = ["id", "p_no", "name", "separation_date", "reason"]
    return [dict(zip(cols, r)) for r in rows]

def delete_separation(rec_id):
    """Delete a separation record by ID"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM separation WHERE id = ?", (rec_id,))

def bulk_upload_separations(filepath):
    """
    Bulk upload separations from CSV, Excel, or JSON file.
    Expected columns (case-insensitive): p_no, name, separation_date, reason
    """
    df = load_dataframe_from_file(filepath)
    if df is None or df.empty:
        print("No data loaded from file:", filepath)
        return 0

    # Normalize and map columns
    mapping = map_columns_case_insensitive(df, ["p_no", "name", "separation_date", "reason"])
    inserted = 0

    for i, row in df.iterrows():
        try:
            p = row[mapping.get("p_no")] if mapping.get("p_no") in row else None
            name = row[mapping.get("name")] if mapping.get("name") else None
            sd = row[mapping.get("separation_date")] if mapping.get("separation_date") else None
            reason = row[mapping.get("reason")] if mapping.get("reason") else None

            if pd.isna(p) or pd.isna(sd):
                continue  # skip invalid rows

            add_separation(p, name, sd, reason)
            inserted += 1
        except Exception as e:
            print(f"bulk_upload_separations skip row {i}: {e}")

    return inserted

def export_separations(path):
    """Export separation records to file (CSV, Excel, JSON supported)"""
    rows = list_separations()
    df = pd.DataFrame(rows)
    if df.empty:
        print("No separations to export")
        return None
    save_dataframe_to_file(df, path)
    return path
