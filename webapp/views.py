import io
from datetime import datetime
import pytz

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session, \
    current_app, send_file
from .backend_scripts.URLValidation import url_validation
from .models import Rating
import os
import gridfs
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from io import BytesIO
from bson import ObjectId
from flask import current_app as app
from gridfs import GridFS


views = Blueprint('views', __name__)

@views.route('/download/<file_id>')
def download_file(file_id):
    db = current_app.db
    fs = gridfs.GridFS(db)

    try:
        file = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file.read()), download_name=file.filename, as_attachment=True)
    except Exception as e:
        flash("File not found or error downloading.")
        return redirect(url_for('views.profile'))
def get_gridfs():
    """HELPER FUNCTION TO ACCESS GRIDFS"""
    return gridfs.GridFS(current_app.db)


@views.route('/')
def launch():
    session.clear()
    flash('You have been logged out.')
    return render_template("launch.html")


@views.route('/signup-options')
def sign_options():
    return render_template("signin_options.html")


@views.route('/dashboard')
def dashboard():
    return render_template("dash_search.html")

@views.route('/profile_page')
def profile():
    if 'email' not in session:
        flash('Please log in to view your profile.')
        return redirect(url_for('auth.login'))

    db = current_app.db
    email = session['email']

    # Get user info from `users` collection
    base_user = db.users.find_one({'email': email})
    if not base_user:
        flash('User not found in users collection.')
        return redirect(url_for('auth.login'))

    # First/last name, password from users collection
    user_first_name = base_user.get('firstName', 'Unknown')
    user_last_name = base_user.get('lastName', 'Unknown')
    user_password = base_user.get('password', 'N/A')

    # ✅ Fetch ALL registered_urls documents for this user
    registered_links_cursor = db.registered_urls.find({'email': email})

    # ✅ Extract all URLs
    user_links = []
    proof_of_id_files = []
    ownership_id_files = []
    verified_statuses = []

    fs = gridfs.GridFS(db)

    for reg_doc in registered_links_cursor:
        # Collect URLs
        if 'url' in reg_doc:
            user_links.append(reg_doc['url'])

        # Optional: Collect verified statuses (if needed)
        verified_statuses.append(reg_doc.get('verified', False))

        # Collect documents for proof of ID & ownership (if you want from all docs)
        proof_ids = reg_doc.get('proof_id_files', [])
        owner_ids = reg_doc.get('ownership_files', [])

        for file_id in proof_ids:
            try:
                file = fs.get(ObjectId(file_id))
                proof_of_id_files.append({'filename': file.filename, 'id': str(file._id)})
            except Exception as e:
                print(f"Proof of ID fetch error: {e}")

        for file_id in owner_ids:
            try:
                file = fs.get(ObjectId(file_id))
                ownership_id_files.append({'filename': file.filename, 'id': str(file._id)})
            except Exception as e:
                print(f"Ownership doc fetch error: {e}")

    # If no documents exist, verified is false, otherwise maybe it's verified
    verified = any(verified_statuses)

    documents = {
        'proof_of_id': proof_of_id_files,
        'ownership_id': ownership_id_files
    }

    return render_template(
        "profile_page.html",
        first_name=user_first_name,
        last_name=user_last_name,
        email=email,
        password=user_password,
        links=user_links,  # ✅ Multiple links from registered_urls
        documents=documents,
        verified=verified
    )

@views.route("/results")
def results_page():
    db = current_app.db

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))

    xss_results = list(db.xss_result.find().sort("timestamp", -1))
    task_ids = [x.get("task_id") for x in xss_results if "task_id" in x]
    sql_results = db.sql_result.find({"task_id": {"$in": task_ids}})
    sql_map = {sql["task_id"]: sql for sql in sql_results}

    # Filter + Format
    valid_results = []
    for xss in xss_results:
        task_id = xss.get("task_id")
        if not task_id or task_id not in sql_map:
            continue

        # Fix timestamp formatting
        raw_timestamp = xss.get("timestamp")
        if isinstance(raw_timestamp, str):
            try:
                raw_timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            except Exception:
                raw_timestamp = None

        formatted = raw_timestamp.strftime("%Y-%m-%d %I:%M %p") if isinstance(raw_timestamp, datetime) else "---"

        valid_results.append({
            "url": xss.get("url", "---"),
            "timestamp": formatted,
            "task_id": task_id,
            "has_results": True
        })

    # PAGINATE AFTER FILTERING
    total = len(valid_results)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated = valid_results[start:end]

    return render_template("result_history.html",
        history=paginated,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )



