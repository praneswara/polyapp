from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import datetime as dt

admin_app = Flask(__name__, template_folder="templates")
admin_app.config["SECRET_KEY"] = "dev"

# ---------------- Demo Data ----------------
DEMO_STATS = {
    "total_users": 10,
    "total_machines": 3,
    "total_transactions": 25
}

DEMO_USERS = [
    {"id": 1, "name": "Alice", "mobile": 1111111111, "points": 100, "bottles": 5,
     "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "name": "Bob", "mobile": 2222222222, "points": 50, "bottles": 2,
     "created_at": dt.datetime.utcnow().isoformat()},
]

DEMO_TRANSACTIONS = [
    {"id": 1, "user_id": 1, "type": "earn", "points": 20, "bottles": 1,
     "machine_id": "M001", "brand_id": None, "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "user_id": 1, "type": "redeem", "points": 50, "bottles": 0,
     "machine_id": None, "brand_id": 1, "created_at": dt.datetime.utcnow().isoformat()},
]

DEMO_MACHINES = [
    {"id": 1, "machine_id": "M001", "name": "RVM Station A", "city": "jim,korea",
     "lat": 10.823879417459477, "lng": 78.70024710440879, "current_bottles": 10,
     "max_capacity": 100, "total_bottles": 50, "is_full": False,
     "last_emptied": None, "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "machine_id": "M002", "name": "RVM Station B", "city": "jim,korea",
     "lat": 12.9352, "lng": 77.6245, "current_bottles": 20,
     "max_capacity": 100, "total_bottles": 60, "is_full": False,
     "last_emptied": None, "created_at": dt.datetime.utcnow().isoformat()},
]

# ---------------- Auth Decorator ----------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Login ----------------
@admin_app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "polygreen" and password == "poly123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "error")
    return "<h3>Admin Login Page (Demo)</h3>"

# ---------------- Dashboard ----------------
@admin_app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return jsonify(DEMO_STATS)

# ---------------- Users ----------------
@admin_app.route("/admin/users")
@admin_required
def admin_users():
    return jsonify(DEMO_USERS)

@admin_app.route("/admin/users/<int:user_id>")
@admin_required
def admin_user_detail(user_id):
    user = next((u for u in DEMO_USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"message": "User not found"}), 404
    transactions = [t for t in DEMO_TRANSACTIONS if t["user_id"] == user_id]
    return jsonify({"user": user, "transactions": transactions})

# ---------------- Machines ----------------
@admin_app.route("/admin/machines")
@admin_required
def admin_machines():
    return jsonify(DEMO_MACHINES)

@admin_app.route("/admin/machines/<string:machine_id>")
@admin_required
def admin_machine_detail(machine_id):
    machine = next((m for m in DEMO_MACHINES if m["machine_id"] == machine_id), None)
    if not machine:
        return jsonify({"message": "Machine not found"}), 404
    transactions = [t for t in DEMO_TRANSACTIONS if t.get("machine_id") == machine_id]
    fill_percentage = (machine["current_bottles"] / machine["max_capacity"]) * 100
    return jsonify({"machine": machine, "transactions": transactions, "fill_percentage": fill_percentage})

# ---------------- Empty Machine ----------------
@admin_app.route("/admin/machine/<string:machine_id>/empty", methods=["POST"])
@admin_required
def admin_empty_machine(machine_id):
    return jsonify({"message": f"Machine {machine_id} emptied successfully", "collected_bottles": 10})

# ---------------- ADD Machine ----------------
@admin_app.route("/admin/machines/add", methods=["POST"])
@admin_required
def admin_add_machine():
    data = request.get_json() or {}
    return jsonify({"message": f"Machine {data.get('name', 'Demo')} added successfully"})

# ---------------- Logout ----------------
@admin_app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return jsonify({"message": "Logged out (Demo)"})

# ---------------- Root ----------------
@admin_app.route("/")
def home():
    return jsonify({"message": "Demo Admin API running (no DB)"})

if __name__ == "__main__":
    admin_app.run(host="0.0.0.0", port=5001, debug=True)
