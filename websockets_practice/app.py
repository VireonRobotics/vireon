#!/usr/bin/python3

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
# from datetime import datetime
import eventlet

eventlet.monkey_patch()


app = Flask(__name__)
# app.config['SECRET_KEY'] = "Dennisco"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

users = {}

app.route("/")
def homepage():
    return render_template("index.html")
    # return HTMLResponse(open)

@socketio.on("connect")
def handle_connect(auth):
    username = request.sid[:8]
    users[request.sid] = username
    print(f"Client connected {username}: ({request.sid})")
    emit('status', {'msg': f'{username} has entered the chat.'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = users.get(request.sid, "Unknown")
    users.pop(request.sid, None)
    print(f"Client disconnected: {username}")
    emit('status', {'msg': f'{username} has left the chat.'}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = users.get(request.sid, "Anonymous")
    message = data.get('msg', '').strip()

    if message:
        emit('message', {
            'username': username,
            'msg': message,
            # 'timestamp': datetime.now().strftime('%H:%M')
            'timestamp': eventlet.import_patched('time').strftime('%H:%M')
        }, broadcast=True)

@socketio.on('private_message')
def handle_private_message(data):
    recipient_sid = data['to']
    message = data['msg']
    username = users.get(request.sid, "Anonymous")

    emit('private_message', {
        'from': username,
        'msg': message
    }, room=recipient_sid)

    emit('private_message', {
        'from': username,
        'to': 'you',
        'msg': message
    })


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
