import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date


# ================= DATABASE =================

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Student table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    course TEXT NOT NULL
)
""")

# Attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()


# ================= FUNCTIONS =================

def add_student():

    name = name_entry.get()
    roll_no = roll_entry.get()
    course = course_entry.get()

    if name == "" or roll_no == "" or course == "":
        messagebox.showwarning(
            "Warning",
            "Please fill all fields."
        )
        return

    try:
        cursor.execute("""
        INSERT INTO students (name, roll_no, course)
        VALUES (?, ?, ?)
        """, (name, roll_no, course))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )

        name_entry.delete(0, tk.END)
        roll_entry.delete(0, tk.END)
        course_entry.delete(0, tk.END)

        show_students()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Error",
            "Roll number already exists."
        )


def show_students():

    for item in student_table.get_children():
        student_table.delete(item)

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    for student in students:

        student_table.insert(
            "",
            tk.END,
            values=student
        )


def mark_attendance():

    selected = student_table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select a student."
        )
        return

    item = student_table.item(selected[0])

    student_id = item["values"][0]

    status = status_box.get()

    today = date.today().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT * FROM attendance
    WHERE student_id = ?
    AND attendance_date = ?
    """, (student_id, today))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
        UPDATE attendance
        SET status = ?
        WHERE student_id = ?
        AND attendance_date = ?
        """, (status, student_id, today))

    else:

        cursor.execute("""
        INSERT INTO attendance
        (student_id, attendance_date, status)
        VALUES (?, ?, ?)
        """, (student_id, today, status))

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Attendance marked successfully!"
    )


def show_attendance():

    for item in attendance_table.get_children():
        attendance_table.delete(item)

    cursor.execute("""
    SELECT
        students.roll_no,
        students.name,
        students.course,
        attendance.attendance_date,
        attendance.status

    FROM attendance

    JOIN students
    ON students.id = attendance.student_id

    ORDER BY attendance.attendance_date DESC
    """)

    records = cursor.fetchall()

    for record in records:

        attendance_table.insert(
            "",
            tk.END,
            values=record
        )


# ================= WINDOW =================

root = tk.Tk()

root.title("Student Attendance Management System")

root.geometry("950x650")

root.resizable(False, False)


# ================= TITLE =================

title = tk.Label(
    root,
    text="Student Attendance Management System",
    font=("Arial", 20, "bold")
)

title.pack(pady=15)


# ================= STUDENT FORM =================

form = tk.LabelFrame(
    root,
    text="Student Details",
    font=("Arial", 12, "bold")
)

form.pack(
    fill="x",
    padx=20,
    pady=5
)


# Student Name

tk.Label(
    form,
    text="Student Name:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)

name_entry = tk.Entry(
    form,
    width=25
)

name_entry.grid(
    row=0,
    column=1
)


# Roll Number

tk.Label(
    form,
    text="Roll Number:"
).grid(
    row=0,
    column=2,
    padx=10
)

roll_entry = tk.Entry(
    form,
    width=20
)

roll_entry.grid(
    row=0,
    column=3
)


# Course

tk.Label(
    form,
    text="Course:"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10
)

course_entry = tk.Entry(
    form,
    width=25
)

course_entry.grid(
    row=1,
    column=1
)


# Add Student

add_button = tk.Button(
    form,
    text="Add Student",
    command=add_student,
    width=18
)

add_button.grid(
    row=1,
    column=3,
    pady=10
)


# ================= STUDENT TABLE =================

student_frame = tk.LabelFrame(
    root,
    text="Student Records",
    font=("Arial", 12, "bold")
)

student_frame.pack(
    fill="x",
    padx=20,
    pady=10
)


student_table = ttk.Treeview(
    student_frame,
    columns=("ID", "Name", "Roll", "Course"),
    show="headings",
    height=6
)


student_table.heading(
    "ID",
    text="ID"
)

student_table.heading(
    "Name",
    text="Name"
)

student_table.heading(
    "Roll",
    text="Roll Number"
)

student_table.heading(
    "Course",
    text="Course"
)


student_table.pack(
    fill="x",
    padx=10,
    pady=10
)


# ================= ATTENDANCE =================

attendance_frame = tk.LabelFrame(
    root,
    text="Attendance",
    font=("Arial", 12, "bold")
)

attendance_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    attendance_frame,
    text="Status:"
).pack(
    side="left",
    padx=10
)


status_box = ttk.Combobox(
    attendance_frame,
    values=["Present", "Absent"],
    state="readonly",
    width=15
)

status_box.set("Present")

status_box.pack(
    side="left",
    padx=10
)


mark_button = tk.Button(
    attendance_frame,
    text="Mark Attendance",
    command=mark_attendance,
    width=18
)

mark_button.pack(
    side="left",
    padx=10
)


view_button = tk.Button(
    attendance_frame,
    text="View Attendance",
    command=show_attendance,
    width=18
)

view_button.pack(
    side="left",
    padx=10
)


# ================= ATTENDANCE TABLE =================

attendance_frame2 = tk.LabelFrame(
    root,
    text="Attendance Records",
    font=("Arial", 12, "bold")
)

attendance_frame2.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


attendance_table = ttk.Treeview(
    attendance_frame2,
    columns=("Roll", "Name", "Course", "Date", "Status"),
    show="headings"
)


attendance_table.heading(
    "Roll",
    text="Roll Number"
)

attendance_table.heading(
    "Name",
    text="Name"
)

attendance_table.heading(
    "Course",
    text="Course"
)

attendance_table.heading(
    "Date",
    text="Date"
)

attendance_table.heading(
    "Status",
    text="Status"
)


attendance_table.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# Load students when program starts

show_students()


# ================= RUN =================

root.mainloop()