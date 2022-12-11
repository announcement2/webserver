from flask import Flask, render_template
import announcement_client
import time
import threading
import humanize

app = Flask(__name__)
announcement_client.run_client('webserver')
app.recent_announcements = []

@announcement_client.announcement_callback
def handle_announcement(message, sender):
    current_time = time.time()
    app.recent_announcements.append({
        'time_sent': current_time,
        'message': message,
        'from': sender
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4592)
