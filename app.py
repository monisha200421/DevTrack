from flask import Flask, jsonify, request, render_template
from database import get_connection, init_db

app = Flask(__name__)
init_db()

PRIORITIES = {"Low", "Medium", "High"}
STATUSES = {"To Do", "In Progress", "Completed"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    search = request.args.get("search", "").strip()

    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if status:
        sql += " AND status =?"
        params.append(status)
    if priority:
        sql += " AND priority =?"
        params.append(priority)
    if search:
        sql += " AND title LIKE?"
        params.append(f"%{search}%")

    sql += " ORDER BY id DESC"

    with get_connection() as conn:
        tasks = conn.execute(sql, params).fetchall()
    return jsonify([dict(t) for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.json
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400

    description = data.get("description", "")
    priority = data.get("priority", "Medium")
    status = data.get("status", "To Do")
    deadline = data.get("deadline", "")

    if priority not in PRIORITIES or status not in STATUSES:
        return jsonify({"error": "Invalid priority or status"}), 400

    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, priority, status, deadline) VALUES (?,?,?,?,?)",
            (title, description, priority, status, deadline)
        )
        task_id = cur.lastrowid

    with get_connection() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return jsonify(dict(task)), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400

    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not exists:
            return jsonify({"error": "Task not found"}), 404
        conn.execute(
            "UPDATE tasks SET title=?, description=?, priority=?, status=?, deadline=? WHERE id=?",
            (title, data.get("description",""), data.get("priority","Medium"), data.get("status","To Do"), data.get("deadline",""), task_id)
        )
        task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return jsonify(dict(task))

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Deleted"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        todo = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='To Do'").fetchone()[0]
        inprog = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='In Progress'").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'").fetchone()[0]
    return jsonify({"total": total, "pending": todo, "in_progress": inprog, "completed": completed})

if __name__ == "__main__":
    app.run(debug=True)