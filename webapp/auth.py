from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from .models import User
from . import db
import os
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.users.find_one({"email": email, "password" : password})
        if user:
            flash('Log In Successful!', category= 'success')
            return redirect(url_for('views.dashboard'))
        else:


    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "Log Out"

@auth.route('/sign-up')
def sign_up():
    return render_template("signup.html")

