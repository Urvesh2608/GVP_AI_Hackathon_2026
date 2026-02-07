from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__, static_url_path="/static")


# ---------- Database Connection ----------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Database Table Create ----------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student (
            roll_no TEXT PRIMARY KEY,
            name TEXT,
            semester TEXT,
            attendance REAL,
            marks INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- AI Logic ----------
def performance_remark(marks):
    if marks >= 75:
        return "Good"
    elif marks >= 50:
        return "Average"
    else:
        return "Needs Improvement"

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        sem = request.form["semester"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO student VALUES (?, ?, ?, ?, ?)",
            (roll, name, sem, 0, 0)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("add_student.html")

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if request.method == "POST":
        roll = request.form["roll"]
        total = int(request.form["total"])
        attended = int(request.form["attended"])
        percent = (attended / total) * 100

        conn = get_db_connection()
        conn.execute(
            "UPDATE student SET attendance=? WHERE roll_no=?",
            (percent, roll)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("attendance.html")

@app.route("/marks", methods=["GET", "POST"])
def marks():
    if request.method == "POST":
        roll = request.form["roll"]
        marks = int(request.form["marks"])

        conn = get_db_connection()
        conn.execute(
            "UPDATE student SET marks=? WHERE roll_no=?",
            (marks, roll)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("marks.html")

@app.route("/report", methods=["GET", "POST"])
def report():
    student = None
    remark = ""
    warning = ""

    if request.method == "POST":
        roll = request.form["roll"]
        conn = get_db_connection()
        student = conn.execute(
            "SELECT * FROM student WHERE roll_no=?",
            (roll,)
        ).fetchone()
        conn.close()

        if student:
            remark = performance_remark(student["marks"])
            if student["attendance"] < 75:
                warning = "⚠ Attendance Shortage"

    return render_template(
        "report.html",
        student=student,
        remark=remark,
        warning=warning
    )

if __name__ == "__main__":
    app.run(debug=True)
