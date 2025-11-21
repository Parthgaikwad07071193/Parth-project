# exam.py
import os
from datetime import datetime
import pandas as pd
from db import get_conn, ensure_date_str
from utils import load_dataframe_from_file, map_columns_case_insensitive, save_dataframe_to_file

# --- UI imports for the new window helpers ---
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry

# Define structured exam groups and their parts
EXAM_GROUPS = {
    "Induction": ["PreTest", "PostTest"],
    "NEEM": ["Sem1", "Sem2", "Sem3", "Sem4", "Sem5", "Sem6"],
    "NTTF": ["Sem1", "Sem2", "Sem3", "Sem4", "Sem5", "Sem6"],
    "BTECH": ["Sem1", "Sem2", "Sem3", "Sem4", "Sem5", "Sem6"],
    "MTECH": ["Sem1", "Sem2", "Sem3", "Sem4"],
}

# Flatten list of canonical part keys in desired order
def _all_part_keys():
    keys = []
    for grp in ["Induction", "NEEM", "NTTF", "BTECH", "MTECH"]:
        parts = EXAM_GROUPS.get(grp, [])
        for p in parts:
            keys.append((grp, p))
    return keys

# Helper: build exam_type string stored in DB
def _exam_type_key(group, part):
    return f"{group}_{part}"

# Normalize a raw exam_type string into canonical DB exam_type (group_part)
def normalize_exam_type(raw):
    """
    Accepts values like:
      - "NEEM Sem1", "NEEM_Sem1", "neem sem 1", "Sem1 NEEM", "Induction PreTest", etc.
    Returns canonical string like "NEEM_Sem1" or "Induction_PreTest" or "Other_<raw>" fallback.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    s_low = s.lower().replace("-", " ").replace("_", " ").replace(".", " ")
    parts = s_low.split()
    # try to detect group present
    groups_lower = {g.lower(): g for g in EXAM_GROUPS.keys()}
    detected_group = None
    detected_part = None

    # detect group token in parts
    for token in parts:
        if token in groups_lower:
            detected_group = groups_lower[token]
            break

    # detect part (pre/post or sem+digit)
    for token in parts:
        t = token.replace(" ", "")
        # pre/post detection
        if t in ("pretest", "pre", "pre-test", "pre_test"):
            detected_part = "PreTest"
            break
        if t in ("posttest", "post", "post-test", "post_test"):
            detected_part = "PostTest"
            break
        # sem detection: look for digits
        if "sem" in t:
            digits = ''.join(ch for ch in t if ch.isdigit())
            if digits:
                try:
                    n = int(digits)
                    detected_part = f"Sem{n}"
                    break
                except Exception:
                    continue
        # token might be purely a digit representing sem number
        if token.isdigit():
            n = int(token)
            detected_part = f"Sem{n}"
            break

    # if group not found but part indicates a sem, try infer common groups (rare)
    if detected_group is None:
        # if part is PreTest/PostTest assume Induction
        if detected_part in ("PreTest", "PostTest"):
            detected_group = "Induction"
        else:
            # ambiguous sem -> leave undetected (fallback later)
            pass

    if detected_group and detected_part:
        # validate part exists in group
        parts_allowed = EXAM_GROUPS.get(detected_group, [])
        if detected_part in parts_allowed:
            return _exam_type_key(detected_group, detected_part)
        else:
            # return even if not allowed; caller may handle it
            return _exam_type_key(detected_group, detected_part)

    # last attempt: some callers may pass exact canonical like "NEEM_Sem1"
    if "_" in s:
        cand = s.replace(" ", "_")
        cand_low = cand.lower()
        for g, parts in EXAM_GROUPS.items():
            for p in parts:
                if cand_low == f"{g.lower()}_{p.lower()}":
                    return _exam_type_key(g, p)

    # unknown format -> fallback to raw label but prefix Other_ to avoid collision
    return f"Other_{s.replace(' ', '_')}"

def add_exam_mark(p_no, name, exam_type, exam_date, marks):
    """
    Insert a single exam row. exam_type is expected to be a canonical string (like 'NEEM_Sem1')
    but we will accept raw strings and normalize them.
    exam_date may be date/datetime/string — ensure_date_str will normalize.
    """
    etype = normalize_exam_type(exam_type) or exam_type
    d = ensure_date_str(exam_date)
    marks_val = None
    if marks is not None and (not (isinstance(marks, float) and pd.isna(marks))):
        try:
            marks_val = float(marks)
        except Exception:
            marks_val = marks  # keep raw if cannot cast
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO exam_marks (p_no, name, exam_type, exam_date, marks) VALUES (?, ?, ?, ?, ?)",
            (str(p_no), name, etype, d, marks_val)
        )
        conn.commit()

def add_structured_exam(p_no, name, group, part, exam_date, marks):
    """
    Convenience wrapper to add a structured exam piece (e.g. NEEM Sem1 or Induction PreTest).
    group: one of EXAM_GROUPS keys
    part: specific part name, e.g. "Sem1", "PreTest"
    """
    if group not in EXAM_GROUPS:
        raise ValueError("Unknown exam group: " + str(group))
    if part not in EXAM_GROUPS[group]:
        raise ValueError(f"Invalid part '{part}' for group '{group}'")
    exam_type = _exam_type_key(group, part)
    add_exam_mark(p_no, name, exam_type, exam_date, marks)

def list_exam_marks(limit=500):
    """Return recent exam records for inspection."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, p_no, name, exam_type, exam_date, marks FROM exam_marks ORDER BY exam_date DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
    cols = ["id", "p_no", "name", "exam_type", "exam_date", "marks"]
    return [dict(zip(cols, r)) for r in rows]

