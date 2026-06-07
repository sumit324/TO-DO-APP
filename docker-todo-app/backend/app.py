from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DB_URL = os.getenv("DATABASE_URL", "postgresql://todo_user:todo_pass@db:5432/todo_db")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = "todos"
    id      = db.Column(db.Integer, primary_key=True)
    task    = db.Column(db.String(200), nullable=False)
    done    = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "task": self.task, "done": self.done}

with app.app_context():
    db.create_all()

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    if not data or not data.get("task"):
        return jsonify({"error": "task is required"}), 400
    todo = Todo(task=data["task"])
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    if "done" in data:
        todo.done = data["done"]
    if "task" in data:
        todo.task = data["task"]
    db.session.commit()
    return jsonify(todo.to_dict())

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"deleted": todo_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
