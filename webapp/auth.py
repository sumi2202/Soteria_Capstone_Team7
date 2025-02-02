from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from user.models import User
import os
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "Log Out"

@auth.route('/sign-up')
def sign_up():
    return render_template("signup.html")

