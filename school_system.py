import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import datetime
import hashlib
import random
import string
import os

# Password Generator Function
def generate_password():
    characters = string.ascii_letters + string.digits + "@#%&"
    return ''.join(random.choice(characters) for _ in range(12))

class SchoolSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management System - Designed by Aniq Abbasi")
        
        # Make window fullscreen
        self.state('zoomed')  # For Windows
        # Alternatively use: self.attributes('-fullscreen', True)
        
        self.configure(bg="#f4f6f9")
        
        # Add escape key binding to exit fullscreen
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False))
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        
        self.is_fullscreen = True
        
        self.data_file = "school_data.json"
        
        # Load or Create Data
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
        else:
            self.data = {
                "users": {},
                "next_student_id": 1000001,
                "results": {},
                "login_logs": []
            }
            self.save_data()

        self.current_user = None
        
        # First Time Admin Creation
        if "Aniq Abbasi" not in self.data["users"]:
            self.first_time_admin_setup()
        else:
            self.show_login_screen()
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
    
    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)
    
    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def log_login(self, user_id, role):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data["login_logs"].append({"time": timestamp, "id": user_id, "role": role})
        self.save_data()

    # ===================== FIRST TIME SETUP =====================
    def first_time_admin_setup(self):
        self.clear_screen()
        main_frame = tk.Frame(self, bg="#f4f6f9")
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="SCHOOL MANAGEMENT SYSTEM", font=("Helvetica", 32, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=80)
        tk.Label(main_frame, text="First Time Setup", font=("Arial", 20), bg="#f4f6f9", fg="#e74c3c").pack(pady=10)
        tk.Label(main_frame, text="Creating Default Admin Account", font=("Arial", 16), bg="#f4f6f9").pack(pady=30)

        tk.Label(main_frame, text="Admin Name: Aniq Abbasi", font=("Arial", 20, "bold"), bg="#f4f6f9", fg="#27ae60").pack(pady=15)
        tk.Label(main_frame, text="Password: Abbasi984", font=("Arial", 20, "bold"), bg="#f4f6f9", fg="#27ae60").pack(pady=10)

        def create_admin_account():
            self.data["users"]["Aniq Abbasi"] = {
                "role": "admin",
                "name": "Aniq Abbasi",
                "password": hashlib.sha256("Abbasi984".encode()).hexdigest(),
                "hint": "My name + 984"
            }
            self.save_data()
            messagebox.showinfo("Success", "Admin Account Created Successfully!\n\nYou can now login.")
            self.show_login_screen()

        tk.Button(main_frame, text="CREATE ADMIN & CONTINUE", font=("Arial", 18, "bold"), bg="#27ae60", fg="white", width=35, height=2,
                 command=create_admin_account).pack(pady=70)
        
        self.credit_label()

    # ===================== LOGIN SCREEN =====================
    def show_login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(expand=True)

        tk.Label(frame, text="SCHOOL MANAGEMENT SYSTEM", font=("Helvetica", 32, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=90)

        tk.Label(frame, text="User ID", font=("Arial", 18), bg="#f4f6f9").pack(pady=(40,10))
        self.entry_id = tk.Entry(frame, font=("Arial", 18), width=38, justify="center", relief="solid", bd=2)
        self.entry_id.pack()
        self.entry_id.insert(0, "Aniq Abbasi")

        tk.Label(frame, text="Password", font=("Arial", 18), bg="#f4f6f9").pack(pady=(30,10))
        self.entry_pass = tk.Entry(frame, font=("Arial", 18), width=38, show="*", justify="center", relief="solid", bd=2)
        self.entry_pass.pack()
        self.entry_pass.insert(0, "Abbasi984")

        btn_frame = tk.Frame(frame, bg="#f4f6f9")
        btn_frame.pack(pady=50)

        tk.Button(btn_frame, text="LOGIN", font=("Arial", 18, "bold"), bg="#27ae60", fg="white", width=20, height=2,
                 command=self.login).pack(pady=15)
        tk.Button(btn_frame, text="Forgot Password?", font=("Arial", 12), bg="#e74c3c", fg="white",
                 command=self.forgot_password).pack()

        self.credit_label()

    def login(self):
        uid = self.entry_id.get().strip()
        pwd = hashlib.sha256(self.entry_pass.get().encode()).hexdigest()

        if uid in self.data["users"] and self.data["users"][uid]["password"] == pwd:
            self.current_user = uid
            role = self.data["users"][uid]["role"]
            self.log_login(uid, role)
            if role == "admin":
                self.admin_dashboard()
            elif role == "teacher":
                self.teacher_dashboard()
            elif role == "student":
                self.student_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid User ID or Password")

    def forgot_password(self):
        uid = simpledialog.askstring("Password Hint", "Enter your User ID:")
        if uid and uid in self.data["users"]:
            hint = self.data["users"][uid].get("hint", "No hint set")
            messagebox.showinfo("Password Hint", f"Hint: {hint}")
        else:
            messagebox.showerror("Error", "User ID not found")

    def credit_label(self):
        tk.Label(self, text="This Program is designed by Aniq Abbasi | Press F11 to toggle fullscreen | ESC to exit fullscreen", 
                 font=("Arial", 11), fg="gray", bg="#f4f6f9").pack(side="bottom", pady=20)

    # ===================== ADMIN DASHBOARD =====================
    def admin_dashboard(self):
        self.clear_screen()
        
        # Create scrollable canvas
        canvas = tk.Canvas(self, bg="#f4f6f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6f9")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind mouse wheel for Linux
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="ADMIN DASHBOARD", font=("Helvetica", 28, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=60)
        tk.Label(scrollable_frame, text="Welcome Aniq Abbasi", font=("Arial", 18), bg="#f4f6f9").pack(pady=10)

        options = [
            ("Register New Teacher", self.register_teacher),
            ("Register New Student", self.register_student),
            ("Manage Teachers", self.manage_teachers),
            ("Manage Students", self.manage_students),
            ("View Login Activity", self.view_login_logs),
            ("Change Admin Password", self.change_admin_password),
            ("Logout", self.show_login_screen)
        ]

        btn_frame = tk.Frame(scrollable_frame, bg="#f4f6f9")
        btn_frame.pack(expand=True, pady=30)

        for text, command in options:
            tk.Button(btn_frame, text=text, font=("Arial", 16), width=45, height=2, bg="#3498db", fg="white", 
                     command=command).pack(pady=15)

        tk.Label(scrollable_frame, text="This Program is designed by Aniq Abbasi | Press F11 to toggle fullscreen | ESC to exit fullscreen", 
                 font=("Arial", 11), fg="gray", bg="#f4f6f9").pack(side="bottom", pady=40)

    def register_teacher(self):
        win = tk.Toplevel(self)
        win.title("Register Teacher")
        win.geometry("600x720")
        win.configure(bg="#f4f6f9")

        tk.Label(win, text="TEACHER REGISTRATION", font=("Helvetica", 20, "bold"), bg="#f4f6f9").pack(pady=40)

        tk.Label(win, text="Full Name", font=("Arial", 14), bg="#f4f6f9").pack(pady=(20,5))
        name_entry = tk.Entry(win, width=45, font=("Arial", 14))
        name_entry.pack()

        tk.Label(win, text="Date of Joining (YYYY-MM-DD)", font=("Arial", 14), bg="#f4f6f9").pack(pady=(25,5))
        doj_entry = tk.Entry(win, width=45, font=("Arial", 14))
        doj_entry.insert(0, str(datetime.date.today()))
        doj_entry.pack()

        tk.Label(win, text="Password", font=("Arial", 14), bg="#f4f6f9").pack(pady=(25,5))
        pw_entry = tk.Entry(win, width=45, font=("Arial", 14), show="*")
        pw_entry.pack()

        tk.Button(win, text="Generate Strong Password", bg="#27ae60", fg="white", font=("Arial", 12),
                 command=lambda: (pw_entry.delete(0, tk.END), pw_entry.insert(0, generate_password()))).pack(pady=10)

        tk.Label(win, text="Password Hint (Optional)", font=("Arial", 14), bg="#f4f6f9").pack(pady=(20,5))
        hint_entry = tk.Entry(win, width=45, font=("Arial", 14))
        hint_entry.pack()

        def save_teacher():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            teacher_id = f"{name.replace(' ', '').lower()}-2026-01-Teacher"
            if teacher_id in self.data["users"]:
                messagebox.showerror("Error", "Teacher already exists")
                return
            password = pw_entry.get()
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be 6+ characters")
                return

            self.data["users"][teacher_id] = {
                "role": "teacher",
                "name": name,
                "doj": doj_entry.get(),
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "hint": hint_entry.get().strip() or "No hint",
                "classes": {}
            }
            self.save_data()
            messagebox.showinfo("Success", f"Teacher Registered Successfully!\n\nID: {teacher_id}\nPassword: {password}")
            win.destroy()

        tk.Button(win, text="REGISTER TEACHER", font=("Arial", 16, "bold"), bg="#27ae60", fg="white", width=35, height=2,
                 command=save_teacher).pack(pady=50)

    def register_student(self):
        win = tk.Toplevel(self)
        win.title("Register Student")
        win.geometry("600x780")
        win.configure(bg="#f4f6f9")

        tk.Label(win, text="STUDENT REGISTRATION", font=("Helvetica", 20, "bold"), bg="#f4f6f9").pack(pady=40)

        tk.Label(win, text="Full Name", font=("Arial", 14), bg="#f4f6f9").pack(pady=(20,5))
        name_entry = tk.Entry(win, width=45, font=("Arial", 14))
        name_entry.pack()

        tk.Label(win, text="Class (1-12)", font=("Arial", 14), bg="#f4f6f9").pack(pady=(25,5))
        class_entry = tk.Entry(win, width=45, font=("Arial", 14))
        class_entry.pack()

        tk.Label(win, text="Date of Joining (YYYY-MM-DD)", font=("Arial", 14), bg="#f4f6f9").pack(pady=(25,5))
        doj_entry = tk.Entry(win, width=45, font=("Arial", 14))
        doj_entry.insert(0, str(datetime.date.today()))
        doj_entry.pack()

        tk.Label(win, text="Password", font=("Arial", 14), bg="#f4f6f9").pack(pady=(25,5))
        pw_entry = tk.Entry(win, width=45, font=("Arial", 14), show="*")
        pw_entry.pack()

        tk.Button(win, text="Generate Password", bg="#27ae60", fg="white", font=("Arial", 12),
                 command=lambda: (pw_entry.delete(0, tk.END), pw_entry.insert(0, generate_password()))).pack(pady=10)

        tk.Label(win, text="Password Hint", font=("Arial", 14), bg="#f4f6f9").pack(pady=(20,5))
        hint_entry = tk.Entry(win, width=45, font=("Arial", 14))
        hint_entry.pack()

        def save_student():
            name = name_entry.get().strip()
            cls = class_entry.get().strip()
            if not name or not cls or not cls.isdigit() or int(cls) not in range(1,13):
                messagebox.showerror("Error", "Valid name and class (1-12) required")
                return
            student_id = f"{name.replace(' ', '').lower()}-{self.data['next_student_id']}"
            self.data["next_student_id"] += 1
            password = pw_entry.get()
            if len(password) < 6:
                messagebox.showerror("Error", "Password too short")
                return

            self.data["users"][student_id] = {
                "role": "student",
                "name": name,
                "class": cls,
                "doj": doj_entry.get(),
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "hint": hint_entry.get().strip() or "No hint"
            }
            self.data["results"][student_id] = {}
            self.save_data()
            messagebox.showinfo("Success", f"Student Registered!\n\nID: {student_id}\nPassword: {password}")
            win.destroy()

        tk.Button(win, text="REGISTER STUDENT", font=("Arial", 16, "bold"), bg="#27ae60", fg="white", width=35, height=2,
                 command=save_student).pack(pady=50)

    def manage_teachers(self):
        win = tk.Toplevel(self)
        win.title("Manage Teachers")
        win.geometry("1000x650")

        tree = ttk.Treeview(win, columns=("ID", "Name", "DOJ"), show="headings")
        tree.heading("ID", text="Teacher ID")
        tree.heading("Name", text="Name")
        tree.heading("DOJ", text="Date of Joining")
        tree.column("ID", width=350)
        tree.column("Name", width=300)
        tree.column("DOJ", width=200)
        tree.pack(fill="both", expand=True, padx=30, pady=30)

        def refresh():
            tree.delete(*tree.get_children())
            for uid, info in self.data["users"].items():
                if info["role"] == "teacher":
                    tree.insert("", "end", values=(uid, info["name"], info["doj"]))

        refresh()

        def delete_teacher():
            selected = tree.selection()
            if selected and messagebox.askyesno("Confirm", "Delete this teacher permanently?"):
                uid = tree.item(selected[0])["values"][0]
                del self.data["users"][uid]
                self.save_data()
                refresh()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Refresh List", bg="#3498db", fg="white", width=20, command=refresh).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Delete Selected", bg="#e74c3c", fg="white", width=20, command=delete_teacher).pack(side="left", padx=20)

    def manage_students(self):
        win = tk.Toplevel(self)
        win.title("Manage Students")
        win.geometry("1000x650")

        tree = ttk.Treeview(win, columns=("ID", "Name", "Class", "DOJ"), show="headings")
        tree.heading("ID", text="Student ID")
        tree.heading("Name", text="Name")
        tree.heading("Class", text="Class")
        tree.heading("DOJ", text="Date of Joining")
        tree.column("ID", width=350)
        tree.column("Name", width=250)
        tree.column("Class", width=100)
        tree.column("DOJ", width=200)
        tree.pack(fill="both", expand=True, padx=30, pady=30)

        def refresh():
            tree.delete(*tree.get_children())
            for uid, info in self.data["users"].items():
                if info["role"] == "student":
                    tree.insert("", "end", values=(uid, info["name"], info["class"], info["doj"]))

        refresh()

        def delete_student():
            selected = tree.selection()
            if selected and messagebox.askyesno("Confirm", "Delete student and all results?"):
                uid = tree.item(selected[0])["values"][0]
                self.data["users"].pop(uid, None)
                self.data["results"].pop(uid, None)
                self.save_data()
                refresh()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Refresh List", bg="#3498db", fg="white", width=20, command=refresh).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Delete Selected", bg="#e74c3c", fg="white", width=20, command=delete_student).pack(side="left", padx=20)

    def view_login_logs(self):
        win = tk.Toplevel(self)
        win.title("Login Activity Log")
        win.geometry("900x600")

        tree = ttk.Treeview(win, columns=("Time", "User ID", "Role"), show="headings")
        tree.heading("Time", text="Login Time")
        tree.heading("User ID", text="User ID")
        tree.heading("Role", text="Role")
        tree.column("Time", width=250)
        tree.column("User ID", width=400)
        tree.column("Role", width=150)
        tree.pack(fill="both", expand=True, padx=30, pady=30)

        for log in reversed(self.data["login_logs"][-100:]):
            tree.insert("", "end", values=(log["time"], log["id"], log["role"]))

    def change_admin_password(self):
        new_pw = simpledialog.askstring("Change Password", "Enter new admin password:", show="*")
        if new_pw and len(new_pw) >= 6:
            self.data["users"]["Aniq Abbasi"]["password"] = hashlib.sha256(new_pw.encode()).hexdigest()
            self.save_data()
            messagebox.showinfo("Success", "Admin password updated successfully")
        elif new_pw:
            messagebox.showerror("Error", "Password must be at least 6 characters")

    # ===================== TEACHER DASHBOARD =====================
    def teacher_dashboard(self):
        self.clear_screen()
        
        # Create scrollable canvas
        canvas = tk.Canvas(self, bg="#f4f6f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6f9")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        name = self.data["users"][self.current_user]["name"]
        tk.Label(scrollable_frame, text=f"WELCOME TEACHER\n{name.upper()}", font=("Helvetica", 26, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=80)

        tk.Button(scrollable_frame, text="Manage Classes & Subjects", font=("Arial", 16), width=50, height=3, bg="#3498db", fg="white",
                 command=self.manage_teacher_classes).pack(pady=20)
        tk.Button(scrollable_frame, text="Enter Student Results", font=("Arial", 16), width=50, height=3, bg="#27ae60", fg="white",
                 command=self.enter_student_results).pack(pady=20)
        tk.Button(scrollable_frame, text="Change My Password", font=("Arial", 16), width=50, height=3, bg="#f39c12", fg="white",
                 command=self.change_own_password).pack(pady=20)
        tk.Button(scrollable_frame, text="Delete My Account", font=("Arial", 16), width=50, height=3, bg="#e74c3c", fg="white",
                 command=self.delete_own_account).pack(pady=20)
        tk.Button(scrollable_frame, text="Logout", font=("Arial", 16), width=50, height=3, bg="#34495e", fg="white",
                 command=self.show_login_screen).pack(pady=50)

        tk.Label(scrollable_frame, text="This Program is designed by Aniq Abbasi | Press F11 to toggle fullscreen | ESC to exit fullscreen", 
                 font=("Arial", 11), fg="gray", bg="#f4f6f9").pack(side="bottom", pady=40)

    def manage_teacher_classes(self):
        win = tk.Toplevel(self)
        win.title("Manage Classes & Subjects")
        win.geometry("1100x800")
        win.configure(bg="#f4f6f9")

        classes = self.data["users"][self.current_user].setdefault("classes", {})

        # Scrollable Canvas
        canvas = tk.Canvas(win, bg="#f4f6f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6f9")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        scrollbar.pack(side="right", fill="y")

        def refresh():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            if not classes:
                tk.Label(scrollable_frame, text="No classes added yet.\nClick below to add your first class.", 
                        font=("Arial", 18), fg="gray", bg="#f4f6f9").pack(pady=200)

            for cls in sorted(classes.keys(), key=int):
                class_box = tk.Frame(scrollable_frame, bg="white", relief="groove", bd=3)
                class_box.pack(fill="x", pady=20, padx=40)

                header = tk.Frame(class_box, bg="white")
                header.pack(fill="x", padx=20, pady=15)
                tk.Label(header, text=f"CLASS {cls}", font=("Arial", 22, "bold"), bg="white", fg="#2c3e50").pack(side="left")
                tk.Button(header, text="Delete Class", font=("Arial", 12), bg="#e74c3c", fg="white",
                         command=lambda c=cls: (classes.pop(c, None), self.save_data(), refresh())).pack(side="right")

                subjects_container = tk.Frame(class_box, bg="white")
                subjects_container.pack(fill="x", padx=50, pady=20)

                if classes[cls]:
                    for subject in classes[cls]:
                        subj_row = tk.Frame(subjects_container, bg="#ecf0f1")
                        subj_row.pack(fill="x", pady=8, padx=20)
                        tk.Label(subj_row, text="• " + subject, font=("Arial", 16), bg="#ecf0f1").pack(side="left", padx=20)
                        tk.Button(subj_row, text="Remove Subject", bg="#c0392b", fg="white",
                                 command=lambda c=cls, s=subject: (classes[c].remove(s), self.save_data(), refresh())).pack(side="right", padx=20)
                else:
                    tk.Label(subjects_container, text="No subjects added to this class", font=("Arial", 14), fg="gray").pack(pady=30)

                tk.Button(subjects_container, text="+ Add Subject to Class " + cls, font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                         command=lambda c=cls: add_subject(c)).pack(side="right", pady=15)

            add_class_frame = tk.Frame(scrollable_frame, bg="#f4f6f9")
            add_class_frame.pack(fill="x", pady=60)
            tk.Button(add_class_frame, text="+ ADD NEW CLASS", font=("Arial", 20, "bold"), bg="#27ae60", fg="white", width=40, height=3,
                     command=add_new_class).pack(expand=True)

        def add_subject(cls):
            subject = simpledialog.askstring("Add Subject", f"Enter subject name for Class {cls}:")
            if subject and subject.strip() and subject.strip() not in classes[cls]:
                classes[cls].append(subject.strip())
                self.save_data()
                refresh()

        def add_new_class():
            cls = simpledialog.askstring("Add Class", "Enter class number (1-12):")
            if cls and cls.isdigit() and 1 <= int(cls) <= 12 and cls not in classes:
                classes[cls] = []
                self.save_data()
                refresh()
            elif cls and cls in classes:
                messagebox.showwarning("Exists", "This class is already added")

        refresh()

    def enter_student_results(self):
        classes = self.data["users"][self.current_user]["classes"]
        if not classes:
            messagebox.showerror("No Classes", "Please add classes first in 'Manage Classes & Subjects'")
            return

        win = tk.Toplevel(self)
        win.title("Enter Student Results")
        win.geometry("1100x800")

        tk.Label(win, text="Enter Student Results - Step by Step", font=("Arial", 20, "bold")).pack(pady=40)

        tk.Label(win, text="Select Class:", font=("Arial", 16)).pack(pady=(30,10))
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(win, textvariable=class_var, values=list(classes.keys()), state="readonly", width=20, font=("Arial", 14))
        class_combo.pack(pady=10)

        def proceed_to_term():
            selected_class = class_var.get()
            if not selected_class:
                return
            for widget in win.winfo_children()[4:]:
                widget.destroy()

            terms = ["1st term", "2nd term", "finalterm"] if int(selected_class) <= 8 else ["1st term", "Sendups", "Preboard", "finalterm"]
            tk.Label(win, text="Select Term:", font=("Arial", 16)).pack(pady=(40,10))
            term_var = tk.StringVar()
            term_combo = ttk.Combobox(win, textvariable=term_var, values=terms, state="readonly", width=30, font=("Arial", 14))
            term_combo.pack(pady=10)

            tk.Label(win, text="Enter Student ID:", font=("Arial", 16)).pack(pady=(40,10))
            student_id_entry = tk.Entry(win, width=50, font=("Arial", 14))
            student_id_entry.pack(pady=10)

            def open_result_entry():
                student_id = student_id_entry.get().strip()
                term = term_var.get()
                if not all([selected_class, term, student_id]):
                    messagebox.showerror("Error", "All fields are required")
                    return
                if student_id not in self.data["users"] or self.data["users"][student_id]["role"] != "student":
                    messagebox.showerror("Error", "Student ID not found")
                    return

                result_win = tk.Toplevel(win)
                result_win.title(f"Result Entry - {student_id}")
                result_win.geometry("900x800")

                tk.Label(result_win, text=f"Class {selected_class} - {term}", font=("Arial", 20, "bold")).pack(pady=30)
                tk.Label(result_win, text=f"Student: {self.data['users'][student_id]['name']}", font=("Arial", 16)).pack(pady=10)

                entries = {}
                for subject in classes[selected_class]:
                    row = tk.Frame(result_win)
                    row.pack(pady=15, padx=60, fill="x")
                    tk.Label(row, text=f"{subject}", width=25, anchor="w", font=("Arial", 14)).pack(side="left")
                    tk.Label(row, text="Total Marks:").pack(side="left")
                    total_entry = tk.Entry(row, width=10, font=("Arial", 14))
                    total_entry.insert(0, "100")
                    total_entry.pack(side="left", padx=10)
                    tk.Label(row, text="Obtained:").pack(side="left")
                    obt_entry = tk.Entry(row, width=10, font=("Arial", 14))
                    obt_entry.pack(side="left", padx=10)
                    entries[subject] = (total_entry, obt_entry)

                tk.Label(result_win, text="Remarks:", font=("Arial", 16)).pack(pady=(30,10), anchor="w", padx=80)
                remarks_box = tk.Text(result_win, width=70, height=6, font=("Arial", 12))
                remarks_box.pack(pady=10, padx=80)

                def save_result():
                    result_data = {"class": selected_class, "subjects": {}, "overall": {}}
                    total_max = total_obtained = 0

                    for subject, (t_entry, o_entry) in entries.items():
                        try:
                            total = int(t_entry.get())
                            obtained = int(o_entry.get())
                            if obtained > total:
                                messagebox.showerror("Error", f"Obtained marks cannot exceed total in {subject}")
                                return
                            result_data["subjects"][subject] = {"total": total, "obtained": obtained}
                            total_max += total
                            total_obtained += obtained
                        except ValueError:
                            messagebox.showerror("Error", "Please enter valid numbers for marks")
                            return

                    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0
                    result_data["overall"] = {
                        "total": total_max,
                        "obtained": total_obtained,
                        "percentage": percentage,
                        "remarks": remarks_box.get("1.0", tk.END).strip()
                    }

                    self.data["results"].setdefault(student_id, {})[term] = result_data
                    self.save_data()
                    messagebox.showinfo("Success", "Result has been saved successfully!")
                    result_win.destroy()

                tk.Button(result_win, text="SAVE RESULT", font=("Arial", 18, "bold"), bg="#27ae60", fg="white", width=40, height=2,
                         command=save_result).pack(pady=50)

            tk.Button(win, text="Proceed to Enter Marks", font=("Arial", 16, "bold"), bg="#27ae60", fg="white", width=40, height=2,
                     command=open_result_entry).pack(pady=60)

        tk.Button(win, text="Next Step", font=("Arial", 16, "bold"), bg="#3498db", fg="white", width=30, command=proceed_to_term).pack(pady=30)

    def student_dashboard(self):
        self.clear_screen()
        
        # Create scrollable canvas
        canvas = tk.Canvas(self, bg="#f4f6f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f6f9")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        name = self.data["users"][self.current_user]["name"]
        tk.Label(scrollable_frame, text=f"WELCOME STUDENT\n{name.upper()}", font=("Helvetica", 26, "bold"), bg="#f4f6f9").pack(pady=80)

        results = self.data["results"].get(self.current_user, {})
        if not results:
            tk.Label(scrollable_frame, text="No results have been entered yet.\nPlease check back later.", font=("Arial", 18), fg="gray").pack(pady=150)
        else:
            tk.Label(scrollable_frame, text="Select Term to View Result", font=("Arial", 18)).pack(pady=40)
            term_var = tk.StringVar()
            term_combo = ttk.Combobox(scrollable_frame, textvariable=term_var, values=list(results.keys()), state="readonly", width=35, font=("Arial", 14))
            term_combo.pack(pady=20)

            def display_result():
                term = term_var.get()
                if not term:
                    return
                data = results[term]
                view_win = tk.Toplevel(self)
                view_win.title(f"Result - {term}")
                view_win.geometry("900x700")

                tree = ttk.Treeview(view_win, columns=("Subject", "Total", "Obtained", "Percentage"), show="headings")
                tree.heading("Subject", text="Subject")
                tree.heading("Total", text="Total Marks")
                tree.heading("Obtained", text="Obtained")
                tree.heading("Percentage", text="Percentage")
                tree.column("Subject", width=300)
                tree.column("Total", width=150)
                tree.column("Obtained", width=150)
                tree.column("Percentage", width=150)
                tree.pack(fill="both", expand=True, padx=50, pady=50)

                for subject, marks in data["subjects"].items():
                    perc = round(marks["obtained"] / marks["total"] * 100, 2) if marks["total"] > 0 else 0
                    tree.insert("", "end", values=(subject, marks["total"], marks["obtained"], f"{perc}%"))

                overall = data["overall"]
                tree.insert("", "end", values=("TOTAL", overall["total"], overall["obtained"], f"{overall['percentage']}%"))

                if overall["remarks"]:
                    tk.Label(view_win, text=f"Remarks: {overall['remarks']}", font=("Arial", 14, "italic"), fg="#2c3e50").pack(pady=20)

            tk.Button(scrollable_frame, text="VIEW RESULT", font=("Arial", 18, "bold"), bg="#27ae60", fg="white", width=35, height=2,
                     command=display_result).pack(pady=50)

        tk.Button(scrollable_frame, text="Change Password", font=("Arial", 16), bg="#3498db", fg="white", width=30, command=self.change_own_password).pack(pady=20)
        tk.Button(scrollable_frame, text="Logout", font=("Arial", 16), bg="#e74c3c", fg="white", width=30, command=self.show_login_screen).pack(pady=30)

        tk.Label(scrollable_frame, text="This Program is designed by Aniq Abbasi", 
                 font=("Arial", 11), fg="gray", bg="#f4f6f9").pack(side="bottom", pady=40)

    def change_own_password(self):
        new_pass = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if new_pass and len(new_pass) >= 6:
            self.data["users"][self.current_user]["password"] = hashlib.sha256(new_pass.encode()).hexdigest()
            self.save_data()
            messagebox.showinfo("Success", "Password changed successfully")
        elif new_pass:
            messagebox.showerror("Error", "Password must be at least 6 characters")

    def delete_own_account(self):
        if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?\nThis cannot be undone."):
            self.data["users"].pop(self.current_user, None)
            self.data["results"].pop(self.current_user, None)
            self.save_data()
            messagebox.showinfo("Account Deleted", "Your account has been deleted")
            self.show_login_screen()

if __name__ == "__main__":
    app = SchoolSystem()
    app.mainloop()