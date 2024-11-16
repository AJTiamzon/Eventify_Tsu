from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class Users9(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    fullname = db.Column(db.String(150))
    role = db.Column(db.String(50))
    past_experience = db.Column(db.String)
    last_profile_update = db.Column(db.DateTime, nullable=True)
    admin_strikes = db.Column(db.Integer)
    events = db.relationship('Events17')
    attend = db.relationship('Attendee_events8')
    client_events = db.relationship('Client_events7')
    event_records = db.relationship('Event_records11', backref='creator')  # New relationship
    # New credibility columns
    credibility1 = db.Column(db.String(300), nullable=True)
    credibility2 = db.Column(db.String(300), nullable=True)
    credibility3 = db.Column(db.String(300), nullable=True)
    credibility4 = db.Column(db.String(300), nullable=True)
    credibility5 = db.Column(db.String(300), nullable=True)


class Events17(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data1 = db.Column(db.String)  # Store data as JSON string
    room_code = db.Column(db.String)
    event_name = db.Column(db.String)
    event_desc = db.Column(db.String)  # New column for event description
    event_type = db.Column(db.String)
    event_privacy = db.Column(db.String)  # New column for event status
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users9.id'))
    invited_attendees = db.Column(db.Text)
    rsvp_attendees = db.Column(db.String)
    max_attendee_num = db.Column(db.Integer)  # New column for max attendees
    start_date = db.Column(db.DateTime)  # New column for start time/date
    end_date = db.Column(db.DateTime)  # New column for end time/date
    image_path = db.Column(db.String)


class Attendee_events8(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invites = db.Column(db.Text)  # Store data as JSON string
    rsvp_events = db.Column(db.Text)
    attending_events = db.Column(db.Text)
    rejected_invites = db.Column(db.Text)  # New column to store rejected invites and reasons
    user_id = db.Column(db.Integer, db.ForeignKey('users9.id'))


class Event_records11(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String)
    event_desc = db.Column(db.String)
    event_type = db.Column(db.String)
    event_privacy = db.Column(db.String)
    data1 = db.Column(db.String)
    room_code = db.Column(db.String)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('users9.id'))  # Link to the user who created it
    invited_attendees = db.Column(db.Text)
    rsvp_attendees = db.Column(db.String)
    max_attendee_num = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)  # New column to store the total cost of the event
    supplier_hired_status = db.Column(db.String, nullable=True)  # New field to store hire status as JSON
    image_path = db.Column(db.String)


class Attendee_records5(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_name = db.Column(db.String)
    event_name = db.Column(db.String)
    event_desc = db.Column(db.String)
    event_privacy = db.Column(db.String)
    date_accepted = db.Column(db.DateTime(timezone=True), default=func.now())
    attendee_id = db.Column(db.Integer, db.ForeignKey('users9.id'))  # Link to the attendee
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)


class Client_events7(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data1 = db.Column(db.String)  # Store data as JSON string
    event_name = db.Column(db.String)
    event_type = db.Column(db.String)
    event_desc = db.Column(db.String)  # Add event description
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users9.id'))
    max_attendee_num = db.Column(db.Integer)  # Add max attendees
    start_date = db.Column(db.DateTime)  # Add start time/date
    end_date = db.Column(db.DateTime)  # Add end time/date

class Client_Attend_Events2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String)
    event_desc = db.Column(db.String)
    room_code = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    creator_name = db.Column(db.String)
    client_id = db.Column(db.Integer, db.ForeignKey('users9.id'))
    date_rsvped = db.Column(db.DateTime(timezone=True), default=func.now())  # Timestamp when RSVP'd

class Client_Hired_Suppliers5(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)  # Reference to Users9
    supplier_name = db.Column(db.String(150))
    supplier_business_name = db.Column(db.String(150))
    supplier_contact_number = db.Column(db.String(150))
    supplier_email = db.Column(db.String(150))
    supplier_type = db.Column(db.String(150))
    supplier_price = db.Column(db.Float)
    supplier_rating = db.Column(db.Float)
    date_hired = db.Column(db.DateTime(timezone=True), default=func.now())
    hired_status = db.Column(db.Boolean, default=False)  # New boolean column

class SupplierRating3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(150))  # Store the supplier's name
    rating = db.Column(db.Float)
    feedback = db.Column(db.String(5000))
    reviewer_name = db.Column(db.String(150))  # Store the reviewer's full name
    reviewer_role = db.Column(db.String(50))  # Store the role of the reviewer
    date_reviewed = db.Column(db.DateTime(timezone=True), default=func.now())  # Date when the rating was submitted

class Attendee_Rating_Creator2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_name = db.Column(db.String(150))
    reviewer_firstname = db.Column(db.String(150))
    reviewer_lastname = db.Column(db.String(150))
    reviewer_role = db.Column(db.String(150))
    date_reviewed = db.Column(db.DateTime(timezone=True), default=func.now())
    attendee_id = db.Column(db.Integer, db.ForeignKey('users9.id'))  # Link to the attendee who rated
    rating = db.Column(db.Float)
    feedback = db.Column(db.Text)
    date_submitted = db.Column(db.DateTime(timezone=True), default=func.now())

