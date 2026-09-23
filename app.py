from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Change this to a random secret before production
app.secret_key = "change-this-to-a-random-secret-key"


def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for('home'))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for('login'))

    title = request.form.get("title")
    description = request.form.get("description")

    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "user_id" not in session:
        return redirect(url_for('login'))

    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")

    conn = get_db()
    conn.execute(
        "UPDATE tasks SET title=?, description=?, status=? WHERE id=?",
        (title, description, status, id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if "user_id" not in session:
        flash("You must login first", "warning")
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
