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

def get_gridfs():
    """HELPER FUNCTION TO ACCESS GRIDFS"""
    return gridfs.GridFS(current_app.db)


@views.route('/')
def launch():
    return render_template("launch.html")


@views.route('/signup-options')
def sign_options():
    return render_template("signin_options.html")


@views.route('/dashboard')
def dashboard():
    return render_template("dash_search.html")


@views.route('/validation', methods=['GET', 'POST'])
def link_validation():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url', '')

        email = session.get('email')
        if not email:
            return jsonify({'error': 'User not logged in'}), 401

        validURL, invalidURL, alreadyRegistered = url_validation(email, url)

        print(
            f"✅ [DEBUG] Validation Results → valid: {validURL}, invalid: {invalidURL}, alreadyRegistered: {alreadyRegistered}")

        if validURL == 0 and invalidURL == 0 and alreadyRegistered == 0:
            session['validated_url'] = url  # Store URL in session
            session.modified = True  # Mark session as modified
            print(f"✅ [DEBUG] Stored in session: {session.get('validated_url')}")

        print("🔍 [DEBUG] Session content after validation:", dict(session))  # Print session contents

        return jsonify({
            'validURL': validURL,
            'alreadyRegistered': alreadyRegistered,
            'invalidURL': invalidURL
        })

    return render_template("link_validation.html")


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
        fs = get_gridfs()

        for file in proof_id_files:
            if file:
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename, content_type=file.content_type)
                file_ids.append(file_id)

        for file in ownership_files:
            if file:
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename, content_type=file.content_type)
                file_ids.append(file_id)

        db = current_app.db

        user = db.users.find_one({"email": email})
        if not user:
            flash("user account not found. use correct email")
            return redirect(url_for('auth.sign_up'))

        db.users.update_one(
            {"email": email},
            {"$set": {
                "registered_url": url,
                "proof_id_files": file_ids[:len(proof_id_files)],
                "ownership_files": file_ids[len(proof_id_files):]
            }}
        )

        flash("Domain", "success")
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
