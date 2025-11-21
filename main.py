import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkcalendar import DateEntry
import datetime
import os
import sys
import json
import random
import db
import auth
import employee, attendance, separation, exam
from utils import load_dataframe_from_file, save_dataframe_to_file
db.init_db()
DEFAULT_SHOPS = [
    "Paint Shop", "Press Shop", "Body Shop", "Assembly Shop",
    "Welding Shop", "Stamping Shop", "Quality", "Logistics",
    "Maintenance", "Tool Room", "Machine Shop", "Electrical Shop"
]
DEFAULT_CATEGORIES = ["NEEM", "NTTF", "BTECH", "MTECH"]
SETTINGS_FILENAME = os.path.join(os.path.dirname(__file__), "app_settings.json")
class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        ttk.Label(self, text="Username").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.u_entry = ttk.Entry(self)
        self.u_entry.grid(row=0, column=1, padx=8, pady=8)
        ttk.Label(self, text="Password").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.p_entry = ttk.Entry(self, show="*")
        self.p_entry.grid(row=1, column=1, padx=8, pady=8)
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 8))
        ttk.Button(btn_frame, text="Login", command=self._on_login).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side="left", padx=6)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.u_entry.focus_set()
    def _on_login(self):
        username = self.u_entry.get().strip()
        password = self.p_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Login", "Enter username & password")
            return
        if auth.authenticate(username, password):
            self.result = {"username": username, "role": auth.get_role(username)}
            self.destroy()
        else:
            messagebox.showerror("Login", "Invalid credentials")
    def _on_cancel(self):
        self.result = None
        self.destroy()
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management & Attendance - Company")
        self.geometry("1180x740")
        self._load_settings()
        login = LoginDialog(self)
        self.wait_window(login)
        if not login.result:
            messagebox.showinfo("Exit", "Login required. Exiting.")
            self.destroy()
            sys.exit(0)
        self.current_user = login.result["username"]
        self.user_role = login.result["role"]
        self.is_admin = (self.user_role == "admin")
        self._build_ui()
    def _load_settings(self):
        """
        Load shops and categories from SETTINGS_FILENAME if present, otherwise use defaults.
        """
        self.shops = list(DEFAULT_SHOPS)
        self.categories = list(DEFAULT_CATEGORIES)
        try:
            if os.path.exists(SETTINGS_FILENAME):
                with open(SETTINGS_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data.get("shops"), list) and data["shops"]:
                    self.shops = data["shops"]
                if isinstance(data.get("categories"), list) and data["categories"]:
                    self.categories = data["categories"]
        except Exception:
            pass
    def _save_settings(self):
        """
        Persist current shops and categories to SETTINGS_FILENAME.
        """
        try:
            data = {"shops": self.shops, "categories": self.categories}
            with open(SETTINGS_FILENAME, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("Settings save", f"Failed to save settings: {e}")
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.emp_frame = ttk.Frame(nb)
        self.att_frame = ttk.Frame(nb)
        self.sep_frame = ttk.Frame(nb)
        self.exam_frame = ttk.Frame(nb)
        nb.add(self.emp_frame, text="Employees")
        nb.add(self.att_frame, text="Attendance")
        nb.add(self.sep_frame, text="Separation")
        nb.add(self.exam_frame, text="Exams")
        self._build_employee_tab()
        self._build_attendance_tab()
        self._build_separation_tab()
        self._build_exam_tab()
    def _build_employee_tab(self):
        f = self.emp_frame
        left = ttk.Frame(f, width=360)
        left.pack(side="left", fill="y", padx=10, pady=10)
        right = ttk.Frame(f)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ttk.Label(left, text="P. No (ID)").pack(anchor="w")
        self.e_pno = ttk.Entry(left)
        self.e_pno.pack(fill="x")
        ttk.Label(left, text="Name").pack(anchor="w")
        self.e_name = ttk.Entry(left)
        self.e_name.pack(fill="x")
        ttk.Label(left, text="Phone").pack(anchor="w")
        self.e_phone = ttk.Entry(left)
        self.e_phone.pack(fill="x")
        ttk.Label(left, text="Date of Birth").pack(anchor="w")
        self.e_dob = DateEntry(left, date_pattern="yyyy-mm-dd")
        self.e_dob.pack(fill="x")
        ttk.Label(left, text="Date of Joining").pack(anchor="w")
        self.e_doj = DateEntry(left, date_pattern="yyyy-mm-dd")
        self.e_doj.pack(fill="x")
        ttk.Label(left, text="End Date").pack(anchor="w")
        self.e_end = DateEntry(left, date_pattern="yyyy-mm-dd")
        self.e_end.pack(fill="x")
        ttk.Label(left, text="Ticket No").pack(anchor="w")
        self.e_ticket = ttk.Entry(left)
        self.e_ticket.pack(fill="x")
        ttk.Label(left, text="Shop").pack(anchor="w")
        shop_frame = ttk.Frame(left)
        shop_frame.pack(fill="x")
        self.e_shop = ttk.Combobox(shop_frame, values=self.shops)
        self.e_shop.pack(side="left", fill="x", expand=True)
        ttk.Button(shop_frame, text="+", width=3, command=self.add_shop).pack(side="left", padx=(6, 0))
        ttk.Label(left, text="Category").pack(anchor="w")
        cat_frame = ttk.Frame(left)
        cat_frame.pack(fill="x")
        self.e_category = ttk.Combobox(cat_frame, values=self.categories, state="readonly")
        default_cat = "NEEM" if "NEEM" in self.categories else (self.categories[0] if self.categories else "")
        self.e_category.set(default_cat)
        self.e_category.pack(side="left", fill="x", expand=True)
        ttk.Button(cat_frame, text="+", width=3, command=self.add_category).pack(side="left", padx=(6, 0))
        filt_frame = ttk.LabelFrame(left, text="Filter employees")
        filt_frame.pack(fill="x", pady=(8, 6))
        ttk.Label(filt_frame, text="Shop").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.filter_shop = ttk.Combobox(filt_frame, values=[""] + self.shops, state="readonly", width=20)
        self.filter_shop.set("")  # empty = all
        self.filter_shop.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(filt_frame, text="Category").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.filter_category = ttk.Combobox(filt_frame, values=[""] + self.categories, state="readonly", width=20)
        self.filter_category.set("")  # empty = all
        self.filter_category.grid(row=1, column=1, padx=4, pady=4)
        btns_frame = ttk.Frame(filt_frame)
        btns_frame.grid(row=2, column=0, columnspan=2, pady=(6, 4))
        ttk.Button(btns_frame, text="Apply Filter", command=self.refresh_employee_list).pack(side="left", padx=6)
        ttk.Button(btns_frame, text="Clear Filters", command=self.clear_employee_filters).pack(side="left", padx=6)
        ttk.Button(left, text="Add / Update", command=self.add_update_employee).pack(fill="x", pady=(8, 2))
        ttk.Button(left, text="Export Employees", command=self.export_employees).pack(fill="x", pady=2)
        self.emp_bulk_btn = ttk.Button(left, text="Bulk Upload (CSV/XLSX/JSON)", command=self.bulk_upload_employees)
        self.emp_delete_btn = ttk.Button(left, text="Delete Selected Employee", command=self.delete_selected_employee)
        self.emp_delete_all_btn = ttk.Button(left, text="Delete All Employees", command=self.delete_all_employees)
        self.emp_bulk_btn.pack(fill="x", pady=2)
        self.emp_delete_btn.pack(fill="x", pady=2)
        self.emp_delete_all_btn.pack(fill="x", pady=2)
        ttk.Button(left, text="Refresh List", command=self.refresh_employee_list).pack(fill="x", pady=2)
        if not self.is_admin:
            self.emp_bulk_btn.configure(state="disabled")
            self.emp_delete_btn.configure(state="disabled")
            self.emp_delete_all_btn.configure(state="disabled")
        cols = ("p_no", "name", "phone", "dob", "doj", "end_date", "ticket_no", "shop", "category")
        self.emp_tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            self.emp_tree.heading(c, text=c)
            self.emp_tree.column(c, width=120, anchor="w")
        self.emp_tree.pack(fill="both", expand=True)
        self.emp_tree.bind("<Double-1>", self.on_emp_double_click)
        self.refresh_employee_list()
    def add_shop(self):
        val = simpledialog.askstring("Add Shop", "Enter new shop name:", parent=self)
        if not val:
            return
        val = val.strip()
        if not val:
            messagebox.showwarning("Invalid", "Shop name cannot be empty.")
            return
        if val in self.shops:
            messagebox.showinfo("Exists", "Shop already exists.")
            return
        self.shops.append(val)
        self.e_shop["values"] = self.shops
        self.filter_shop["values"] = [""] + self.shops
        self._save_settings()
        messagebox.showinfo("Added", f"Shop '{val}' added.")
    def add_category(self):
        val = simpledialog.askstring("Add Category", "Enter new category name:", parent=self)
        if not val:
            return
        val = val.strip()
        if not val:
            messagebox.showwarning("Invalid", "Category name cannot be empty.")
            return
        if val in self.categories:
            messagebox.showinfo("Exists", "Category already exists.")
            return
        self.categories.append(val)
        self.e_category["values"] = self.categories
        self.filter_category["values"] = [""] + self.categories
        self._save_settings()
        messagebox.showinfo("Added", f"Category '{val}' added.")
    def clear_employee_filters(self):
        self.filter_shop.set("")
        self.filter_category.set("")
        self.refresh_employee_list()
    def add_update_employee(self):
        pno = self.e_pno.get().strip()
        name = self.e_name.get().strip()
        if not pno or not name:
            messagebox.showerror("Required", "P. No and Name are required.")
            return
        try:
            category_val = self.e_category.get().strip() or None
            employee.add_employee(
                p_no=pno,
                name=name,
                phone=self.e_phone.get().strip() or None,
                dob=self.e_dob.get_date(),
                doj=self.e_doj.get_date(),
                end_date=self.e_end.get_date(),
                ticket_no=self.e_ticket.get().strip() or None,
                shop=self.e_shop.get() or None,
                category=category_val
            )
            messagebox.showinfo("OK", "Employee saved.")
            self.refresh_employee_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def refresh_employee_list(self):
        for r in self.emp_tree.get_children():
            self.emp_tree.delete(r)
        shop_filter = self.filter_shop.get().strip() or None
        category_filter = self.filter_category.get().strip() or None
        rows = employee.list_employees(shop=shop_filter, category=category_filter)
        for row in rows:
            self.emp_tree.insert("", "end", values=(
                row.get("p_no"),
                row.get("name"),
                row.get("phone"),
                row.get("dob"),
                row.get("doj"),
                row.get("end_date"),
                row.get("ticket_no"),
                row.get("shop"),
                row.get("category", "")
            ))
    def on_emp_double_click(self, event):
        item = self.emp_tree.selection()
        if not item:
            return
        vals = self.emp_tree.item(item[0])["values"]
        self.e_pno.delete(0, tk.END)
        self.e_pno.insert(0, vals[0])
        self.e_name.delete(0, tk.END)
        self.e_name.insert(0, vals[1])
        self.e_phone.delete(0, tk.END)
        self.e_phone.insert(0, vals[2] or "")
        try:
            if vals[3]:
                self.e_dob.set_date(vals[3])
            if vals[4]:
                self.e_doj.set_date(vals[4])
            if vals[5]:
                self.e_end.set_date(vals[5])
        except Exception:
            pass
        self.e_ticket.delete(0, tk.END)
        self.e_ticket.insert(0, vals[6] or "")
        self.e_shop.set(vals[7] or "")
        cat_val = vals[8] if len(vals) > 8 and vals[8] else (self.categories[0] if self.categories else "")
        if cat_val not in self.categories:
            self.categories.append(cat_val)
            self.e_category["values"] = self.categories
            self.filter_category["values"] = [""] + self.categories
        self.e_category.set(cat_val)
    def delete_selected_employee(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can delete employees.")
            return
        sel = self.emp_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select employee to delete in the list.")
            return
        vals = self.emp_tree.item(sel[0])["values"]
        pno = vals[0]
        if messagebox.askyesno("Confirm", f"Delete employee {pno} and all related records?"):
            try:
                employee.delete_employee(pno)
                messagebox.showinfo("OK", "Deleted.")
                self.refresh_employee_list()
                self.refresh_attendance_view()
                self.refresh_separation_list()
                self.refresh_exam_view()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    def delete_all_employees(self):
        """
        Handler for the 'Delete All Employees' button.
        Admin-only. Shows a strong confirmation prompt.
        """
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can delete all employees.")
            return
        confirm = messagebox.askyesno(
            "Confirm DELETE ALL",
            "This will PERMANENTLY DELETE ALL EMPLOYEE records and cannot be undone.\n\n"
            "Are you absolutely sure you want to proceed?"
        )
        if not confirm:
            return
        second = simpledialog.askstring("Type CONFIRM", "Type CONFIRM to proceed with deleting all employees:", parent=self)
        if not second or second.strip().upper() != "CONFIRM":
            messagebox.showinfo("Cancelled", "Delete all employees cancelled.")
            return
        try:
            try:
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(os.path.dirname(__file__), f"employees_backup_{ts}.csv")
                employee.export_employees(backup_path)
            except Exception:
                backup_path = None
            employee.delete_all_employees()
            msg = "All employees deleted."
            if backup_path:
                msg += f"\nBackup saved to: {backup_path}"
            messagebox.showinfo("Done", msg)
            self.refresh_employee_list()
            self.refresh_attendance_view()
            self.refresh_separation_list()
            self.refresh_exam_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete all employees: {e}")
    def bulk_upload_employees(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can bulk upload.")
            return
        path = filedialog.askopenfilename(title="Select employee file", filetypes=[("Data files", "*.csv *.xls *.xlsx *.json")])
        if not path:
            return
        try:
            count = employee.bulk_upload_employees(path)
            messagebox.showinfo("Bulk Upload", f"Inserted/updated {count} records.")
            self.refresh_employee_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def export_employees(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("JSON", "*.json")])
        if not path:
            return
        try:
            employee.export_employees(path)
            messagebox.showinfo("Export", f"Employees exported to {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
    def _build_attendance_tab(self):
        f = self.att_frame
        top = ttk.Frame(f)
        top.pack(side="top", fill="x", padx=8, pady=8)
        bottom = ttk.Frame(f)
        bottom.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        ttk.Label(top, text="P. No").grid(row=0, column=0, sticky="w")
        self.att_single_pno = ttk.Entry(top, width=12)
        self.att_single_pno.grid(row=0, column=1, padx=4)
        ttk.Label(top, text="Name (optional)").grid(row=0, column=2, sticky="w")
        self.att_single_name = ttk.Entry(top, width=20)
        self.att_single_name.grid(row=0, column=3, padx=4)
        ttk.Label(top, text="Date").grid(row=0, column=4, sticky="w")
        self.att_date = DateEntry(top, date_pattern="yyyy-mm-dd")
        self.att_date.grid(row=0, column=5, padx=4)
        ttk.Label(top, text="Status").grid(row=0, column=6, sticky="w")
        self.att_status = ttk.Combobox(top, values=["Present", "Absent", "Leave"], width=10)
        self.att_status.grid(row=0, column=7, padx=4)
        ttk.Button(top, text="Add Attendance (Single)", command=self.add_single_attendance).grid(row=0, column=8, padx=6)
        self.create_missing_single_var = tk.BooleanVar(value=False)
        self.create_missing_chk = ttk.Checkbutton(top, text="Create missing employee if not found (admin only)", variable=self.create_missing_single_var)
        self.create_missing_chk.grid(row=1, column=0, columnspan=5, sticky="w", pady=(6, 0))
        if not self.is_admin:
            self.create_missing_chk.state(["disabled"])
        ttk.Label(top, text="View Date").grid(row=1, column=6, sticky="w")
        self.view_date = DateEntry(top, date_pattern="yyyy-mm-dd")
        self.view_date.set_date(datetime.date.today())
        self.view_date.grid(row=1, column=7, padx=4)
        ttk.Button(top, text="View Day Attendance", command=self.view_attendance_for_day).grid(row=1, column=8, padx=4)
        ttk.Label(top, text="From").grid(row=2, column=0, sticky="w")
        self.filter_from = DateEntry(top, date_pattern="yyyy-mm-dd")
        self.filter_from.grid(row=2, column=1, padx=4)
        ttk.Label(top, text="To").grid(row=2, column=2, sticky="w")
        self.filter_to = DateEntry(top, date_pattern="yyyy-mm-dd")
        self.filter_to.grid(row=2, column=3, padx=4)
        ttk.Label(top, text="Filter employees who took exactly (Leave)").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.leave_day_count = ttk.Spinbox(top, from_=1, to=100, width=5)
        self.leave_day_count.grid(row=3, column=1, sticky="w", pady=(6, 0))
        ttk.Button(top, text="Filter by Leave Count", command=self.filter_by_leave_count).grid(row=3, column=2, padx=4, pady=(6, 0))
        ttk.Label(top, text="Filter employees who took exactly (Absent)").grid(row=3, column=3, sticky="w", pady=(6, 0))
        self.absent_day_count = ttk.Spinbox(top, from_=1, to=100, width=5)
        self.absent_day_count.grid(row=3, column=4, sticky="w", pady=(6, 0))
        ttk.Button(top, text="Filter by Absent Count", command=self.filter_by_absent_count).grid(row=3, column=5, padx=4, pady=(6, 0))
        ttk.Label(top, text="Sort by").grid(row=2, column=4, sticky="e")
        self.sort_by_cb = ttk.Combobox(top, values=["", "absent", "leave"], width=10)
        self.sort_by_cb.grid(row=2, column=5, padx=4)
        ttk.Button(top, text="Get Summary", command=self.refresh_attendance_view).grid(row=2, column=6, padx=4)
        self.att_bulk_btn = ttk.Button(top, text="Bulk Upload Attendance", command=self.bulk_upload_attendance)
        self.att_bulk_btn.grid(row=0, column=9, padx=4)
        ttk.Button(top, text="Export Summary", command=self.export_attendance_summary).grid(row=2, column=7, padx=4)
        gen_frame = ttk.LabelFrame(top, text="Auto-generate Attendance")
        gen_frame.grid(row=4, column=0, columnspan=11, sticky="ew", pady=(8, 6), padx=2)
        ttk.Label(gen_frame, text="From").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.gen_from = DateEntry(gen_frame, date_pattern="yyyy-mm-dd")
        self.gen_from.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(gen_frame, text="To").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.gen_to = DateEntry(gen_frame, date_pattern="yyyy-mm-dd")
        self.gen_to.grid(row=0, column=3, padx=6, pady=6)
        ttk.Label(gen_frame, text="Present %").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.auto_present = ttk.Entry(gen_frame, width=6)
        self.auto_present.insert(0, "85")
        self.auto_present.grid(row=0, column=5, padx=6, pady=6)
        ttk.Label(gen_frame, text="Absent %").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        self.auto_absent = ttk.Entry(gen_frame, width=6)
        self.auto_absent.insert(0, "10")
        self.auto_absent.grid(row=0, column=7, padx=6, pady=6)
        ttk.Label(gen_frame, text="Leave %").grid(row=0, column=8, padx=6, pady=6, sticky="w")
        self.auto_leave = ttk.Entry(gen_frame, width=6)
        self.auto_leave.insert(0, "5")
        self.auto_leave.grid(row=0, column=9, padx=6, pady=6)
        ttk.Label(gen_frame, text="Shop").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.gen_shop_cb = ttk.Combobox(gen_frame, values=["All"] + self.shops, state="readonly", width=18)
        self.gen_shop_cb.set("All")
        self.gen_shop_cb.grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(gen_frame, text="Category").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.gen_cat_cb = ttk.Combobox(gen_frame, values=["All"] + self.categories, state="readonly", width=18)
        self.gen_cat_cb.set("All")
        self.gen_cat_cb.grid(row=1, column=3, padx=6, pady=6)
        self.gen_create_missing = tk.BooleanVar(value=False)
        self.gen_create_missing_chk = ttk.Checkbutton(gen_frame, text="Create missing employees (if any)", variable=self.gen_create_missing)
        self.gen_create_missing_chk.grid(row=1, column=4, columnspan=3, padx=6, pady=6, sticky="w")
        if not self.is_admin:
            self.gen_create_missing_chk.state(["disabled"])
        ttk.Button(gen_frame, text="Auto Generate", command=self.auto_generate_button).grid(row=1, column=8, padx=6, pady=6)
        ttk.Button(gen_frame, text="Preview Sample (1 day)", command=self.preview_auto_sample).grid(row=1, column=9, padx=6, pady=6)
        self.att_emp_bulk_btn = ttk.Button(top, text="Bulk Upload Employees (to Employees table)", command=self.bulk_upload_employees_from_att_tab)
        self.att_emp_bulk_btn.grid(row=0, column=10, padx=6)
        if not self.is_admin:
            self.att_bulk_btn.configure(state="disabled")
            self.att_emp_bulk_btn.configure(state="disabled")
        cols = ("p_no", "name", "present", "absent", "leave")
        self.att_tree = ttk.Treeview(bottom, columns=cols, show="headings")
        for c in cols:
            self.att_tree.heading(c, text=c)
            self.att_tree.column(c, width=150, anchor="w")
        self.att_tree.pack(fill="both", expand=True)
        self.refresh_attendance_view()
    def add_single_attendance(self):
        pno = self.att_single_pno.get().strip()
        name = self.att_single_name.get().strip()
        date = self.att_date.get_date()
        status = self.att_status.get().strip()
        if not pno:
            messagebox.showerror("Required", "P. No is required.")
            return
        if not status:
            messagebox.showerror("Required", "Status is required.")
            return
        with db.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM employees WHERE p_no = ?", (pno,))
            exists = cur.fetchone()[0] > 0
        create_missing = bool(self.create_missing_single_var.get())
        if not exists and create_missing:
            if not self.is_admin:
                messagebox.showwarning("Permission", "Only admin can create missing employees.")
                return
            create_name = name if name else f"Employee_{pno}"
            try:
                employee.add_employee(p_no=pno, name=create_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create employee: {e}")
                return
        if not exists and not create_missing:
            messagebox.showwarning("Missing employee", "Employee not found. Either create the employee first or enable 'Create missing' checkbox (admin only).")
            return
        try:
            attendance.update_attendance(pno, date, status)
            messagebox.showinfo("OK", f"Attendance set for {pno} on {date}")
            self.refresh_attendance_view()
            self.refresh_employee_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def refresh_attendance_view(self):
        for r in self.att_tree.get_children():
            self.att_tree.delete(r)
        date_from = self.filter_from.get_date()
        date_to = self.filter_to.get_date()
        sort_by = self.sort_by_cb.get().strip() or None
        data = attendance.get_attendance_summary(date_from=date_from, date_to=date_to, sort_by=sort_by)
        for row in data:
            self.att_tree.insert("", "end", values=(row["p_no"], row["name"], row["present"], row["absent"], row["leave"]))
    def view_attendance_for_day(self):
        try:
            date_val = self.view_date.get_date()
        except Exception:
            messagebox.showerror("Date", "Select a valid date.")
            return
        rows = attendance.get_attendance_for_date(date_val)
        if not rows:
            messagebox.showinfo("Result", "No employees found.")
            return
        win = tk.Toplevel(self)
        win.title(f"Attendance for {date_val}")
        cols = ("p_no", "name", "status")
        tv = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=180, anchor="w")
        tv.pack(fill="both", expand=True)
        for r in rows:
            tv.insert("", "end", values=(r["p_no"], r["name"], r["status"]))
        def export_day():
            path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("JSON", "*.json")])
            if not path:
                return
            import pandas as pd
            df = pd.DataFrame(rows)
            save_dataframe_to_file(df, path)
            messagebox.showinfo("Export", f"Day attendance exported to {path}")
        ttk.Button(win, text="Export", command=export_day).pack(pady=6)
    def filter_by_leave_count(self):
        try:
            target = int(self.leave_day_count.get())
        except Exception:
            messagebox.showerror("Error", "Enter number for leave days")
            return
        date_from = self.filter_from.get_date()
        date_to = self.filter_to.get_date()
        found = attendance.find_employees_with_leave_count(target, date_from=date_from, date_to=date_to)
        if not found:
            messagebox.showinfo("Result", "No employees found.")
            return
        win = tk.Toplevel(self)
        win.title(f"Employees with {target} leave days")
        t = ttk.Treeview(win, columns=("p_no", "name", "leave_count"), show="headings")
        for c in ("p_no", "name", "leave_count"):
            t.heading(c, text=c)
        t.pack(fill="both", expand=True)
        for r in found:
            t.insert("", "end", values=(r["p_no"], r["name"], r["leave_count"]))
    def filter_by_absent_count(self):
        try:
            target = int(self.absent_day_count.get())
        except Exception:
            messagebox.showerror("Error", "Enter number for absent days")
            return
        date_from = self.filter_from.get_date()
        date_to = self.filter_to.get_date()
        found = attendance.find_employees_with_absent_count(target, date_from=date_from, date_to=date_to)
        if not found:
            messagebox.showinfo("Result", "No employees found.")
            return
        win = tk.Toplevel(self)
        win.title(f"Employees with {target} absent days")
        t = ttk.Treeview(win, columns=("p_no", "name", "absent_count"), show="headings")
        for c in ("p_no", "name", "absent_count"):
            t.heading(c, text=c)
        t.pack(fill="both", expand=True)
        for r in found:
            t.insert("", "end", values=(r["p_no"], r["name"], r["absent_count"]))
    def bulk_upload_attendance(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can bulk upload.")
            return
        path = filedialog.askopenfilename(title="Select attendance file", filetypes=[("Data files", "*.csv *.xls *.xlsx *.json")])
        if not path:
            return
        create_missing = messagebox.askyesno(
            "Create missing employees?",
            "If the attendance file contains P.Nos that are not in Employees, do you want to automatically create minimal employee entries for them?\n\nYes = create missing employees (will use Name column if present)\nNo = skip attendance rows for unknown P.Nos"
        )
        try:
            inserted, created = attendance.bulk_upload_attendance(path, create_missing=create_missing)
            messagebox.showinfo("Bulk Upload", f"Inserted {inserted} attendance rows.\nCreated {created} new employee(s).")
            self.refresh_attendance_view()
            self.refresh_employee_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def bulk_upload_employees_from_att_tab(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can bulk upload employees.")
            return
        path = filedialog.askopenfilename(title="Select employee file (CSV/XLSX/JSON)", filetypes=[("Data files", "*.csv *.xls *.xlsx *.json")])
        if not path:
            return
        try:
            count = employee.bulk_upload_employees(path)
            messagebox.showinfo("Bulk Upload Employees", f"Inserted/updated {count} employee records.")
            self.refresh_employee_list()
            self.refresh_attendance_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def export_attendance_summary(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("JSON", "*.json")])
        if not path:
            return
        try:
            date_from = self.filter_from.get_date()
            date_to = self.filter_to.get_date()
            sort_by = self.sort_by_cb.get().strip() or None
            attendance.export_attendance_summary(path, date_from=date_from, date_to=date_to, sort_by=sort_by)
            messagebox.showinfo("Export", f"Attendance summary exported to {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
    def auto_generate_button(self):
        try:
            d_from = self.gen_from.get_date()
            d_to = self.gen_to.get_date()
        except Exception:
            messagebox.showerror("Date", "Enter valid 'From' and 'To' dates for generation.")
            return
        if d_to < d_from:
            messagebox.showerror("Date", "'To' date must be same or after 'From' date.")
            return
        try:
            p_val = float(self.auto_present.get())
            a_val = float(self.auto_absent.get())
            l_val = float(self.auto_leave.get())
        except Exception:
            messagebox.showerror("Input", "Enter numeric values for percentages.")
            return
        if p_val + a_val + l_val <= 0:
            messagebox.showerror("Input", "At least one of the percentages must be > 0.")
            return
        shop = self.gen_shop_cb.get()
        if shop == "All":
            shop = None
        cat = self.gen_cat_cb.get()
        if cat == "All":
            cat = None
        create_missing = bool(self.gen_create_missing.get())
        days = (d_to - d_from).days + 1
        employees = employee.list_employees(shop=shop, category=cat)
        if not employees:
            messagebox.showinfo("No employees", "No employees found for the selected shop/category.")
            return
        if not messagebox.askyesno("Confirm", f"Generate attendance for {len(employees)} employees for {days} day(s)?"):
            return
        try:
            res = attendance.auto_generate_attendance(d_from, d_to,
                                                      present_pct=p_val, absent_pct=a_val, leave_pct=l_val,
                                                      shop=shop, category=cat, create_missing=create_missing)
            messagebox.showinfo("Done", f"Auto-generated attendance: inserted={res.get('inserted')} for {res.get('employees_count')} employees over {res.get('dates_count')} days.")
            self.refresh_attendance_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def preview_auto_sample(self):
        try:
            sample_date = self.gen_from.get_date()
        except Exception:
            messagebox.showerror("Date", "Enter a valid sample 'From' date.")
            return
        try:
            p_val = float(self.auto_present.get())
            a_val = float(self.auto_absent.get())
            l_val = float(self.auto_leave.get())
        except Exception:
            messagebox.showerror("Input", "Enter numeric values for percentages.")
            return
        total = p_val + a_val + l_val
        if total <= 0:
            messagebox.showerror("Input", "At least one percentage must be >0.")
            return
        weights = [p_val / total, a_val / total, l_val / total]
        choices = ["Present", "Absent", "Leave"]
        shop = self.gen_shop_cb.get()
        if shop == "All":
            shop = None
        cat = self.gen_cat_cb.get()
        if cat == "All":
            cat = None
        employees = employee.list_employees(shop=shop, category=cat)
        if not employees:
            messagebox.showinfo("No employees", "No employees found for that filter.")
            return
        win = tk.Toplevel(self)
        win.title(f"Sample attendance for {sample_date}")
        cols = ("p_no", "name", "status")
        tv = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=180)
        tv.pack(fill="both", expand=True)
        for emp in employees[:50]:
            status = random.choices(choices, weights=weights, k=1)[0]
            tv.insert("", "end", values=(emp.get("p_no"), emp.get("name"), status))
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)
    def _build_separation_tab(self):
        f = self.sep_frame
        top = ttk.Frame(f)
        top.pack(side="top", fill="x", padx=8, pady=8)
        bottom = ttk.Frame(f)
        bottom.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        ttk.Label(top, text="P. No").grid(row=0, column=0, sticky="w")
        self.sep_pno = ttk.Entry(top)
        self.sep_pno.grid(row=0, column=1, padx=4)
        ttk.Label(top, text="Name").grid(row=0, column=2, sticky="w")
        self.sep_name = ttk.Entry(top)
        self.sep_name.grid(row=0, column=3, padx=4)
        ttk.Label(top, text="Separation Date").grid(row=1, column=0, sticky="w")
        self.sep_date = DateEntry(top, date_pattern="yyyy-mm-dd")
        self.sep_date.grid(row=1, column=1, padx=4)
        ttk.Label(top, text="Reason").grid(row=1, column=2, sticky="w")
        self.sep_reason = ttk.Entry(top)
        self.sep_reason.grid(row=1, column=3, padx=4)
        ttk.Button(top, text="Add Separation", command=self.add_separation_record).grid(row=2, column=0, padx=4, pady=6)
        self.sep_bulk_btn = ttk.Button(top, text="Bulk Upload Separation", command=self.bulk_upload_separations)
        self.sep_bulk_btn.grid(row=2, column=1, padx=4, pady=6)
        self.sep_delete_btn = ttk.Button(top, text="Delete Selected Separation", command=self.delete_selected_separation)
        self.sep_delete_btn.grid(row=2, column=2, padx=4, pady=6)
        ttk.Button(top, text="Export Separations", command=self.export_separations).grid(row=2, column=3, padx=4, pady=6)
        if not self.is_admin:
            self.sep_bulk_btn.configure(state="disabled")
            self.sep_delete_btn.configure(state="disabled")
        cols = ("id", "p_no", "name", "separation_date", "reason")
        self.sep_tree = ttk.Treeview(bottom, columns=cols, show="headings")
        for c in cols:
            self.sep_tree.heading(c, text=c)
            self.sep_tree.column(c, width=160)
        self.sep_tree.pack(fill="both", expand=True)
        self.refresh_separation_list()
    def add_separation_record(self):
        pno = self.sep_pno.get().strip()
        name = self.sep_name.get().strip()
        if not pno or not name:
            messagebox.showerror("Required", "P. No and Name required.")
            return
        try:
            separation.add_separation(pno, name, self.sep_date.get_date(), self.sep_reason.get().strip() or None)
            messagebox.showinfo("OK", "Separation recorded.")
            self.refresh_separation_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def refresh_separation_list(self):
        for r in self.sep_tree.get_children():
            self.sep_tree.delete(r)
        for row in separation.list_separations():
            self.sep_tree.insert("", "end", values=(row["id"], row["p_no"], row["name"], row["separation_date"], row["reason"]))
    def delete_selected_separation(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can delete separation records.")
            return
        sel = self.sep_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select record to delete.")
            return
        vals = self.sep_tree.item(sel[0])["values"]
        rec_id = vals[0]
        if messagebox.askyesno("Confirm", "Delete separation record?"):
            separation.delete_separation(rec_id)
            self.refresh_separation_list()
    def bulk_upload_separations(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can bulk upload.")
            return
        path = filedialog.askopenfilename(title="Select separation file", filetypes=[("Data files", "*.csv *.xls *.xlsx *.json")])
        if not path:
            return
        try:
            count = separation.bulk_upload_separations(path)
            messagebox.showinfo("Bulk Upload", f"Inserted {count} separation rows.")
            self.refresh_separation_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def export_separations(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("JSON", "*.json")])
        if not path:
            return
        try:
            separation.export_separations(path)
            messagebox.showinfo("Export", f"Separations exported to {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
    def _build_exam_tab(self):
        f = self.exam_frame
        top = ttk.Frame(f)
        top.pack(side="top", fill="x", padx=8, pady=8)
        bottom = ttk.Frame(f)
        bottom.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        self.exam_bulk_btn = ttk.Button(top, text="Bulk Upload Exam Marks", command=self.bulk_upload_exams)
        self.exam_bulk_btn.grid(row=0, column=0, padx=4, pady=6)
        ttk.Button(top, text="Export Exam Summary", command=self.export_exam_summary).grid(row=0, column=1, padx=4, pady=6)
        ttk.Button(top, text="Refresh Summary", command=self.refresh_exam_view).grid(row=0, column=2, padx=4, pady=6)
        if not self.is_admin:
            self.exam_bulk_btn.configure(state="disabled")
        group_btn_frame = ttk.Frame(top)
        group_btn_frame.grid(row=1, column=0, columnspan=6, pady=(6, 4), sticky="w")
        col_idx = 0
        for grp in exam.EXAM_GROUPS.keys():
            ttk.Button(group_btn_frame, text=f"Open {grp} Entry", command=lambda g=grp: exam.open_exam_window(self, g)).grid(row=0, column=col_idx, padx=4, pady=2)
            ttk.Button(group_btn_frame, text=f"Show {grp} Marks", command=lambda g=grp: exam.open_marks_window(self, g)).grid(row=1, column=col_idx, padx=4, pady=2)
            col_idx += 1
        bulk_frame = ttk.Frame(top)
        bulk_frame.grid(row=2, column=0, columnspan=6, pady=(6, 4), sticky="w")
        ttk.Label(bulk_frame, text="Per-group Bulk Upload (select part then click):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self._exam_bulk_part_vars = {}
        cidx = 0
        for group, parts in exam.EXAM_GROUPS.items():
            var = tk.StringVar(value=(parts[0] if parts else ""))
            self._exam_bulk_part_vars[group] = var
            ttk.Label(bulk_frame, text=group).grid(row=1, column=cidx * 2, sticky="w", padx=(6, 4))
            cb = ttk.Combobox(bulk_frame, values=parts, textvariable=var, state="readonly", width=10)
            cb.grid(row=1, column=cidx * 2 + 1, padx=(0, 8))
            btn = ttk.Button(bulk_frame, text=f"Bulk Upload {group}", command=lambda g=group, pv=var: exam.open_bulk_upload_window(self, g, pv.get()))
            btn.grid(row=2, column=cidx * 2, columnspan=2, pady=(2, 6), padx=4)
            if not self.is_admin:
                btn.configure(state="disabled")
            cidx += 1
        sub_nb = ttk.Notebook(bottom)
        sub_nb.pack(side="left", fill="both", expand=False, padx=(0, 8), pady=4)
        self._exam_widgets = {}
        for group, parts in exam.EXAM_GROUPS.items():
            frame = ttk.Frame(sub_nb, padding=8)
            sub_nb.add(frame, text=group)
            self._exam_widgets[group] = {}
            for i, part in enumerate(parts):
                ttk.Label(frame, text=f"{part} Date").grid(row=i, column=0, sticky="w", padx=4, pady=2)
                dt = DateEntry(frame, date_pattern="yyyy-mm-dd")
                dt.grid(row=i, column=1, padx=4, pady=2)
                ttk.Label(frame, text=f"{part} Marks").grid(row=i, column=2, sticky="w", padx=4, pady=2)
                marks_e = ttk.Entry(frame, width=10)
                marks_e.grid(row=i, column=3, padx=4, pady=2)
                self._exam_widgets[group][part] = {"date": dt, "marks": marks_e}
            def make_save_fn(g):
                return lambda: self.save_exam_group(g)
            ttk.Button(frame, text="Save " + group, command=make_save_fn(group)).grid(row=len(parts), column=0, columnspan=4, pady=(8, 4))
        self.exam_tree = ttk.Treeview(bottom, show="headings")
        self.exam_tree.pack(side="right", fill="both", expand=True)
        self.refresh_exam_view()
    def save_exam_group(self, group):
        widgets = self._exam_widgets.get(group, {})
        if not widgets:
            messagebox.showwarning("No panel", "No inputs found for group.")
            return
        pno = simpledialog.askstring("P. No", "Enter P. No (employee ID):", parent=self)
        if not pno:
            return
        name = simpledialog.askstring("Name (optional)", "Enter Name (optional):", parent=self)
        written = 0
        errors = []
        for part, w in widgets.items():
            try:
                dt_widget = w["date"]
                marks_widget = w["marks"]
                try:
                    date_val = dt_widget.get_date()
                except Exception:
                    date_val = dt_widget.get().strip() or None
                marks_val = marks_widget.get().strip()
                if (not marks_val) and (not date_val):
                    continue
                marks_to_store = float(marks_val) if marks_val else None
                try:
                    exam.add_structured_exam(p_no=pno, name=name, group=group, part=part, exam_date=date_val, marks=marks_to_store)
                    written += 1
                except Exception as e:
                    errors.append(f"{group} {part}: {e}")
            except Exception as e:
                errors.append(f"Widget error for {group} {part}: {e}")
        if errors:
            messagebox.showwarning("Saved with errors", f"Saved {written} items but some errors occurred:\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Saved", f"Saved {written} exam entries for P. No {pno}.")
        self.refresh_exam_view()
    def refresh_exam_view(self):
        for r in getattr(self, "exam_tree").get_children():
            self.exam_tree.delete(r)
        pivot = exam.pivot_exam_summary()
        if not pivot:
            cols = ["p_no", "name"]
            for g, part in exam._all_part_keys():
                cols.append(f"{g}_{part}_marks")
                cols.append(f"{g}_{part}_date")
        else:
            cols = list(pivot[0].keys())
        self.exam_tree["columns"] = cols
        for c in cols:
            self.exam_tree.heading(c, text=c)
            self.exam_tree.column(c, width=110, anchor="w")
        for row in pivot:
            vals = [row.get(c) for c in cols]
            self.exam_tree.insert("", "end", values=vals)
    def bulk_upload_exams(self):
        if not self.is_admin:
            messagebox.showwarning("Permission", "Only admin can bulk upload.")
            return
        path = filedialog.askopenfilename(title="Select exams file", filetypes=[("Data files", "*.csv *.xls *.xlsx *.json")])
        if not path:
            return
        try:
            count = exam.bulk_upload_exams(path)
            messagebox.showinfo("Bulk Upload", f"Inserted {count} exam rows.")
            self.refresh_exam_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def export_exam_summary(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("JSON", "*.json")])
        if not path:
            return
        try:
            exam.export_exam_summary(path)
            messagebox.showinfo("Export", f"Exam summary exported to {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
if __name__ == "__main__":
    app = App()
    app.mainloop()