@views.route('/register-link', methods=['GET', 'POST'])
def link_registration():
    print("🔍 [DEBUG] Entire session before retrieving URL:", dict(session))
    validated_url = session.get('validated_url', '')  # Retrieve from Flask session
    print(f"🚨 [DEBUG] validated_url before rendering template: {validated_url}")

    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        url = session.get('validated_url')
        print("🔍 Retrieved from session:", url)

        if not url:
            flash("No validated URL found. Please validate URL first", "error")
            return redirect(url_for("views.link_validation"))

        proof_id_files = request.files.getlist('proofIdFiles')
        ownership_files = request.files.getlist('ownershipFiles')

        file_ids = []
        fs = current_app.fs  # Use app's GridFS instance

        for file in proof_id_files + ownership_files:
            if file:
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename, content_type=file.content_type)
                file_ids.append(file_id)

        db = current_app.db

        user = db.users.find_one({"email": email})
        if not user:
            flash("User account not found. Use the correct email.", "error")
            return redirect(url_for('auth.sign_up'))

        # Check if URL is already registered
        existing_registration = db.registered_urls.find_one({"email": email, "url": url})
        if existing_registration:
            flash("This URL is already registered.", "info")
            return redirect(url_for('views.dashboard'))

        # Store registration in `registered_urls` collection
        db.registered_urls.insert_one({
            "first_name": first_name,  # ✅ Added
            "last_name": last_name,  # ✅ Added
            "email": email,
            "url": url,
            "proof_id_files": file_ids[:len(proof_id_files)],
            "ownership_files": file_ids[len(proof_id_files):],
            "verified": False
        })

        flash("URL successfully registered!", "success")
        return redirect(url_for('views.dashboard'))

    if not validated_url:
        flash("Session lost. Please validate the URL again.", "error")

    return render_template("link_registration.html", validated_url=validated_url)


@views.route('/view-file/<file_id>', methods=['GET'])
def view_file(file_id):
    try:
        # Convert the string to ObjectId
        file_id = ObjectId(file_id)

        # Fetch the file from GridFS using get_gridfs
        fs = get_gridfs()
        file_data = fs.find_one({"_id": file_id})

        if file_data:
            return send_file(BytesIO(file_data.read()),
                             mimetype='application/pdf')  # Change mimetype based on your file type
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error retrieving file: {e}", 500


@views.route('/check-registered-url', methods=['POST'])
def check_registered_url():
    data = request.get_json()
    url = data.get('url')

    # Get email from session
    email = session.get('email')
    if not email:
        return jsonify({"success": False, "message": "User not logged in."}), 401

    # Check if the URL is registered under the user's email
    db = current_app.db
    registration = db.registered_urls.find_one({"email": email, "url": url})

    if registration:
        return jsonify({"success": True, "message": "URL is registered."})
    else:
        return jsonify({"success": False, "message": "This URL is not registered under your account."})


@views.route('/customer-rating', methods=['GET'])
def customer_rating():
    return render_template('customer_rating.html')


@views.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    rating_data = data.get("rating")

    # User has already submitted a rating (check using session key)
    if session.get('rated', False):
        return jsonify({
            'output_msg': "A rating has already been submitted with this account."
        }), 400

    # Storing rating in the db
    rating = Rating(current_app.db)
    rating_value = rating.store_rating("placeholder", rating_data)

    # changing session flag to indicate rating has been done
    session['rated'] = True

    return jsonify({
        'output_msg': "Your feedback has been submitted, thank you!"
    })