def delete_exam_record(rec_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM exam_marks WHERE id = ?", (rec_id,))
        conn.commit()

def bulk_upload_exams(filepath, force_group=None, force_part=None):
    """
    Bulk upload exam rows from CSV/XLSX/JSON.
    If force_group and force_part provided, all inserted rows will be assigned that exam_type.
    Required per-row: p_no (or equivalent), exam_date (and optionally name, marks).
    Returns number of successfully inserted rows.
    """
    df = load_dataframe_from_file(filepath)
    if df is None or df.empty:
        return 0

    mapping = map_columns_case_insensitive(df, ["p_no", "name", "exam_type", "exam_date", "marks"])
    inserted = 0
    for i, row in df.iterrows():
        try:
            # pick values using mapping if available
            p_val = None
            if mapping.get("p_no") in df.columns:
                p_val = row[mapping.get("p_no")]
            else:
                # attempt to find a likely column
                for col in df.columns:
                    if str(col).lower() in ("p_no", "pno", "p.no", "pn", "id", "employeeid", "empid"):
                        p_val = row[col]; break

            if pd.isna(p_val):
                continue

            name_val = row[mapping.get("name")] if mapping.get("name") in df.columns else None
            et_raw = row[mapping.get("exam_type")] if mapping.get("exam_type") in df.columns else None
            ed_raw = row[mapping.get("exam_date")] if mapping.get("exam_date") in df.columns else None
            marks_val = row[mapping.get("marks")] if mapping.get("marks") in df.columns else None

            if pd.isna(ed_raw):
                # exam_date mandatory for insertion (we require date or it won't insert)
                continue

            if force_group and force_part:
                # use forced structured exam
                add_structured_exam(p_no=str(p_val).strip(),
                                    name=(None if (pd.isna(name_val)) else str(name_val).strip()),
                                    group=force_group,
                                    part=force_part,
                                    exam_date=ed_raw,
                                    marks=(None if (pd.isna(marks_val)) else marks_val))
            else:
                # Normalize exam_type to canonical like "NEEM_Sem1" if present in file
                if pd.isna(et_raw):
                    # skip if we don't know exam type
                    continue
                et_key = normalize_exam_type(et_raw)
                add_exam_mark(p_no=str(p_val).strip(),
                              name=(None if (pd.isna(name_val)) else str(name_val).strip()),
                              exam_type=et_key,
                              exam_date=ed_raw,
                              marks=(None if (pd.isna(marks_val)) else marks_val))
            inserted += 1
        except Exception as e:
            print("bulk_upload_exams skip:", i, e)
            continue

    return inserted

def bulk_upload_for(group, part, filepath):
    """
    Convenience: bulk upload rows and force exam_type to given structured group+part.
    Returns number inserted and a message string.
    """
    if group not in EXAM_GROUPS:
        raise ValueError("Unknown exam group: " + str(group))
    if part not in EXAM_GROUPS[group]:
        raise ValueError(f"Invalid part '{part}' for group '{group}'")
    cnt = bulk_upload_exams(filepath, force_group=group, force_part=part)
    return cnt

def pivot_exam_summary():
    """
    Return list[dict] where each dict has:
      p_no, name, and for each group+part two keys:
        <Group>_<Part>_marks, <Group>_<Part>_date
    Ensures canonical columns are present even if empty.
    Also includes employees with no exam records (left-join behavior).
    """
    # fetch exam records
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT p_no, name, exam_type, exam_date, marks FROM exam_marks")
        rows = cur.fetchall()

    # Build a DataFrame if rows exist
    if rows:
        df = pd.DataFrame(rows, columns=["p_no", "name", "exam_type", "exam_date", "marks"])
    else:
        df = pd.DataFrame(columns=["p_no", "name", "exam_type", "exam_date", "marks"])

    # normalize and parse
    if not df.empty:
        df["exam_type_norm"] = df["exam_type"].apply(lambda x: normalize_exam_type(x) if pd.notna(x) else None)
        def split_norm(x):
            if not isinstance(x, str):
                return (None, None)
            if "_" in x:
                g, p = x.split("_", 1)
                return (g, p)
            return (None, None)
        df[["group", "part"]] = df["exam_type_norm"].apply(lambda x: pd.Series(split_norm(x)))
        df["exam_date_parsed"] = pd.to_datetime(df["exam_date"], errors="coerce")
        df["p_no"] = df["p_no"].astype(str)
        df["name"] = df["name"].fillna("").astype(str)
    else:
        df["exam_type_norm"] = pd.Series(dtype=str)
        df["group"] = pd.Series(dtype=str)
        df["part"] = pd.Series(dtype=str)
        df["exam_date_parsed"] = pd.Series(dtype="datetime64[ns]")

    data = {}
    canonical_parts = _all_part_keys()
    if not df.empty:
        df_sorted = df.sort_values(by=["p_no", "group", "exam_date_parsed"], ascending=[True, True, False])
        for _, r in df_sorted.iterrows():
            p = r["p_no"]
            name = r["name"]
            grp = r.get("group") or (r.get("exam_type_norm") and r["exam_type_norm"].split("_",1)[0])
            part = r.get("part")
            if not grp or not part:
                continue
            ed = None if pd.isna(r["exam_date_parsed"]) else r["exam_date_parsed"].date().isoformat()
            marks = None if pd.isna(r["marks"]) else r["marks"]
            if p not in data:
                rec = {"p_no": p, "name": name or ""}
                for g, partk in canonical_parts:
                    rec[f"{g}_{partk}_marks"] = None
                    rec[f"{g}_{partk}_date"] = None
                data[p] = rec
            marks_key = f"{grp}_{part}_marks"
            date_key = f"{grp}_{part}_date"
            if data[p].get(marks_key) is None:
                data[p][marks_key] = marks
                data[p][date_key] = ed
            if not data[p]["name"] and name:
                data[p]["name"] = name

    # include employees even if they have no exam rows
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT p_no, name FROM employees")
        for e_pno, e_name in cur.fetchall():
            e_pno = str(e_pno)
            if e_pno not in data:
                rec = {"p_no": e_pno, "name": e_name or ""}
                for g, partk in canonical_parts:
                    rec[f"{g}_{partk}_marks"] = None
                    rec[f"{g}_{partk}_date"] = None
                data[e_pno] = rec

    out = [data[k] for k in sorted(data.keys())]
    return out

def export_exam_summary(path):
    """
    Export the pivot to CSV / XLSX / JSON depending on extension.
    """
    pivot = pivot_exam_summary()
    canonical_parts = _all_part_keys()
    cols = ["p_no", "name"]
    for g, partk in canonical_parts:
        cols.append(f"{g}_{partk}_marks")
        cols.append(f"{g}_{partk}_date")

    if not pivot:
        df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(pivot)
        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]

    save_dataframe_to_file(df, path)
    return path

