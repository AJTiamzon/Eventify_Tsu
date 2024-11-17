from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Events17, Users9, Attendee_events8, Client_Attend_Events2,Event_records11
from . import db
from .gen_algo_final import *
import json
import csv
from datetime import datetime

views = Blueprint('views', __name__)
# admin_home
######################################################################################################################################################### Home

@views.route('/', methods=['GET', 'POST'])
def home():
    # Fetch only public events
    public_events = Event_records11.query.filter_by(event_privacy="Public").all()
    events_data = []
    
    for event in public_events:
        # Get event creator's name from Users9 table
        creator = Users9.query.get(event.creator_id)
        creator_name = f"{creator.fullname}" if creator else "Unknown"

        events_data.append({
            'event_name': event.event_name,
            'event_desc': event.event_desc,
            'creator_name': creator_name,
            'room_code': event.room_code,
            'image_path': event.image_path,
            'start_date': event.start_date.strftime("%Y-%m-%d %H:%M"),
            'end_date': event.end_date.strftime("%Y-%m-%d %H:%M")
        })
    return render_template('index.html', user = current_user, events_data=events_data)

######################################################################################################################################################### Role Redirection And Calendar

@views.route('/role', methods=['GET', 'POST'])
def role():
    if current_user.role == "Event Creator":
        return redirect(url_for('views_creator.create_event_home'))
    elif current_user.role == "Client":
        return redirect(url_for('views_creator.client_home'))
    elif current_user.role == "Attendee":
        return redirect(url_for('views_attendee.attendee'))
    elif current_user.role == "Admin":
        return redirect(url_for('views_creator.admin_home'))
    else:
        return redirect(url_for('auth.login'))

@views.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html', user = current_user)

@views.route('/fetch-events')
@login_required
def fetch_events():
    events = []

    # Fetch finalized events created by the current user from Event_records7
    event_records = current_user.events  # Assuming a relationship exists in User model
    for event_record in event_records:
        events.append({
            'title': event_record.event_name,
            'start': event_record.start_date.isoformat(),
            'end': event_record.end_date.isoformat(),
            'description': event_record.event_desc,
            'event_privacy': event_record.event_privacy,
        })

    # Fetch RSVP events for the user from Attendee_events8
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()
    if attendee_event and attendee_event.rsvp_events:
        rsvp_events = json.loads(attendee_event.rsvp_events)
        for rsvp_event in rsvp_events:
            events.append({
                'title': rsvp_event['event_name'],
                'start': rsvp_event['start_date'],
                'end': rsvp_event['end_date'],
                'description': rsvp_event['event_desc'],
                'event_privacy': rsvp_event['event_privacy'],
            })
    
    # Fetch RSVP events for the user from Client_Attend_Events2
    client_rsvps = Client_Attend_Events2.query.filter_by(client_id=current_user.id).all()
    for client_rsvp in client_rsvps:
        events.append({
            'title': client_rsvp.event_name,
            'start': client_rsvp.start_date.isoformat(),
            'end': client_rsvp.end_date.isoformat(),
            'description': client_rsvp.event_desc,
            'event_privacy': 'Public',  # Assuming these events are public
        })

    return jsonify(events)

######################################################################################################################################################### Events List

@views.route('/event_list', methods=['GET'])
def event_list():
    # Fetch only public events
    public_events = Event_records11.query.filter_by(event_privacy="Public").all()
    events_data = []
    
    for event in public_events:
        # Get event creator's name from Users9 table
        creator = Users9.query.get(event.creator_id)
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"

        if event.data1:  # Check if data1 is not None
            event_data = json.loads(event.data1)
        else:
            event_data = {}  # Default to an empty dictionary if data1 is None

        events_data.append({
            'event_name': event.event_name,
            'event_desc': event.event_desc,
            'creator_name': creator_name,
            'room_code': event.room_code,
            'image_path': event.image_path,
            'start_date': event.start_date.strftime("%Y-%m-%d %H:%M"),
            'end_date': event.end_date.strftime("%Y-%m-%d %H:%M")
        })

    return render_template("events_list.html", user=current_user, events=events_data)

@views.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    if current_user.role != 'Admin':
        flash('Only admins can add suppliers.', category='error')
        return redirect(url_for('views.role'))

    fullname = request.form.get('fullname')
    business_name = request.form.get('business_name')
    contact_number = request.form.get('contact_number')
    email = request.form.get('email')
    rating = request.form.get('rating')
    price = request.form.get('price')
    supplier_type = request.form.get('type')

    # Append all information to csv_file_path3
    with open(csv_file_path3, mode='a', newline='') as csv_file:
        fieldnames = ['name', 'business_name', 'contact_number', 'email', 'rating', 'price', 'type']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({
            'name': fullname,
            'business_name': business_name,
            'contact_number': contact_number,
            'email': email,
            'rating': rating,
            'price': price,
            'type': supplier_type
        })

    # Map type to the correct CSV and append fullname, rating, and price
    supplier_map = {
        'cake': cake,
        'digital_printing': digital_printing,
        'event_planner': event_planner,
        'grazing_table': grazing_table,
        'makeup_and_hair': makeup_and_Hair,
        'photobooth': photobooth,
        'photographer': photographer,
        'catering': catering,
        'church': church,
        'event_stylist': event_stylist,
        'events_place': events_place,
        'lights_and_sounds': lights_and_sounds,
    }

    csv_file_type = supplier_map.get(supplier_type)
    
    if csv_file_type:
        with open(csv_file_type, mode='a', newline='') as csv_file:
            fieldnames = ['name', 'rating', 'price']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({
                'name': fullname,
                'rating': rating,
                'price': price
            })
    
    flash('Supplier added successfully!', category='success')
    return redirect('/admin')