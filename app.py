import re

from flask import Flask, jsonify, render_template, request

import db
from config import PORT

app = Flask(__name__)
db.init_db()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/issues/001")
def issue_001():
    return render_template("issue_001.html")


@app.route("/waitlist", methods=["POST"])
def waitlist():
    email = (request.json or {}).get("email", "").strip()
    if not EMAIL_RE.match(email):
        return jsonify({"ok": False, "error": "Enter a valid email."}), 400
    db.add_to_waitlist(email)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
