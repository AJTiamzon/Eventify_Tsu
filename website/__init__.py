from flask import Flask, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
import os
import threading
import dns.resolver  # Ensure DNS compatibility

db = SQLAlchemy()
DB_NAME = "database.db"
socketio = SocketIO()
mail = Mail()

def create_app():
    # Enable Eventlet monkey patching
    import eventlet
    eventlet.monkey_patch()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'I am a hacker!'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')  # Set UPLOAD_FOLDER here
    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")  # Ensure Eventlet async_mode

    # Configure Flask-Mail
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USERNAME='adrianjennelltiamzon@gmail.com',
        MAIL_PASSWORD='iuit qpqh xngf rckk',
        MAIL_DEFAULT_SENDER='adrianjennelltiamzon@gmail.com',
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
    )
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

    # Ensure proper DNS configuration for Eventlet
    configure_dns()

    return app

# Function to configure DNS for compatibility
def configure_dns():
    try:
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=True)
        print("DNS resolver successfully configured.")
    except Exception as e:
        print(f"DNS configuration failed: {e}")

# Function to set up Flask-Admin
def setup_admin(app):
    class CustomAdminIndexView(AdminIndexView):
        @expose('/')
        def index(self):
            return self.render('admin/custom_admin_dashboard.html')

    admin = Admin(app, name='Event Management', template_mode='bootstrap3', index_view=CustomAdminIndexView())

    from .models import Users9, Events17, Attendee_events8, Event_records11, Client_Attend_Events2, Client_Hired_Suppliers5, SupplierRating3

    admin.add_view(UserAdminView(Users9, db.session))
    admin.add_view(RestrictedModelView(Events17, db.session))
    admin.add_view(RestrictedModelView(Attendee_events8, db.session))
    admin.add_view(RestrictedModelView(Event_records11, db.session))
    admin.add_view(RestrictedModelView(Client_Attend_Events2, db.session))
    admin.add_view(RestrictedModelView(Client_Hired_Suppliers5, db.session))
    admin.add_view(RestrictedModelView(SupplierRating3, db.session))

class RestrictedModelView(ModelView):
    column_exclude_list = []  # Show all columns by default

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'Admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

class UserAdminView(RestrictedModelView):
    column_exclude_list = ['password']  # Don't show password
    form_excluded_columns = ['password']  # Don't allow password editing
    column_searchable_list = ['first_name', 'last_name', 'email']

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
