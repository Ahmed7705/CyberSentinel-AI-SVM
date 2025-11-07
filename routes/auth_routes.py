"""Authentication related Flask routes."""
from __future__ import annotations

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from services import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/", methods=["GET"])
def root() -> str:
    if session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))
    return redirect(url_for("auth.index"))


@auth_bp.route("/index", methods=["GET"])
def index() -> str:
    if session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    selected_role = ""
    entered_username = ""
    if request.method == "POST":
        selected_role = request.form.get("user_type", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        entered_username = username

        if not selected_role:
            error = "Please select a user type."
            return render_template("login.html", error=error, selected_role=selected_role, username=entered_username)

        user = auth_service.authenticate_user(username, password)
        if user and user["role"] == selected_role:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["full_name"] = user.get("full_name")
            current_app.logger.info("User %s logged in", username)
            redirect_target = "admin.dashboard" if user["role"] == "admin" else "user.dashboard"
            return redirect(url_for(redirect_target))
        if user and user["role"] != selected_role:
            error = "Selected role does not match account role."
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error, selected_role=selected_role, username=entered_username)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name", username)
    role = data.get("role", "user")
    department = data.get("department", "Unknown")

    if not username or not password:
        return {"error": "username and password are required"}, 400

    existing = auth_service.get_user_by_username(username)
    if existing:
        return {"error": "Username already exists"}, 409

    auth_service.register_user(username, password, full_name, role, department)
    current_app.logger.info("Created user %s (role=%s)", username, role)
    return {"status": "created"}, 201


@auth_bp.route("/logout", methods=["GET"])
def logout():
    if session.get("user_id"):
        current_app.logger.info("User %s logged out", session.get("username"))
    session.clear()
    return redirect(url_for("auth.login"))
