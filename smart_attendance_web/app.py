from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path="/static")
app.secret_key = "gvp_secret_key"


# ================= DB =================

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

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


# ================= AI LOGIC =================

def performance_remark(marks):
    if marks >= 75:
        return "Good"
    elif marks >= 50:
        return "Average"
    else:
        return "Needs Improvement"


# ================= AUTH =================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?,?,?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["email"]
            return redirect(url_for("index"))

        return "Invalid Login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= HOME =================

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


# ================= STUDENT =================

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO student VALUES (?,?,?,?,?)",
            (
                request.form["roll"],
                request.form["name"],
                request.form["semester"],
                0,
                0
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add_student.html")


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        percent = (int(request.form["attended"]) / int(request.form["total"])) * 100

        conn = get_db_connection()
        conn.execute(
            "UPDATE student SET attendance=? WHERE roll_no=?",
            (percent, request.form["roll"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("attendance.html")


@app.route("/marks", methods=["GET", "POST"])
def marks():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        conn = get_db_connection()
        conn.execute(
            "UPDATE student SET marks=? WHERE roll_no=?",
            (request.form["marks"], request.form["roll"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("marks.html")


# ================= SINGLE REPORT =================

@app.route("/report", methods=["GET", "POST"])
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    student = None
    remark = ""
    warning = ""

    if request.method == "POST":
        conn = get_db_connection()
        student = conn.execute(
            "SELECT * FROM student WHERE roll_no=?",
            (request.form["roll"],)
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


# ================= ALL STUDENTS REPORT =================

@app.route("/all_students")
def all_students():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM student").fetchall()
    conn.close()

    return render_template("all_students.html", students=students)


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
