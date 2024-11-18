from gevent import monkey
from gevent.pool import Pool
# Patching to make the Mail sending function non-blocking
monkey.patch_all()
# Initialize a pool of workers for gevent
email_pool = Pool(10)  # You can adjust the pool size based on your needs

from flask import Flask, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
import os
from flask import current_app

db = SQLAlchemy()
DB_NAME = "database.db"
socketio = SocketIO()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'I am a hacker!'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')  # Set UPLOAD_FOLDER here
    db.init_app(app)
    socketio.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'       # e.g., 'smtp.gmail.com' for Gmail
    app.config['MAIL_PORT'] = 465                         # Port number, usually 587 for TLS
    app.config['MAIL_USERNAME'] = 'adrianjennelltiamzon@gmail.com' # Your email address
    app.config['MAIL_PASSWORD'] = 'iuit qpqh xngf rckk'         # Your email password
    app.config['MAIL_DEFAULT_SENDER'] = 'adrianjennelltiamzon@gmail.com' # Default sender
    app.config['MAIL_USE_TLS'] = False                     # Enable TLS
    app.config['MAIL_USE_SSL'] = True                     # Enable SSL
    mail.init_app(app)

    # Set up Flask-Admin
    setup_admin(app)

    from .views import views
    from .views_creator import views_creator
    from .views_attendee import views_attendee
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(views_creator, url_prefix='/')
    app.register_blueprint(views_attendee, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Users9

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users9.query.get(int(id))

    return app

def send_async_email(app, msg):
    """ Function to send emails asynchronously in the background """
    with app.app_context():
        mail.send(msg)

def send_email_async(recipient_emails, subject, body):
    """ Function to send email in the background """
    msg = Message(
        subject,
        sender='noreply@eventify.com',
        recipients=recipient_emails
    )
    msg.body = body
    # Sending email asynchronously with gevent
    # Ensure the 'app' is passed to the worker correctly
    email_pool.spawn(send_async_email, current_app._get_current_object(), msg)

# Function to set up Flask-Admin
def setup_admin(app):
    # Create the custom Admin index view class right here
    class CustomAdminIndexView(AdminIndexView):
        @expose('/')
        def index(self):
            return self.render('admin/custom_admin_dashboard.html')

    # Initialize Admin with the custom index view
    admin = Admin(app, name='Event Management', template_mode='bootstrap3', index_view=CustomAdminIndexView())
    
    # Add your models to Flask-Admin
    from .models import Users9, Events17, Attendee_events8, Event_records11, Client_Attend_Events3, Client_Hired_Suppliers6, SupplierRating3

    admin.add_view(UserAdminView(Users9, db.session))
    admin.add_view(RestrictedModelView(Events17, db.session))
    admin.add_view(RestrictedModelView(Attendee_events8, db.session))
    admin.add_view(RestrictedModelView(Event_records11, db.session))
    admin.add_view(RestrictedModelView(Client_Attend_Events3, db.session))
    admin.add_view(RestrictedModelView(Client_Hired_Suppliers6, db.session))
    admin.add_view(RestrictedModelView(SupplierRating3, db.session))

class RestrictedModelView(ModelView):
    column_exclude_list = []  # Show all columns by default
    
    def is_accessible(self):
        # Only allow access to Admins
        return current_user.is_authenticated and current_user.role == 'Admin'

    def inaccessible_callback(self, name, **kwargs):
        # Redirect users who don't have access
        return redirect(url_for('auth.login'))

class UserAdminView(RestrictedModelView):
    column_exclude_list = ['password']  # Don't show password
    form_excluded_columns = ['password']  # Don't allow password editing
    column_searchable_list = ['first_name', 'last_name', 'email']

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