# -------------------------
# GUI helper: open exam entry window (existing) & marks display window (new)
# -------------------------
def open_exam_window(parent=None, group="Induction"):
    """
    Open a Toplevel window that allows entering exams for a specific group.
    parent: tk root or Toplevel (may be None)
    group: one of keys in EXAM_GROUPS ("Induction","NEEM","NTTF","BTECH","MTECH")
    """
    if group not in EXAM_GROUPS:
        raise ValueError("Unknown exam group: " + str(group))

    win = tk.Toplevel(parent)
    win.title(f"{group} - Enter Exam Marks")
    win.resizable(False, False)

    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    # P. No and Name inputs
    ttk.Label(frm, text="P. No (required)").grid(row=0, column=0, sticky="w", padx=4, pady=4)
    pno_e = ttk.Entry(frm, width=20)
    pno_e.grid(row=0, column=1, padx=4, pady=4)

    ttk.Label(frm, text="Name (optional)").grid(row=0, column=2, sticky="w", padx=4, pady=4)
    name_e = ttk.Entry(frm, width=30)
    name_e.grid(row=0, column=3, padx=4, pady=4)

    parts = EXAM_GROUPS[group]
    widgets = {}
    # create rows for each part
    for i, part in enumerate(parts, start=1):
        ttk.Label(frm, text=f"{part} Date").grid(row=i, column=0, sticky="w", padx=4, pady=2)
        dt = DateEntry(frm, date_pattern="yyyy-mm-dd")
        dt.grid(row=i, column=1, padx=4, pady=2)

        ttk.Label(frm, text=f"{part} Marks").grid(row=i, column=2, sticky="w", padx=4, pady=2)
        marks_e = ttk.Entry(frm, width=12)
        marks_e.grid(row=i, column=3, padx=4, pady=2)

        widgets[part] = {"date": dt, "marks": marks_e}

    # Save button
    def _on_save():
        pno = pno_e.get().strip()
        if not pno:
            messagebox.showerror("Required", "P. No is required to save exam entries.", parent=win)
            return
        name = name_e.get().strip() or None
        saved = 0
        errors = []
        for part, w in widgets.items():
            try:
                try:
                    date_val = w["date"].get_date()
                except Exception:
                    date_str = w["date"].get().strip()
                    date_val = date_str if date_str else None
                marks_raw = w["marks"].get().strip()
                marks_val = None
                if marks_raw:
                    try:
                        marks_val = float(marks_raw)
                    except Exception:
                        marks_val = marks_raw  # keep string if not numeric

                if (not date_val) and (marks_val is None):
                    continue

                try:
                    add_structured_exam(p_no=pno, name=name, group=group, part=part, exam_date=date_val, marks=marks_val)
                    saved += 1
                except Exception as e:
                    errors.append(f"{part}: {e}")
            except Exception as e:
                errors.append(f"{part}: widget/read error: {e}")

        if errors:
            messagebox.showwarning("Saved with errors", f"Saved {saved} entries but some errors occurred:\n" + "\n".join(errors), parent=win)
        else:
            messagebox.showinfo("Saved", f"Saved {saved} entries for P. No {pno}.", parent=win)
            win.destroy()

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=len(parts) + 2, column=0, columnspan=4, pady=(8,4))
    ttk.Button(btn_frame, text="Save", command=_on_save).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side="left", padx=6)

    # center window relative to parent if possible
    try:
        win.update_idletasks()
        if parent:
            x = parent.winfo_rootx() + 50
            y = parent.winfo_rooty() + 50
            win.geometry(f"+{x}+{y}")
    except Exception:
        pass

    return win

