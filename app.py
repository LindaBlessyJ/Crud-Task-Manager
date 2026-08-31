from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("tasks.db")
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
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    description = request.form["description"]

    conn = sqlite3.connect("tasks.db")
    conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    title = request.form["title"]
    description = request.form["description"]
    status = request.form["status"]

    conn = sqlite3.connect("tasks.db")
    conn.execute(
        "UPDATE tasks SET title=?, description=?, status=? WHERE id=?",
        (title, description, status, id)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect("tasks.db")
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
