from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session, current_app
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

        return jsonify({
            'validURL': validURL,
            'alreadyRegistered': alreadyRegistered,
            'invalidURL': invalidURL
        })
    return render_template("link_validation.html")


@views.route('/register-link')
def link_registration():
    return render_template("link_registration.html")

@views.route('/customer-rating', methods=['GET'])
def customer_rating():
    return render_template('customer_rating.html')


@views.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    rating_data = data.get("rating")

    #User has already submitted a rating (check using session key)
    if session.get('rated', False):
        return jsonify({
            'output_msg': "A rating has already been submitted with this account."
        }), 400

    #Storing rating in the db
    rating = Rating(current_app.db)
    rating_value = rating.store_rating("placeholder", rating_data)

    #changing session flag to indicate rating has been done
    session['rated'] = True

    return jsonify({
        'output_msg': "Your feedback has been submitted, thank you!"
    })
