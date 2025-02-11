from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
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

@views.route('/validation')
def link_validation():
    return render_template("link_validation.html")

@views.route('/register-link')
def link_registration():
    return render_template("link_registration.html")



