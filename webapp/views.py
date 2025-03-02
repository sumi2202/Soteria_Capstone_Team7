from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session, \
    current_app
from .backend_scripts.URLValidation import url_validation
from .models import Rating
import os

views = Blueprint('views', __name__)


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

        if validURL:
            session['validated_url'] = url
            session.modified = True
            print("✅ Stored in session:", session.get('validated_url'))

        return jsonify({
            'validURL': validURL,
            'alreadyRegistered': alreadyRegistered,
            'invalidURL': invalidURL
        })
    return render_template("link_validation.html")


@views.route('/register-link', methods=['GET', 'POST'])
def link_registration():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        url = session.get('validated_url')
        print("🔍 Retrieved from session:", url)

        if not url:
            flash("No validated URL found. Please validate URL first", "error")
            return redirect(url_for("views.link_validation"))

        db = current_app.db

        user = db.users.find_one({"email": email})
        if not user:
            flash("user account not found. use correct email")
            return redirect(url_for('auth.sign_up'))

        db.users.update_one(
            {"email": email},
            {"$set": {"registered_url": url}}
        )

        flash("Domain", "success")
        return redirect(url_for('views.dashboard'))

    validated_url = session.get('validated_url', '')
    print("📌 Sending to template:", validated_url)
    return render_template("link_registration.html", validated_url=validated_url)


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
