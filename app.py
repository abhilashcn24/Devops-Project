from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory store (replace with DB in production)
notes = []

def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)

@app.route("/")
def index():
    return render_template("index.html", notes=sorted(notes, key=lambda x: x["created_at"], reverse=True))

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if title and content:
        notes.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "created_at": datetime.now().strftime("%b %d, %Y · %H:%M")
        })
    return redirect(url_for("index"))

@app.route("/edit/<note_id>", methods=["GET", "POST"])
def edit(note_id):
    note = find_note(note_id)
    if not note:
        return redirect(url_for("index"))
    if request.method == "POST":
        note["title"] = request.form.get("title", note["title"]).strip()
        note["content"] = request.form.get("content", note["content"]).strip()
        note["updated_at"] = datetime.now().strftime("%b %d, %Y · %H:%M")
        return redirect(url_for("index"))
    return render_template("edit.html", note=note)

@app.route("/delete/<note_id>", methods=["POST"])
def delete(note_id):
    global notes
    notes = [n for n in notes if n["id"] != note_id]
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return jsonify({"status": "ok", "notes_count": len(notes)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
