from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory

views = Blueprint('views', __name__)

@views.route('/')
def launch():
    return render_template("launch.html")

@views.route('/signup-options')
def sign_options():
    return "sign up or log in"