def open_marks_window(parent=None, group="Induction"):
    """
    Open a Toplevel window that displays marks for all employees for a specific group.
    Shows columns: p_no, name, and for each part in the group -> <Part>_marks and <Part>_date
    """
    if group not in EXAM_GROUPS:
        raise ValueError("Unknown exam group: " + str(group))

    win = tk.Toplevel(parent)
    win.title(f"{group} - Marks Display")
    win.geometry("900x600")

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill="both", expand=True)

    # Controls: refresh and export
    ctrl = ttk.Frame(frm)
    ctrl.pack(side="top", fill="x", pady=(0,6))
    refresh_btn = ttk.Button(ctrl, text="Refresh", command=lambda: _populate())
    refresh_btn.pack(side="left", padx=4)
    export_btn = ttk.Button(ctrl, text="Export", command=lambda: _export())
    export_btn.pack(side="left", padx=4)

    # Treeview
    tree_frame = ttk.Frame(frm)
    tree_frame.pack(fill="both", expand=True)

    parts = EXAM_GROUPS[group]
    # build column list
    cols = ["p_no", "name"]
    for part in parts:
        cols.append(f"{part}_marks")
        cols.append(f"{part}_date")

    tv = ttk.Treeview(tree_frame, columns=cols, show="headings")
    # add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tv.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tv.xview)
    tv.configure(yscroll=vsb.set, xscroll=hsb.set)
    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, columnspan=2, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    for c in cols:
        header = c
        # make headers nicer for part columns
        if c.endswith("_marks"):
            header = c.replace("_marks", " Marks")
        if c.endswith("_date"):
            header = c.replace("_date", " Date")
        tv.heading(c, text=header)
        tv.column(c, width=120, anchor="w")

    def _populate():
        # Clear
        for r in tv.get_children():
            tv.delete(r)
        pivot = pivot_exam_summary()
        # build rows with only group columns
        for row in pivot:
            pno = row.get("p_no")
            name = row.get("name")
            vals = [pno, name]
            for part in parts:
                vals.append(row.get(f"{group}_{part}_marks"))
                vals.append(row.get(f"{group}_{part}_date"))
            tv.insert("", "end", values=vals)

    def _export():
        pivot = pivot_exam_summary()
        # create DataFrame with only group columns
        rows_out = []
        for row in pivot:
            rec = {"p_no": row.get("p_no"), "name": row.get("name")}
            for part in parts:
                rec[f"{part}marks"] = row.get(f"{group}_{part}_marks")
                rec[f"{part}date"] = row.get(f"{group}_{part}_date")
            rows_out.append(rec)
        df = pd.DataFrame(rows_out)
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV",".csv"),("Excel",".xlsx"),("JSON","*.json")])
        if not path:
            return
        save_dataframe_to_file(df, path)
        messagebox.showinfo("Export", f"{group} marks exported to {path}", parent=win)

    _populate()
    return win

