from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

from database.supabase_client import supabase


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")

        # Check whether email already exists
        existing = (
            supabase
            .table("users")
            .select("user_id")
            .eq("email", email)
            .execute()
        )

        if existing.data:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        try:

            response = (
                supabase
                .table("users")
                .insert({
                    "name": name,
                    "email": email,
                    "password_hash": password_hash,
                    "role": "STUDENT"
                })
                .execute()
            )

            if not response.data:
                flash("Registration failed.", "error")
                return render_template("register.html")

            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as error:

            print("Registration error:", error)

            flash("Could not create the account.", "error")
            return render_template("register.html")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        try:

            response = (
                supabase
                .table("users")
                .select("*")
                .eq("email", email)
                .limit(1)
                .execute()
            )

            if not response.data:
                flash("Invalid email or password.", "error")
                return render_template("login.html")

            user = response.data[0]

            if not check_password_hash(
                user["password_hash"],
                password
            ):
                flash("Invalid email or password.", "error")
                return render_template("login.html")

            session.clear()

            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == "STUDENT":
                return redirect(url_for("auth.student_dashboard"))

            elif user["role"] == "SUPERVISOR":
                return redirect(url_for("auth.supervisor_dashboard"))

            elif user["role"] == "ADMIN":
                return redirect(url_for("auth.admin_dashboard"))

            flash("Unknown user role.", "error")
            session.clear()

        except Exception as error:

            print("Login error:", error)

            flash("Login failed.", "error")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))


@auth.route("/student/dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "STUDENT":
        return "Access denied", 403

    return render_template(
        "student_dashboard.html",
        name=session.get("name")
    )


@auth.route("/supervisor/dashboard")
def supervisor_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "SUPERVISOR":
        return "Access denied", 403

    return render_template(
        "supervisor_dashboard.html",
        name=session.get("name")
    )


@auth.route("/admin/dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "ADMIN":
        return "Access denied", 403

    return render_template(
        "admin_dashboard.html",
        name=session.get("name")
    )