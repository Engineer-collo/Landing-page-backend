import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate, upgrade

from config import Config
from models import db, Registration, MeetingLink

# =========================
# APP INIT
# =========================
app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

print("DATABASE_URL:", os.getenv("DATABASE_URL"))


# =========================
# AUTO MIGRATION (RENDER SAFE)
# =========================
with app.app_context():
    try:
        upgrade()
        print("✅ Database migrated successfully")
    except Exception as e:
        print("⚠️ Migration error:", e)


# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return {"message": "Backend running successfully"}


# =========================
# REGISTER USER
# =========================
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    if not name or not email or not phone:
        return jsonify({"error": "All fields are required"}), 400

    existing_user = Registration.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    try:
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

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================
# GET ALL REGISTRATIONS
# =========================
@app.route("/registrations", methods=["GET"])
def get_registrations():

    registrations = Registration.query.all()

    return jsonify([
        r.to_dict() for r in registrations
    ]), 200


# =========================
# DELETE REGISTRATION
# =========================
@app.route("/registrations/<int:id>", methods=["DELETE"])
def delete_registration(id):

    reg = Registration.query.get(id)

    if not reg:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(reg)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"}), 200


# =====================================================
# 🎥 MEETING LINK ROUTES
# =====================================================

# CREATE MEETING LINK
@app.route("/meeting-links", methods=["POST"])
def create_meeting_link():

    data = request.get_json()

    url = data.get("url")
    title = data.get("title", "Zoom Meeting")
    description = data.get("description")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # deactivate previous active links
        MeetingLink.query.filter_by(is_active=True).update({"is_active": False})

        new_link = MeetingLink(
            title=title,
            url=url,
            description=description,
            is_active=True
        )

        db.session.add(new_link)
        db.session.commit()

        return jsonify({
            "message": "Meeting link created",
            "data": new_link.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# GET ALL MEETING LINKS
@app.route("/meeting-links", methods=["GET"])
def get_meeting_links():

    links = MeetingLink.query.all()

    return jsonify([
        link.to_dict() for link in links
    ]), 200


# GET ACTIVE MEETING LINK (FOR FRONTEND)
@app.route("/meeting-links/active", methods=["GET"])
def get_active_meeting_link():

    link = MeetingLink.query.filter_by(is_active=True).first()

    if not link:
        return jsonify({"error": "No active meeting link found"}), 404

    return jsonify(link.to_dict()), 200


# UPDATE MEETING LINK
@app.route("/meeting-links/<int:id>", methods=["PUT"])
def update_meeting_link(id):

    link = MeetingLink.query.get(id)

    if not link:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()

    if "title" in data:
        link.title = data["title"]

    if "url" in data:
        link.url = data["url"]

    if "description" in data:
        link.description = data["description"]

    if "is_active" in data:
        link.is_active = data["is_active"]

    try:
        db.session.commit()

        return jsonify({
            "message": "Updated successfully",
            "data": link.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# DELETE MEETING LINK
@app.route("/meeting-links/<int:id>", methods=["DELETE"])
def delete_meeting_link(id):

    link = MeetingLink.query.get(id)

    if not link:
        return jsonify({"error": "Not found"}), 404

    try:
        db.session.delete(link)
        db.session.commit()

        return jsonify({"message": "Deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)