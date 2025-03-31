from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = current_app.db

        # Validate user credentials
        user = db.users.find_one({"email": email, "password": password})

        if user:
            session['user_id'] = str(user['_id'])  # This is the unique MongoDB ID
            session['email'] = user['email']

            flash('LOG IN SUCCESSFUL!', category='success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('WRONG CREDENTIALS', category='error')

    return render_template("login.html")


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', category='info')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_email = request.form.get('confirmEmail')
        confirm_password = request.form.get('confirmPassword')

        db = current_app.db

        if email != confirm_email:
            flash('EMAIL DOES NOT MATCH!', category='error')
            return redirect(url_for('auth.sign_up'))
        if password != confirm_password:
            flash('PASSWORD DOES NOT MATCH!', category='error')
            return redirect(url_for('auth.sign_up'))
        if db.users.find_one({"email": email}):
            flash('EMAIL ALREADY EXISTS.', category='error')
            return redirect(url_for('auth.sign_up'))

        user = User(db)
        user_id = user.signup(first_name, last_name, email, password)

        flash('ACCOUNT CREATED SUCCESSFULLY! PLEASE LOG IN.', category='success')
        return redirect(url_for('auth.login'))

    return render_template("signup.html")
