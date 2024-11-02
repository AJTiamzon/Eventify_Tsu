from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from flask_mail import Mail, Message
from .models import Events16, Users9, Attendee_events8, Attendee_records5, Attendee_Rating_Creator2
from . import db, socketio
from .gen_algo_final import *
import json, csv
from flask_socketio import join_room, leave_room, send, emit
from datetime import datetime
from .views_creator import rooms
from .__init__ import mail

views_attendee = Blueprint('views_attendee', __name__)

@views_attendee.route('/create_event_profile_attendee')
@login_required
def create_event_profile():
    # Get the current user
    user = current_user

    # Pass the user data and images to the template
    return render_template('create_event_profile.html', user=user)
###################################################################################################################################################################################
@views_attendee.route("/video_chat_dashboard_attendee", methods=["POST", "GET"])
@login_required
def video_chat_dashboard_attendee():
    return render_template("video_chat_dashboard.html", user=current_user, role=current_user.role, first_name=current_user.first_name, last_name=current_user.last_name)

@views_attendee.route("/video_join_meeting_attendee", methods=["POST", "GET"])
@login_required
def video_join_meeting_attendee():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/video_create_meeting?roomID={room_id}")
    return render_template("video_join_meeting.html", user=current_user, role=current_user.role, first_name=current_user.first_name, last_name=current_user.last_name)
####################################################################################################################################################################################
@views_attendee.route("/join_room_attendee", methods=["POST", "GET"])
@login_required
def join_room_view():
    """Page where users enter the room code to join."""
    session.clear()

    # Retrieve RSVP events for the current user if they are an attendee
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()
    rsvp_events = []
    if attendee_event and attendee_event.rsvp_events:
        try:
            rsvp_events = json.loads(attendee_event.rsvp_events)
        except (TypeError, json.JSONDecodeError):
            flash("Failed to load RSVP events.", category="error")

    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            return render_template("join_room.html", error="Please enter a room code.", user=current_user, role=current_user.role, name=current_user.first_name, rsvp_events=rsvp_events)

        if code not in rooms:
            return render_template("join_room.html", error="Room does not exist.", user=current_user, role=current_user.role, name=current_user.first_name, rsvp_events=rsvp_events)

        session["room"] = code
        session["name"] = current_user.first_name  # Use the user's first name
        return redirect(url_for('views_attendee.room'))

    return render_template("join_room.html", user=current_user, role=current_user.role, name=current_user.first_name, rsvp_events=rsvp_events)

@views_attendee.route("/room")
@login_required
def room():
    """Chat room view."""
    room_code = session.get("room")
    if room_code is None or room_code not in rooms:
        return redirect(url_for("views_attendee.join_room_view"))

    return render_template("room.html", user=current_user, code=room_code, messages=rooms[room_code]["messages"], role=current_user.role, name=current_user.first_name)

@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    if room not in rooms:
        return 

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    rooms[room]["messages"].append(content)  # Store message in the room
    send(content, to=room)  # Emit message to room
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    
    if room not in rooms:
        return  # Ignore if room does not exist
    
    join_room(room)
    rooms[room]["members"] += 1
    send({"name": name, "message": "has entered the room"}, to=room)
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} has left the room {room}")

######################################################################################################################################################### Attendee
@views_attendee.route('/attendee', methods=['GET', 'POST'])
def attendee():
    return render_template('attendee.html', user=current_user, name=current_user.first_name)

@views_attendee.route('/attendee_invites', methods=['GET', 'POST'])
@login_required
def attendee_invites():

    # Get the invites stored in the Attendee_events8 table
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()
    
    invited_events = []
    if attendee_event and attendee_event.invites:
        invited_events = json.loads(attendee_event.invites)

    return render_template('attendee_invites.html', user=current_user, name=current_user.first_name, invited_events=invited_events)

