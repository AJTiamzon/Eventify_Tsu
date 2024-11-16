from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Users9
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import re, os, random, string
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from .__init__ import mail

auth = Blueprint('auth', __name__)

def generate_verification_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

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

@auth.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    email = request.form.get('email')
    user = Users9.query.filter_by(email=email).first()

    if user:
        # Generate a reset code
        reset_code = generate_verification_code()
        session['reset_code'] = reset_code
        session['reset_email'] = email

        # Send reset code via email
        msg = Message("Password Reset Code", recipients=[email])
        msg.body = f"Your password reset code is: {reset_code}"
        mail.send(msg)

        flash("A password reset code has been sent to your email.", "info")
        return redirect(url_for("auth.reset_password_verify"))
    else:
        flash("Email address not found.", "error")
        return redirect(url_for("auth.login"))

@auth.route('/reset_password_verify', methods=['GET', 'POST'])
def reset_password_verify():
    if request.method == 'POST':
        entered_code = request.form.get('reset_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if entered_code == session.get('reset_code'):
            if new_password == confirm_password:
                password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,}$'
                if re.match(password_regex, new_password):
                    email = session.pop('reset_email', None)
                    user = Users9.query.filter_by(email=email).first()
                    if user:
                        user.password = generate_password_hash(new_password)
                        db.session.commit()
                        flash("Password reset successful! Please log in with your new password.", "success")
                        return redirect(url_for("auth.login"))
                else:
                    flash("Password must contain at least 8 characters, one uppercase letter, and one number.", "error")
            else:
                flash("Passwords don't match.", "error")
        else:
            flash("Incorrect reset code. Please try again.", "error")

    return render_template("reset_password_verify.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf', 'doc', 'docx', 'txt', 'svg', 'webp', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    verification_sent = False  # To control form display in template

    if request.method == 'POST':
        if 'verification_code' in request.form:
            # Verify the code
            entered_code = request.form.get('verification_code')
            if entered_code == session.get('verification_code'):
                sign_up_data = session.pop('sign_up_data', {})
                new_user = Users9(
                    email=sign_up_data['email'],
                    first_name=sign_up_data['first_name'],
                    last_name=sign_up_data['last_name'],
                    fullname=sign_up_data['fullname'],
                    role=sign_up_data['role'],
                    password=generate_password_hash(sign_up_data['password1']),
                    past_experience=sign_up_data['past_experience'],
                    credibility1=sign_up_data['credibility_images'][0],
                    credibility2=sign_up_data['credibility_images'][1],
                    credibility3=sign_up_data['credibility_images'][2],
                    credibility4=sign_up_data['credibility_images'][3],
                    credibility5=sign_up_data['credibility_images'][4]
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account created successfully!", "success")
                return redirect(url_for("views.role"))
            else:
                flash("Incorrect verification code. Please try again.", "error")
                verification_sent = True  # Keep the form in verification mode

        else:
            # Handle sign-up and send verification email
            email = request.form.get('email')
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            fullname = first_name + " " + last_name
            role = request.form.get('role')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            past_experience = request.form.get('past_experience')
            credibility_images = []
            for i in range(1, 6):
                image_file = request.files.get(f'credibility{i}')
                if image_file and allowed_file(image_file.filename):
                    filename = secure_filename(image_file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(filepath)
                    credibility_images.append(filename)
                else:
                    credibility_images.append(None)
            
            # Perform validations
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
                flash("Passwords don't match.", category='error')
            elif not re.match(password_regex, password1):
                flash("Password must contain at least 8 characters, one uppercase letter, and one number.", category='error')
            else:
                # Generate and send verification code
                verification_code = generate_verification_code()
                session['verification_code'] = verification_code
                session['sign_up_data'] = {
                    'email': email, 'first_name': first_name, 'last_name': last_name, 'fullname': fullname,
                    'role': role, 'password1': password1, 'past_experience': past_experience,
                    'credibility_images': credibility_images
                }
                msg = Message("Sign-Up Verification Code", recipients=[email])
                msg.body = f"Your verification code is: {verification_code}"
                mail.send(msg)
                
                flash("A verification code has been sent to your email. Please enter it to complete sign-up.", "info")
                verification_sent = True  # Set to True to show the verification code form

            # If validation fails, render the template with the current values
            return render_template(
                'sign_up.html', user=current_user, email=email, first_name=first_name, 
                last_name=last_name, role=role, password1=password1, password2=password2, 
                past_experience=past_experience, 
                credibility1=credibility_images[0], credibility2=credibility_images[1], 
                credibility3=credibility_images[2], credibility4=credibility_images[3], 
                credibility5=credibility_images[4], verification_sent=verification_sent
            )

    return render_template("sign_up.html", user=current_user, verification_sent=verification_sent)

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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            setattr(user, f'credibility{i}', filename)

    # Update the last profile update date
    user.last_profile_update = now

    db.session.commit()
    flash('Profile updated successfully!', category='success')
    return redirect(url_for('views_creator.create_event_profile'))