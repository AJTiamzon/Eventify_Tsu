from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Users9
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import re
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users9.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.role'))
            else:
                flash('Incorrect password, try again.', category='error')
                return render_template("login.html", user=current_user, email=email, password=password)
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


UPLOAD_FOLDER = 'C:/Users/Adrian/Desktop/HTML Guide 2/Capstone/Experiment3/website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        fullname = first_name + " " + last_name
        role = request.form.get('role')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        past_experience = request.form.get('past_experience')

        # Image files for credibility
        credibility_images = []
        for i in range(1, 6):
            image_file = request.files.get(f'credibility{i}')
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(filepath)
                credibility_images.append(filename)
            else:
                credibility_images.append(None)

        # Other validations as before
        password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,}$'
        user = Users9.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not re.match(password_regex, password1):
            flash('Password must be at least 8 characters long, contain at least one capital letter, and one number.', category='error')
        else:
            new_user = Users9(
                email=email, first_name=first_name, last_name=last_name, fullname=fullname,
                role=role, password=generate_password_hash(password1), past_experience=past_experience,
                credibility1=credibility_images[0], credibility2=credibility_images[1],
                credibility3=credibility_images[2], credibility4=credibility_images[3],
                credibility5=credibility_images[4]
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.role'))

        # If validation fails, render the template with the current values
        return render_template('sign_up.html', user=current_user, email=email, 
                               first_name=first_name, last_name=last_name, role=role, 
                               password1=password1, password2=password2, 
                               past_experience=past_experience)

    return render_template("sign_up.html", user=current_user)

@auth.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = current_user
    now = datetime.now()

    # Check if the user has updated their profile in the last 30 days
    if user.last_profile_update and (now - user.last_profile_update) < timedelta(days=30):
        remaining_days = 30 - (now - user.last_profile_update).days
        flash(f'You can only update your profile once every 30 days. Please wait {remaining_days} more day(s).', category='error')
        return redirect(url_for('views_creator.create_event_profile'))

    # Get the form data and update only fields that are not empty
    email = request.form.get('email')
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    past_experience = request.form.get('past_experience')

    if email:
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if past_experience:
        user.past_experience = past_experience

    # Handle file uploads for credibility images
    for i in range(1, 6):
        image_file = request.files.get(f'credibility{i}')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            setattr(user, f'credibility{i}', filename)

    # Update the last profile update date
    user.last_profile_update = now

    db.session.commit()
    flash('Profile updated successfully!', category='success')
    return redirect(url_for('views_creator.create_event_profile'))