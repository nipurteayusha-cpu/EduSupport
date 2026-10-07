
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "edusupport_secret_key"

DATABASE = "database.db"
# Create database and tables
def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    """)

    # Support requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            course TEXT NOT NULL,
            college TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Register page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users
                (name, email, password, user_type)
                VALUES (?, ?, ?, ?)
            """, (name, email, password, user_type))

            conn.commit()
            conn.close()

            return """
            <h2>Registration Successful!</h2>
            <a href="/login">Go to Login</a>
            """

        except sqlite3.IntegrityError:

            return """
            <h2>Email already registered.</h2>
            <a href="/register">Try Again</a>
            """

    return render_template("register.html")

# Login page

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE email = ? AND password = ?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            if user[4] == "student":
                return redirect("/student")

            elif user[4] == "supporter":
                return redirect("/supporter")

        return """
        <h2>Invalid email or password.</h2>
        <a href="/login">Try Again</a>
        """

    return render_template("login.html")



# Student support application
@app.route("/apply", methods=["GET", "POST"])
def apply():

    if request.method == "POST":

        student_name = request.form["student_name"]
        course = request.form["course"]
        college = request.form["college"]
        amount = request.form["amount"]
        reason = request.form["reason"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO support_requests
            (student_name, course, college, amount, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_name,
            course,
            college,
            amount,
            reason
        ))

        conn.commit()
        conn.close()

        return """
        <h2>Application Submitted Successfully!</h2>
        <p>Your education support request has been saved.</p>

        <br>

        <a href="/student">Back to Student Dashboard</a>
        <br><br>

        <a href="/student-requests">View My Applications</a>
        """

    return render_template("apply.html")


# Supporter dashboard
# Supporter dashboard
@app.route("/supporter")
def supporter():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, student_name, course, college,
               amount, reason, status
        FROM support_requests
        WHERE status = 'Pending'
        ORDER BY id DESC
    """)

    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "supporter.html",
        requests=requests
    )
# Support a student
@app.route("/support/<int:request_id>", methods=["POST"])
def support(request_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE support_requests
        SET status = 'Supported'
        WHERE id = ?
    """, (request_id,))

    conn.commit()
    conn.close()

    return render_template(
        "support_success.html"
    )
 # Student dashboard
@app.route("/student")
def student():

    return render_template("student.html")
 # View student applications
@app.route("/student-requests")
def student_requests():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_name, course, college,
               amount, reason, status
        FROM support_requests
        ORDER BY id DESC
    """)

    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "student_requests.html",
        requests=requests
    )
# Admin Login
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect("/admin")

        return """
        <h2>Invalid Admin Login</h2>
        <a href="/admin-login">Try Again</a>
        """

    return render_template("admin_login.html")
# Admin approve application
@app.route("/admin/approve/<int:request_id>", methods=["POST"])
def admin_approve(request_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE support_requests
        SET status = 'Approved'
        WHERE id = ?
    """, (request_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# Admin reject application
@app.route("/admin/reject/<int:request_id>", methods=["POST"])
def admin_reject(request_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE support_requests
        SET status = 'Rejected'
        WHERE id = ?
    """, (request_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# Admin Dashboard
# Admin Dashboard
@app.route("/admin")
def admin():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get all users
    cursor.execute("""
        SELECT id, name, email, user_type
        FROM users
        ORDER BY id DESC
    """)
    users = cursor.fetchall()

    # Get all support requests
    cursor.execute("""
        SELECT id, student_name, course, college,
               amount, reason, status
        FROM support_requests
        ORDER BY id DESC
    """)
    requests = cursor.fetchall()

    # Dashboard counts
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM support_requests")
    total_requests = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM support_requests
        WHERE status = 'Pending'
    """)
    pending_requests = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM support_requests
        WHERE status = 'Supported'
    """)
    supported_requests = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        requests=requests,
        total_users=total_users,
        total_requests=total_requests,
        pending_requests=pending_requests,
        supported_requests=supported_requests
    )
    


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

  