# -------------------------
# GUI helper: bulk upload per group/part
# -------------------------
def open_bulk_upload_window(parent=None, group="Induction", part=None):
    """
    Open a small window allowing user to select a file and bulk upload for a specific group+part.
    If part is None, user will be able to choose part from dropdown (useful for groups with many parts).
    """
    if group not in EXAM_GROUPS:
        raise ValueError("Unknown exam group: " + str(group))

    win = tk.Toplevel(parent)
    title_part = part if part else "Select Part"
    win.title(f"{group} - Bulk Upload ({title_part})")
    win.resizable(False, False)
    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text=f"Group: {group}").grid(row=0, column=0, sticky="w", padx=4, pady=4)

    part_var = tk.StringVar(value=part or EXAM_GROUPS[group][0])
    if part is None:
        ttk.Label(frm, text="Part:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        part_cb = ttk.Combobox(frm, values=EXAM_GROUPS[group], textvariable=part_var, state="readonly")
        part_cb.grid(row=1, column=1, padx=4, pady=4)
    else:
        ttk.Label(frm, text=f"Part: {part}").grid(row=1, column=0, sticky="w", padx=4, pady=4)

    file_path_var = tk.StringVar()

    def _choose_file():
        p = filedialog.askopenfilename(filetypes=[("All supported","*.csv *.xlsx *.xls *.json"),("CSV",".csv"),("Excel",".xlsx .xls"),("JSON",".json")])
        if p:
            file_path_var.set(p)
            fp_label.config(text=os.path.basename(p))

    ttk.Button(frm, text="Choose File", command=_choose_file).grid(row=2, column=0, padx=4, pady=6)
    fp_label = ttk.Label(frm, text="No file selected", width=40)
    fp_label.grid(row=2, column=1, columnspan=2, sticky="w", padx=4, pady=6)

    def _do_upload():
        fp = file_path_var.get()
        if not fp:
            messagebox.showerror("No file", "Please choose a file to upload.", parent=win); return
        sel_part = part_var.get()
        try:
            cnt = bulk_upload_for(group, sel_part, fp)
            messagebox.showinfo("Bulk Upload", f"Inserted {cnt} rows for {group} {sel_part}.", parent=win)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload: {e}", parent=win)

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=(8,4))
    ttk.Button(btn_frame, text="Upload", command=_do_upload).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side="left", padx=6)

    return win