@views_attendee.route('/accept_invite', methods=['POST'])
@login_required
def accept_invite():
    event_name = request.form.get('event_name')
    creator_name = request.form.get('creator_name')  # Get creator name from the form
    
    # Find the event in the Events16 table
    event = Events16.query.filter_by(event_name=event_name).first()
    
    if not event:
        # If event is not found, redirect with an error message
        flash("Event not found.", category="error")
        return redirect(url_for('views_attendee.attendee_invites'))

    try:
        # Check the current number of RSVP attendees
        rsvp_attendees = json.loads(event.rsvp_attendees) if event.rsvp_attendees else []
    except (TypeError, json.JSONDecodeError):
        rsvp_attendees = []
        flash("Failed to load RSVP attendees.", category="error")

    current_rsvp_count = len(rsvp_attendees)

    # Compare with max_attendee_num
    if current_rsvp_count >= event.max_attendee_num:
        # Event is full, flash a message and redirect without saving
        flash("Event is full.", category="error")
        return redirect(url_for('views_attendee.attendee_invites'))

    # Proceed with accepting the invite if the event is not full
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()
    if attendee_event:
        try:
            rsvp_events = json.loads(attendee_event.rsvp_events) if attendee_event.rsvp_events else []
        except (TypeError, json.JSONDecodeError):
            rsvp_events = []
            flash("Failed to load RSVP events.", category="error")
        
        # Append new RSVP event details
        rsvp_events.append({
            'event_name': event.event_name,
            'event_desc': event.event_desc,
            'room_code': event.room_code,
            'start_date': str(event.start_date),
            'end_date': str(event.end_date),
            'event_privacy': event.event_privacy,
            'creator_name': creator_name  # Use creator's name from the form
        })
        attendee_event.rsvp_events = json.dumps(rsvp_events)

        # Save the event in Attendee_records5 when attendee accepts
        new_attendee_record = Attendee_records5(
            event_name=event.event_name,
            event_desc=event.event_desc,
            event_privacy=event.event_privacy,
            start_date=event.start_date,
            end_date=event.end_date,
            attendee_id=current_user.id,  # Save the attendee's user ID
            creator_name=creator_name  # Store creator's name in the attendee record
        )
        db.session.add(new_attendee_record)

        # Remove the accepted event from invites
        try:
            invites = json.loads(attendee_event.invites) if attendee_event.invites else []
        except (TypeError, json.JSONDecodeError):
            invites = []
            flash("Failed to load invites.", category="error")

        updated_invites = [inv for inv in invites if inv['event_name'] != event_name]
        attendee_event.invites = json.dumps(updated_invites)

    else:
        # Create a new entry for the attendee if it doesn't exist
        new_attendee_event = Attendee_events8(
            user_id=current_user.id,
            rsvp_events=json.dumps([{
                'event_name': event.event_name,
                'event_desc': event.event_desc,
                'room_code': event.room_code,
                'start_date': str(event.start_date),
                'end_date': str(event.end_date),
                'event_privacy': event.event_privacy,
                'creator_name': creator_name  # Add creator's name from the form
            }]),
            invites=json.dumps([])  # Initialize invites as empty if needed
        )
        db.session.add(new_attendee_event)

    msg = Message(
        f"RSVP Spot to {event.event_name}",
        sender='noreply@eventify.com',
        recipients={current_user.email}
        )
    msg.body = f"Hello! You have accepted the invite and have succesfully RSVPed a spot to attend the event '{event.event_name}' by {creator_name}.\n\nDescription: {event.event_desc}\nStart Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nEnd Date: {event.end_date.strftime('%Y-%m-%d %H:%M')}. For more information, go to the wesbite and view your ticket."
    mail.send(msg)

    # Add the user's details to the event's RSVP attendees in Events16
    rsvp_attendees.append({
        'attendee_name': current_user.first_name,
        'attendee_lname': current_user.last_name,
        'attendee_email': current_user.email
    })
    event.rsvp_attendees = json.dumps(rsvp_attendees)

    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to save the RSVP: {str(e)}", category="error")
        return redirect(url_for('views_attendee.attendee_invites'))

    return redirect(url_for('views_attendee.attendee_invites'))

@views_attendee.route('/reject_invite', methods=['POST'])
@login_required
def reject_invite():
    event_name_to_remove = request.form.get('event_name')
    reject_reason = request.form.get('reject_reason')

    # Find the Attendee's event invites
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()

    if attendee_event and attendee_event.invites:
        # Parse the JSON stored in the invites field
        invites = json.loads(attendee_event.invites)

        # Filter out the event to reject
        updated_invites = [event for event in invites if event['event_name'] != event_name_to_remove]

        # Save the rejection information
        rejected_invites = json.loads(attendee_event.rejected_invites or '[]')
        rejected_invites.append({
            'event_name': event_name_to_remove,
            'reject_reason': reject_reason,
            'attendee_name': current_user.first_name,
            'attendee_lname': current_user.last_name,
            'attendee_email': current_user.email
        })

        # Convert the updated invite list back to JSON format
        attendee_event.invites = json.dumps(updated_invites)
        attendee_event.rejected_invites = json.dumps(rejected_invites)

        # Commit the changes to the database
        db.session.commit()

    return redirect(url_for('views_attendee.attendee_invites'))

