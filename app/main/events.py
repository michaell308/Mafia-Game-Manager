from flask import session
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio


messages = []


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'message': session.get('name') + ' has joined the room.'}, room=room)


@socketio.on('connect', namespace = '/chat')
def client_connect():
    pass

@socketio.on('text', namespace='/chat')
def left(data):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    message_data = {'username': session.get('name'), 'message':data['message']}
    messages.append(message_data)
    emit('text', message_data , room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'message': session.get('name') + ' has left the room.'}, room=room)

