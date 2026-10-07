import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)

from config import Config
from database.init_db import init_db, get_db_connection
from models.user import UserModel
from models.waste import WasteModel
from models.buyer import BuyerModel
from models.recommendation import RecommendationModel
from services.ai_service import AIService
from services.recommendation_service import RecommendationService
from services.buyer_service import BuyerService
from utils.helpers import (
    login_required, admin_required, allowed_file,
    calculate_environmental_impact, get_district_coordinates
)

# Initialize Flask Application
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Ensure database exists and is initialized
if not Path(Config.DATABASE_PATH).exists():
    init_db()

# Context processor to inject common variables into all templates
@app.context_processor
def inject_global_data():
    current_user = None
    if "user_id" in session:
        current_user = UserModel.find_by_id(session["user_id"])
    return {
        "current_user": current_user,
        "is_admin": session.get("admin_logged_in", False),
        "buyer_categories": BuyerModel.CATEGORIES
    }

# -------------------------------------------------------------
# Public & Authentication Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    """Home landing page explaining the problem, solution, and workflow."""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Farmer registration route."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        village = request.form.get("village", "").strip()
        district = request.form.get("district", "").strip()
        state = request.form.get("state", "").strip()

        # Validation
        if not all([name, mobile, email, password, village, district, state]):
            flash("All registration fields are required.", "danger")
            return render_template("register.html", form=request.form)

        if len(mobile) < 10:
            flash("Please enter a valid 10-digit mobile number.", "danger")
            return render_template("register.html", form=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", form=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", form=request.form)

        result = UserModel.create_user(name, mobile, email, password, village, district, state)
        if result["success"]:
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash(result["error"], "danger")
            return render_template("register.html", form=request.form)

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Farmer and user login route."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Please enter your mobile/email and password.", "danger")
            return render_template("login.html")

        user = UserModel.authenticate(identifier, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_district"] = user["district"]
            session["user_state"] = user["state"]
            flash(f"Welcome back, {user['name']}! 🌾", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid mobile/email or password. Please try again.", "danger")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logs out farmer and clears session."""
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("login"))

# -------------------------------------------------------------
# Farmer Dashboard & Core Features
# -------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    """Farmer dashboard displaying stats and recent waste entries."""
    user_id = session["user_id"]
    stats = WasteModel.get_user_dashboard_stats(user_id)
    recent_records = WasteModel.get_user_records(user_id)[:5]
    return render_template("dashboard.html", stats=stats, recent_records=recent_records)

@app.route("/add-waste", methods=["GET", "POST"])
@login_required
def add_waste():
    """Add crop waste form and trigger AI analysis."""
    user = UserModel.find_by_id(session["user_id"])

    if request.method == "POST":
        crop_name = request.form.get("crop_name", "").strip()
        waste_type = request.form.get("waste_type", "").strip()
        quantity_str = request.form.get("quantity", "").strip()
        unit = request.form.get("unit", "kg").strip()
        village = request.form.get("village", user.get("village", "")).strip()
        district = request.form.get("district", user.get("district", "")).strip()
        state = request.form.get("state", user.get("state", "")).strip()
        harvest_date = request.form.get("harvest_date", "").strip()
        storage_condition = request.form.get("storage_condition", "").strip()

        # Validation
        if not crop_name or not quantity_str:
            flash("Please provide crop name and quantity.", "danger")
            return render_template("add_waste.html", user=user)

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            flash("Please enter a valid positive quantity number.", "danger")
            return render_template("add_waste.html", user=user)

        if not waste_type:
            waste_type = f"{crop_name} Residue"

        # Image upload handling
        image_filename = None
        if "waste_image" in request.files:
            file = request.files["waste_image"]
            if file and file.filename != "" and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                unique_name = f"waste_{session['user_id']}_{os.urandom(4).hex()}_{fname}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
                image_filename = unique_name

        # 1. Save waste record to SQLite
        record_id = WasteModel.create_record(
            user_id=session["user_id"],
            crop_name=crop_name,
            waste_type=waste_type,
            quantity=quantity,
            unit=unit,
            village=village,
            district=district,
            state=state,
            harvest_date=harvest_date,
            storage_condition=storage_condition,
            image=image_filename
        )

        # 2. Run AI Analysis
        ai_result = AIService.analyze_waste(
            crop_name=crop_name,
            waste_type=waste_type,
            quantity=quantity,
            unit=unit,
            village=village,
            district=district,
            state=state,
            harvest_date=harvest_date,
            storage_condition=storage_condition
        )

        # 3. Save recommendation to database
        RecommendationModel.create_recommendation(
            waste_record_id=record_id,
            recommended_use=ai_result["best_recommended_use"],
            estimated_min_value=ai_result["estimated_min_price"],
            estimated_max_value=ai_result["estimated_max_price"],
            explanation=ai_result["recommendation_reason"],
            environmental_benefit=ai_result["environmental_benefit"],
            scores_json=json.dumps(ai_result["recommendation_scores"])
        )

        flash("Crop waste analyzed successfully by AI!", "success")
        return redirect(url_for("view_analysis", record_id=record_id))

    return render_template("add_waste.html", user=user)

@app.route("/analysis/<int:record_id>")
@login_required
def view_analysis(record_id):
    """Displays detailed AI analysis, scores, value bounds, and environmental indicators."""
    record = WasteModel.get_by_id(record_id)
    if not record or record["user_id"] != session["user_id"]:
        flash("Record not found or access denied.", "warning")
        return redirect(url_for("dashboard"))

    recommendation = RecommendationModel.get_by_waste_record(record_id)
    
    # Calculate environmental metrics
    impact = calculate_environmental_impact(record["crop_name"], record["quantity"], record["unit"])
    
    # Convert unit to total kg
    qty = float(record["quantity"])
    unit = record["unit"].lower()
    total_kg = qty * 1000 if unit == "ton" else (qty * 100 if unit == "quintal" else qty)
    
    min_val_total = total_kg * (recommendation["estimated_min_value"] if recommendation else 0)
    max_val_total = total_kg * (recommendation["estimated_max_value"] if recommendation else 0)

    # Nearby matching buyers
    matching_buyers = BuyerService.find_matching_buyers(
        crop_or_waste=record["crop_name"],
        location=record["district"]
    )[:3]

    return render_template(
        "analysis.html",
        record=record,
        rec=recommendation,
        impact=impact,
        total_kg=total_kg,
        min_val_total=min_val_total,
        max_val_total=max_val_total,
        matching_buyers=matching_buyers
    )

@app.route("/records")
@login_required
def history():
    """List of all submitted waste records for the logged-in farmer."""
    records = WasteModel.get_user_records(session["user_id"])
    return render_template("history.html", records=records)

@app.route("/records/<int:record_id>/delete", methods=["POST"])
@login_required
def delete_record(record_id):
    """Delete a waste record."""
    success = WasteModel.delete_record(record_id, user_id=session["user_id"])
    if success:
        flash("Waste record deleted.", "info")
    else:
        flash("Could not delete record.", "danger")
    return redirect(url_for("history"))

# -------------------------------------------------------------
# Buyer Finder & Nearby Map Routes
# -------------------------------------------------------------

@app.route("/buyers")
def find_buyers():
    """Buyer finder directory with category, crop, and location filters."""
    category = request.args.get("category", "").strip()
    crop = request.args.get("crop", "").strip()
    location = request.args.get("location", "").strip()

    # If logged-in user and no location filter specified, default to farmer's district
    if not location and "user_district" in session:
        location = session["user_district"]

    buyers = BuyerService.find_matching_buyers(
        crop_or_waste=crop,
        category=category,
        location=location
    )

    return render_template(
        "buyers.html",
        buyers=buyers,
        selected_category=category,
        selected_crop=crop,
        selected_location=location
    )

@app.route("/map")
def nearby_map():
    """Interactive OpenStreetMap / Leaflet interface displaying farmer and buyer locations."""
    location_name = request.args.get("location", "")
    if not location_name and "user_district" in session:
        location_name = session["user_district"]
    if not location_name:
        location_name = "Guntur"

    map_data = BuyerService.get_map_markers(farmer_location_name=location_name)
    return render_template("map.html", map_data=map_data, farmer_location_name=location_name)

@app.route("/api/map-data")
def api_map_data():
    """JSON API providing farmer coordinates and demo buyer pins."""
    location_name = request.args.get("location", "Guntur")
    data = BuyerService.get_map_markers(farmer_location_name=location_name)
    return jsonify(data)

# -------------------------------------------------------------
# AI Assistant & Environmental Impact Routes
# -------------------------------------------------------------

@app.route("/assistant")
def assistant():
    """AI Crop Waste Assistant chatbot page."""
    return render_template("assistant.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """JSON endpoint for Waste Assistant chatbot."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    language = data.get("language", "en").strip()

    if not message:
        return jsonify({"error": "Empty message received"}), 400

    result = AIService.chat_assistant(message, language=language)
    return jsonify(result)

@app.route("/impact", methods=["GET", "POST"])
def environmental_impact():
    """Environmental Impact Calculator page."""
    crop = request.form.get("crop", "Paddy")
    qty_str = request.form.get("quantity", "1.0")
    unit = request.form.get("unit", "ton")

    try:
        qty = float(qty_str)
    except ValueError:
        qty = 1.0

    impact_data = calculate_environmental_impact(crop, qty, unit)
    return render_template("impact.html", impact=impact_data, crop=crop, quantity=qty, unit=unit)

# -------------------------------------------------------------
# Admin Dashboard & Management Routes
# -------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_username"] = admin["username"]
            flash("Welcome to the Admin Control Panel.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")
            return render_template("login.html", is_admin_tab=True)

    return render_template("login.html", is_admin_tab=True)

@app.route("/admin/logout")
def admin_logout():
    """Admin logout."""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with Chart.js visualizations and system statistics."""
    analytics = WasteModel.get_admin_analytics()
    recent_users = UserModel.get_all_users()[:5]
    recent_waste = WasteModel.get_all_records()[:5]
    return render_template(
        "admin/dashboard.html",
        analytics=analytics,
        recent_users=recent_users,
        recent_waste=recent_waste
    )

@app.route("/admin/users")
@admin_required
def admin_users():
    """View registered farmers."""
    users = UserModel.get_all_users()
    return render_template("admin/users.html", users=users)

@app.route("/admin/waste")
@admin_required
def admin_waste():
    """View and inspect all waste submissions."""
    records = WasteModel.get_all_records()
    return render_template("admin/waste.html", records=records)

@app.route("/admin/buyers", methods=["GET", "POST"])
@admin_required
def admin_buyers():
    """Manage demo buyers (Add, edit, delete)."""
    if request.method == "POST":
        action = request.form.get("action", "add")
        
        if action == "add":
            BuyerModel.create(
                business_name=request.form.get("business_name"),
                category=request.form.get("category"),
                waste_types=request.form.get("waste_types"),
                village=request.form.get("village"),
                district=request.form.get("district"),
                state=request.form.get("state"),
                latitude=request.form.get("latitude") or None,
                longitude=request.form.get("longitude") or None,
                capacity=request.form.get("capacity"),
                contact=request.form.get("contact"),
                is_demo=1
            )
            flash("New Demo Buyer added successfully.", "success")
        elif action == "edit":
            buyer_id = request.form.get("buyer_id")
            BuyerModel.update(
                buyer_id=buyer_id,
                business_name=request.form.get("business_name"),
                category=request.form.get("category"),
                waste_types=request.form.get("waste_types"),
                village=request.form.get("village"),
                district=request.form.get("district"),
                state=request.form.get("state"),
                latitude=request.form.get("latitude") or None,
                longitude=request.form.get("longitude") or None,
                capacity=request.form.get("capacity"),
                contact=request.form.get("contact")
            )
            flash("Demo Buyer updated successfully.", "success")

        return redirect(url_for("admin_buyers"))

    buyers = BuyerModel.get_all()
    return render_template("admin/buyers.html", buyers=buyers)

@app.route("/admin/buyers/<int:buyer_id>/delete", methods=["POST"])
@admin_required
def admin_delete_buyer(buyer_id):
    """Delete buyer record."""
    BuyerModel.delete(buyer_id)
    flash("Buyer deleted.", "info")
    return redirect(url_for("admin_buyers"))

# -------------------------------------------------------------
# Global Error Handlers
# -------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template("base.html", error_title="Page Not Found (404)",
                           error_message="The page you are looking for does not exist. Please use the navigation above."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", error_title="Temporary System Error (500)",
                           error_message="Sorry, we couldn't complete your request right now. Please try again in a moment."), 500

# -------------------------------------------------------------
# Main Application Runner
# -------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("\n" + "="*60)
    print("[*] AGRIVALUE - APPLICATION STARTED")
    print(f"Server running at: http://127.0.0.1:{Config.PORT}")
    print("Demo Farmer:  farmer@demo.org / farmer123 (or mobile 9876543210)")
    print("Demo Admin:   admin / admin123")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
