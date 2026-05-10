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

    # VALIDATION
    if not name or not email or not phone:
        return jsonify({
            "error": "All fields are required"
        }), 400

    # CHECK IF EMAIL EXISTS
    existing_user = Registration.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 400

    # CREATE USER
    new_registration = Registration(
        name=name,
        email=email,
        phone=phone
    )

    db.session.add(new_registration)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "data": new_registration.to_dict()
    }), 201


# GET ALL REGISTRATIONS
@app.route("/registrations", methods=["GET"])
def get_registrations():

    registrations = Registration.query.all()

    return jsonify([
        registration.to_dict()
        for registration in registrations
    ]), 200


if __name__ == "__main__":app.run(host="0.0.0.0", port=5000)