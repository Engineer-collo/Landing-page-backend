import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from models import db, Registration

app = Flask(__name__)

app.config.from_object(Config)

CORS(app)

db.init_app(app)
migrate = Migrate(app, db)


# 🔥 DEBUG: confirm DB is loaded
print("DATABASE_URL:", os.getenv("DATABASE_URL"))


@app.route("/")
def home():
    return {"message": "Backend running successfully"}


# REGISTER ROUTE
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    print("👉 Incoming request:", name, email, phone)

    # VALIDATION
    if not name or not email or not phone:
        return jsonify({"error": "All fields are required"}), 400

    # CHECK IF EMAIL EXISTS
    existing_user = Registration.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    try:
        # CREATE USER
        new_registration = Registration(
            name=name,
            email=email,
            phone=phone
        )

        db.session.add(new_registration)
        db.session.commit()

        # 🔥 CONFIRM SAVE
        print("✅ Saved to DB:", new_registration.id)

        return jsonify({
            "message": "Registration successful",
            "data": new_registration.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()

        print("❌ DB ERROR:", str(e))

        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500


# GET ALL REGISTRATIONS
@app.route("/registrations", methods=["GET"])
def get_registrations():

    registrations = Registration.query.all()

    print("📦 Total records:", len(registrations))

    return jsonify([
        registration.to_dict()
        for registration in registrations
    ]), 200

@app.route("/registrations/<int:id>", methods=["DELETE"])
def delete_registration(id):

    reg = Registration.query.get(id)

    if not reg:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(reg)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)