@views_attendee.route('/attendee_browse', methods=['GET', 'POST'])
def attendee_browse():
    # Fetch only public events
    public_events = Events16.query.filter_by(event_privacy="Public").all()
    events_data = []
    
    for event in public_events:
        # Get event creator's name from Users9 table
        creator = Users9.query.get(event.user_id)
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"

        events_data.append({
            'event_name': event.event_name,
            'event_desc': event.event_desc,
            'creator_name': creator_name,
            'room_code': event.room_code,
            'start_date': event.start_date.strftime("%Y-%m-%d %H:%M"),
            'end_date': event.end_date.strftime("%Y-%m-%d %H:%M")
        })
    return render_template('attendee_browse.html', user=current_user, name=current_user.first_name, public_events=events_data)

@views_attendee.route('/rsvp_spot', methods=['POST'])
@login_required
def rsvp_spot():
    event_name = request.form.get('event_name')
    creator_name = request.form.get('creator_name')

    # Find the event in the Events16 table
    event = Events16.query.filter_by(event_name=event_name).first()

    if event:
        # Check if the current number of RSVP attendees has reached the max attendee number
        rsvp_attendees = json.loads(event.rsvp_attendees) if event.rsvp_attendees else []
        if len(rsvp_attendees) >= event.max_attendee_num:
            flash("Event is Full", "error")
            return redirect(url_for('views_attendee.attendee_browse'))

        # Check if the event is already saved for the current user in Attendee_events8
        attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()

        if attendee_event:
            # Check if this event is already in the user's RSVP list
            rsvp_events = json.loads(attendee_event.rsvp_events) if attendee_event.rsvp_events else []
            for rsvp_event in rsvp_events:
                if rsvp_event['event_name'] == event.event_name:
                    flash("You have already RSVP'd to this event.", "error")
                    return redirect(url_for('views_attendee.attendee_browse'))

            # Add the event to the current user's RSVP events
            rsvp_events.append({
                'event_name': event.event_name,
                'event_desc': event.event_desc,
                'room_code': event.room_code,
                'start_date': str(event.start_date),
                'end_date': str(event.end_date),
                'event_privacy': event.event_privacy,
                'creator_name': creator_name  # Use creator's name from the form
            })
            attendee_event.rsvp_events = json.dumps(rsvp_events)
        else:
            # Create a new entry for the attendee if it doesn't exist
            new_attendee_event = Attendee_events8(
                user_id=current_user.id,
                rsvp_events=json.dumps([{
                    'event_name': event.event_name,
                    'event_desc': event.event_desc,
                    'room_code': event.room_code,
                    'start_date': str(event.start_date),
                    'end_date': str(event.end_date),
                    'event_privacy': event.event_privacy,
                    'creator_name': creator_name  # Add creator's name from the form
                }])
            )
            db.session.add(new_attendee_event)

        # Save the event in Attendee_records5
        new_attendee_record = Attendee_records5(
            event_name=event.event_name,
            event_desc=event.event_desc,
            event_privacy=event.event_privacy,
            start_date=event.start_date,
            end_date=event.end_date,
            attendee_id=current_user.id,  # Save the attendee's user ID
            creator_name=creator_name  # Store creator's name in the attendee record
        )
        db.session.add(new_attendee_record)

        msg = Message(
        f"RSVP Spot to {event.event_name}",
        sender='noreply@eventify.com',
        recipients={current_user.email}
        )
        msg.body = f"Hello! You have RSVPed a spot to attend the event '{event.event_name}' by {creator_name}.\n\nDescription: {event.event_desc}\nStart Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nEnd Date: {event.end_date.strftime('%Y-%m-%d %H:%M')}. \n For more information, go to the wesbite and view your ticket."
        mail.send(msg)

        # Add the user's details to the event's RSVP attendees in Events16
        rsvp_attendees.append({
            'attendee_name': current_user.first_name,
            'attendee_lname': current_user.last_name,
            'attendee_email': current_user.email
        })
        event.rsvp_attendees = json.dumps(rsvp_attendees)

        db.session.commit()
        flash("Successfully RSVP'd to the event!", "success")

    return redirect(url_for('views_attendee.attendee_browse'))

