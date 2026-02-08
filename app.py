from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data.json"

# Set this in your hosting environment for basic protection of the editor page.
# Example (Windows PowerShell):  setx EDIT_TOKEN "my-secret-token"
# Example (macOS/Linux):        export EDIT_TOKEN="my-secret-token"
EDIT_TOKEN = os.environ.get("EDIT_TOKEN", "")

app = Flask(__name__)


def load_data() -> Dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(payload: Dict[str, Any]) -> None:
    # Enforce: exactly 1 director and exactly 15 members
    if "director" not in payload or not isinstance(payload["director"], dict):
        raise ValueError("director is required and must be an object")
    members = payload.get("members")
    if not isinstance(members, list) or len(members) != 15:
        raise ValueError("members must be a list of exactly 15 items")
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


@app.get("/")
def home():
    data = load_data()
    return render_template("index.html", data=data)


@app.get("/api/data")
def api_get_data():
    return jsonify(load_data())


@app.post("/api/data")
def api_set_data():
    # Token can be sent either as header or query param
    token = request.headers.get("X-Edit-Token") or request.args.get("token") or ""
    if EDIT_TOKEN and token != EDIT_TOKEN:
        abort(401)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "JSON body is required"}), 400

    try:
        save_data(payload)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    return jsonify({"ok": True})


@app.get("/edit")
def edit_page():
    # Very lightweight “editor page” (not an admin panel)
    # If EDIT_TOKEN is set, require ?token=... in the URL
    token = request.args.get("token", "")
    if EDIT_TOKEN and token != EDIT_TOKEN:
        return render_template("edit_locked.html"), 401

    data = load_data()
    return render_template("edit.html", data=data, token=token)


@app.post("/edit")
def edit_save():
    token = request.args.get("token", "")
    if EDIT_TOKEN and token != EDIT_TOKEN:
        abort(401)

    payload = load_data()

    payload["site"]["main_title"] = request.form.get("site_main_title", payload["site"]["main_title"]).strip()
    payload["site"]["tagline"] = request.form.get("site_tagline", payload["site"]["tagline"]).strip()
    payload["site"]["members_title"] = request.form.get("site_members_title", payload["site"]["members_title"]).strip()

    payload["director"]["name"] = request.form.get("director_name", payload["director"]["name"]).strip()
    payload["director"]["bio"] = request.form.get("director_bio", payload["director"]["bio"]).strip()
    payload["director"]["phone"] = request.form.get("director_phone", payload["director"]["phone"]).strip()
    payload["director"]["telegram"] = request.form.get("director_telegram", payload["director"]["telegram"]).strip().lstrip("@")
    payload["director"]["email"] = request.form.get("director_email", payload["director"]["email"]).strip()

    members = []
    for i in range(15):
        members.append({
            "name": (request.form.get(f"m{i}_name", "") or "").strip(),
            "specialty": (request.form.get(f"m{i}_specialty", "") or "").strip(),
            "bio": (request.form.get(f"m{i}_bio", "") or "").strip(),
            "phone": (request.form.get(f"m{i}_phone", "") or "").strip(),
            "telegram": (request.form.get(f"m{i}_telegram", "") or "").strip().lstrip("@"),
            "email": (request.form.get(f"m{i}_email", "") or "").strip(),
        })

    payload["members"] = members

    try:
        save_data(payload)
    except Exception as e:
        return render_template("edit.html", data=payload, token=token, error=str(e)), 400

    return redirect(url_for("edit_page", token=token))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
