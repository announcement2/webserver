from flask import Flask, jsonify, request
import requests
import threading
import os

app = Flask(__name__)
app.announcement_callback_list = []

class AnnouncementsError(Exception):
    pass

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/announcement', methods=['POST'])
def announcement():
    for func in app.announcement_callback_list:
        func(request.form['message'], request.form['from'])
    return jsonify({
        'code': 200,
        'message': 'OK'
    })

def announcement_callback(func):
    app.announcement_callback_list.append(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

def announce(message, name):
    try:
        r = requests.post('{}/make_announcement'.format(app.server_url), data={
            'name': name,
            'name_id': app.name,
            'message': message
        })
    except:
        raise AnnouncementsError('Server did not respond. Please change your server URL, or check the server logs.')
    else:
        if not r.status_code == 200:
            if r.status_code == 400:
                raise AnnouncementsError('Server responded with 400: {}'.format(r.json()['message']))
            elif r.status_code == 404:
                raise AnnouncementsError('Server responded with 404, this is likely an issue with server client version mismatch.')
            elif r.status_code == 500:
                raise AnnouncementsError('Server responded with 500, this is a problem with the server, check the server logs.')
            else:
                raise AnnouncementsError('Server responded with {}'.format(r.status_code))

def run_clientserver_nothread():
    app.run(host='0.0.0.0', port=4598)

def run_client(name):
    app.name = name
    if not os.path.exists('server_url.conf'):
        open('server_url.conf', 'x').close()
        raise AnnouncementsError('server_url.conf does not exist. Please add the server URL to the file.')
    else:
        server_url_f = open('server_url.conf', 'r')
        server_url = server_url_f.read().replace('\n', '')
        if server_url.endswith('/'):
            server_url = server_url[:-1]
        app.server_url = server_url
    threading.Thread(target=run_clientserver_nothread).start()
    try:
        r = requests.post(app.server_url+'/add_client', data={
            'server_scheme': 'http',
            'server_port': 4598,
            'name': app.name
        })
    except:
        raise AnnouncementsError('Server did not respond. Please change your server URL, or check the server logs.')
    else:
        if not r.status_code == 200:
            if r.status_code == 400:
                raise AnnouncementsError('Server responded with 400: {}'.format(r.json()['message']))
            elif r.status_code == 404:
                raise AnnouncementsError('Server responded with 404, this is likely an issue with server client version mismatch.')
            elif r.status_code == 500:
                raise AnnouncementsError('Server responded with 500, this is a problem with the server, check the server logs.')
            else:
                raise AnnouncementsError('Server responded with {}'.format(r.status_code))
