from flask import Flask, request, jsonify
import datetime as dt

admin_app = Flask(__name__)

# ---------------- Demo data ----------------
DEMO_USERS = [
    {"id": 1, "name": "Alice", "mobile": 1234567890, "points": 100, "bottles": 10, "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "name": "Bob", "mobile": 9876543210, "points": 50, "bottles": 5, "created_at": dt.datetime.utcnow().isoformat()},
]

DEMO_MACHINES = [
    {"id": 1, "machine_id": "M001", "name": "RVM Station A", "city": "jim,korea",
     "lat": 10.823879417459477, "lng": 78.70024710440879,
     "current_bottles": 10, "max_capacity": 100, "total_bottles": 50,
     "is_full": False, "last_emptied": None, "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "machine_id": "M002", "name": "RVM Station B", "city": "jim,korea",
     "lat": 12.9352, "lng": 77.6245,
     "current_bottles": 20, "max_capacity": 100, "total_bottles": 70,
     "is_full": False, "last_emptied": None, "created_at": dt.datetime.utcnow().isoformat()},
]

DEMO_TRANSACTIONS = [
    {"id": 1, "user_id": 1, "type": "earn", "points": 20, "bottles": 2, "machine_id": "M001", "brand_id": None, "created_at": dt.datetime.utcnow().isoformat()},
    {"id": 2, "user_id": 1, "type": "redeem", "points": 50, "bottles": 0, "machine_id": None, "brand_id": 1, "created_at": dt.datetime.utcnow().isoformat()},
]

# ---------------- Routes -----------------
@admin_app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    return jsonify({
        "total_users": len(DEMO_USERS),
        "total_machines": len(DEMO_MACHINES),
        "total_transactions": len(DEMO_TRANSACTIONS)
    })


@admin_app.route("/admin/users", methods=["GET"])
def admin_users():
    return jsonify(items=DEMO_USERS)


@admin_app.route("/admin/users/<int:user_id>", methods=["GET"])
def admin_user_detail(user_id):
    user = next((u for u in DEMO_USERS if u["id"] == user_id), None)
    if not user:
        return jsonify(message="User not found"), 404
    user_transactions = [t for t in DEMO_TRANSACTIONS if t["user_id"] == user_id]
    return jsonify(user=user, transactions=user_transactions)


@admin_app.route("/admin/machines", methods=["GET"])
def admin_machines():
    return jsonify(items=DEMO_MACHINES)


@admin_app.route("/admin/machines/<string:machine_id>", methods=["GET"])
def admin_machine_detail(machine_id):
    machine = next((m for m in DEMO_MACHINES if m["machine_id"] == machine_id), None)
    if not machine:
        return jsonify(message="Machine not found"), 404
    machine_transactions = [t for t in DEMO_TRANSACTIONS if t["machine_id"] == machine_id]
    fill_percentage = (machine["current_bottles"] / machine["max_capacity"] * 100) if machine["max_capacity"] else 0
    return jsonify(machine=machine, transactions=machine_transactions, fill_percentage=fill_percentage)


@admin_app.route("/admin/machine/<string:machine_id>/empty", methods=["POST"])
def admin_empty_machine(machine_id):
    machine = next((m for m in DEMO_MACHINES if m["machine_id"] == machine_id), None)
    if not machine:
        return jsonify(message="Machine not found"), 404
    collected = machine["current_bottles"]
    machine["current_bottles"] = 0
    machine["is_full"] = False
    machine["last_emptied"] = dt.datetime.utcnow().isoformat()
    return jsonify(message=f"Machine '{machine['name']}' emptied successfully!", bottles_collected=collected)


@admin_app.route("/admin/machines/add", methods=["POST"])
def admin_add_machine():
    data = request.get_json() or {}
    new_machine = {
        "id": len(DEMO_MACHINES) + 1,
        "machine_id": data.get("machine_id", f"M00{len(DEMO_MACHINES)+1}"),
        "name": data.get("name", "Demo Machine"),
        "city": data.get("city", "Unknown"),
        "lat": data.get("lat", 0.0),
        "lng": data.get("lng", 0.0),
        "current_bottles": 0,
        "max_capacity": data.get("max_capacity", 100),
        "total_bottles": 0,
        "is_full": False,
        "last_emptied": None,
        "created_at": dt.datetime.utcnow().isoformat()
    }
    DEMO_MACHINES.append(new_machine)
    return jsonify(message=f"Machine '{new_machine['name']}' added successfully!", machine=new_machine)


# ---------------- Root -----------------
@admin_app.route("/", methods=["GET"])
def home():
    return jsonify(message="Demo Admin API running (no DB)")


if __name__ == "__main__":
    admin_app.run(port=5001, debug=True)
