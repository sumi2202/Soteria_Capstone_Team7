from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from backend_scripts.URLValidation import url_validation
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
    data = request.json
    email = data.get('email','')
    url = data.get('url','')

    validURL, alreadyRegistered = url_validation(email, url)

    return jsonify({
        'validURL' : validURL,
        'alreadyRegistered' : alreadyRegistered
    })
    return render_template("link_validation.html")

@views.route('/register-link')
def link_registration():
    return render_template("link_registration.html")



