from flask import Flask, render_template, request, make_response, redirect
from flask_socketio import SocketIO, join_room
import announcement_client
import time
import threading
import humanize
import json
import os
import uuid

app = Flask(__name__)
socketio = SocketIO(app=app)
announcement_client.run_client('webserver')
app.recent_announcements = []
app.announcement_dict = {}

if not os.path.exists('announcement_presets.json'):
    announcement_preset_f = open('announcement_presets.json', 'x')
    announcement_preset_f.write('[]')
    announcement_preset_f.close()
    announcement_presets = []
else:
    announcement_presets_f = open('announcement_presets.json', 'r')
    announcement_presets = json.loads(announcement_presets_f.read())
    announcement_presets_f.close()

@announcement_client.announcement_callback
def handle_announcement(message, sender):
    current_time = time.time()
    announcement_uuid = str(uuid.uuid4())
    app.recent_announcements.append({
        'time_sent': current_time,
        'message': message,
        'from': sender,
        'uuid': announcement_uuid
    })
    app.announcement_dict[announcement_uuid] = {
        'time_sent': current_time,
        'message': message,
        'from': sender
    }
    socketio.emit('announcement', {
        'name': sender,
        'message': message,
        'uuid': announcement_uuid
    })

@app.route('/')
def home():
    index = 0
    delete_announcements = []
    for announcement in app.recent_announcements:
        current_time = time.time()
        time_since_announcement = current_time-announcement['time_sent']
        if time_since_announcement >= 3600:
            delete_announcements.append(index)

    for announcement in delete_announcements:
        app.recent_announcements.pop(announcement)
    
    return render_template('home.html', title='Home', announcements=app.recent_announcements, current_time=time.time(), naturaltime=humanize.naturaltime)

@app.route('/make_announcement', methods=['GET', 'POST'])
def make_announcement():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        announcement_client.announce(message, name)
        resp = redirect('/')
        resp.set_cookie('name', name)
        return resp

    cookies = dict(request.cookies)
    if not 'name' in cookies:
        cookies['name'] = ''
    
    return render_template('make_announcement.html', title='Make Announcement', cookies=cookies, presets=announcement_presets)

@app.route('/kiosk')
def kiosk_home():
    index = 0
    delete_announcements = []
    for announcement in app.recent_announcements:
        current_time = time.time()
        time_since_announcement = current_time-announcement['time_sent']
        if time_since_announcement >= 3600:
            delete_announcements.append(index)

    for announcement in delete_announcements:
        app.recent_announcements.pop(announcement)
    
    return render_template('kiosk_home.html', title='Home', announcements=app.recent_announcements, current_time=time.time(), naturaltime=humanize.naturaltime)

@app.route('/kiosk/make_announcement', methods=['GET', 'POST'])
def kiosk_make_announcement():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        announcement_client.announce(message, name)
        resp = redirect('/kiosk')
        resp.set_cookie('name', name)
        return resp

    cookies = dict(request.cookies)
    if not 'name' in cookies:
        cookies['name'] = 'Kiosk'
    
    return render_template('kiosk_make_announcement.html', title='Make Announcement', cookies=cookies, presets=announcement_presets)

@socketio.on('joinRoom')
def joinRoom():
    room = str(uuid.uuid4())
    join_room(room)
    socketio.emit('joinedRoom', room, room=room)

@socketio.on('updateAnnouncementTimes')
def update_announcement_times(data):
    send_data = {}
    current_time = time.time()
    room = data['room']
    data = data['data']
    for announcement in data:
        if not announcement in app.announcement_dict:
            socketio.emit('clearAnnouncements')
            break
        announcement_data = app.announcement_dict[announcement]
        send_data[announcement] = humanize.naturaltime(current_time-announcement_data['time_sent'])
    socketio.emit('announcementTimeUpdate', send_data, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4592)
