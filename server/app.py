# server/app.py
from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Message

app = Flask(__name__)

# SQLite file db in server directory
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.get("/messages")
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

@app.post("/messages")
def create_message():
    data = request.get_json() or {}
    body = data.get("body")
    username = data.get("username")

    if not body or not username:
        return jsonify({"error": "body and username are required"}), 400

    msg = Message(body=body, username=username)
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_dict()), 201

@app.patch("/messages/<int:id>")
def update_message(id):
    msg = Message.query.get(id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json() or {}
    if "body" in data:
        if not data["body"]:
            return jsonify({"error": "body cannot be empty"}), 400
        msg.body = data["body"]

    db.session.commit()
    return jsonify(msg.to_dict()), 200

@app.delete("/messages/<int:id>")
def delete_message(id):
    msg = Message.query.get(id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(msg)
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    app.run(port=5000, debug=True)