@views_attendee.route('/attendee_events', methods=['GET', 'POST'])
@login_required
def attendee_events():
    attendee_event = Attendee_events8.query.filter_by(user_id=current_user.id).first()
    
    attending_events = []
    if attendee_event and attendee_event.rsvp_events:
        attending_events = json.loads(attendee_event.rsvp_events)
    
    return render_template('attendee_events.html', user=current_user, name=current_user.first_name, attending_events=attending_events)

@views_attendee.route('/attendee_history')
@login_required
def attendee_history():
    # Query all records where the current user is the attendee
    attendee_history = Attendee_records5.query.filter_by(attendee_id=current_user.id).all()

    # Pass the current time to the template for comparison
    now = datetime.now()

    return render_template('attendee_history.html', user=current_user, attendee_history=attendee_history, now=now, name=current_user.first_name)

@views_attendee.route('/attendee_rate_creator', methods=['POST'])
@login_required
def attendee_rate_creator():
    # Get the event creator's full name from the form
    creator_name = request.form.get('creator_name')

    # Query the Users9 table to find the event creator by full name
    creator = Users9.query.filter_by(fullname=creator_name).first()

    if not creator:
        flash('Creator not found!', category='error')
        return redirect(url_for('views_attendee.attendee_history'))

    # Render the rating page and pass the creator's details
    return render_template('attendee_rate_creator.html', user=current_user, creator=creator)

@views_attendee.route('/submit_event_creator_rating', methods=['POST'])
@login_required
def submit_event_creator_rating():
    # Get the form data
    rating = request.form.get('rating')
    feedback = request.form.get('feedback')
    creator_name = request.form.get('creator_name')

    # Extract the current user's details for the reviewer
    reviewer_firstname = current_user.first_name
    reviewer_lastname = current_user.last_name
    reviewer_role = current_user.role

    # Check if this reviewer has already rated this creator in the past 30 days
    recent_rating = Attendee_Rating_Creator2.query.filter_by(
        creator_name=creator_name,
        reviewer_firstname=reviewer_firstname,
        reviewer_lastname=reviewer_lastname,
        attendee_id=current_user.id  # Ensure the current user is the reviewer
    ).order_by(Attendee_Rating_Creator2.date_reviewed.desc()).first()

    if recent_rating:
        # Calculate the difference between now and the last review date
        days_since_last_review = (datetime.now() - recent_rating.date_reviewed).days
        if days_since_last_review < 30:
            flash(f'You have already rated {creator_name} within the last 30 days. Please try again after {30 - days_since_last_review} days.', category='error')
            return redirect(url_for('views_attendee.attendee_history'))

    # If no recent rating or 30 days have passed, create a new rating record
    new_rating = Attendee_Rating_Creator2(
        creator_name=creator_name,
        reviewer_firstname=reviewer_firstname,
        reviewer_lastname=reviewer_lastname,
        reviewer_role=reviewer_role,
        attendee_id=current_user.id,  # ID of the logged-in user (the reviewer)
        rating=rating,
        feedback=feedback,
        date_submitted=datetime.now()
    )

    # Add the new rating to the database
    db.session.add(new_rating)
    db.session.commit()

    flash('Your rating has been submitted successfully!', category='success')
    return redirect(url_for('views_attendee.attendee_history'))

@views_attendee.route('/view_creator_info', methods=['POST'])
@login_required
def view_creator_info():
    # Get the creator's name from the form
    creator_name = request.form.get('creator_name')
    
    # Query the database to find the user by their name
    creator = Users9.query.filter(
        (Users9.first_name + " " + Users9.last_name) == creator_name
    ).first()

    if not creator:
        flash('Creator not found!', category='error')
        return redirect(url_for('views_attendee.attendee_invites'))

    # Query the Attendee_Rating_Creator2 table to find all ratings for this creator
    ratings = Attendee_Rating_Creator2.query.filter_by(creator_name=creator_name).all()

    # Render the creator details along with the ratings on a new page
    return render_template('attendee_creator_view.html', creator=creator, ratings=ratings, user=current_user)