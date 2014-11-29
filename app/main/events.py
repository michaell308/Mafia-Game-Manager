from flask import session
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
from game import *
from flask import jsonify

messages = []
name = 'Derp'
rooms = ['default']
lobby_room = 'lobby string. needs to be long so no conflict with user created rooms :3'

@socketio.on('create game', namespace='/lobby')
def create_game(data):
    """Sent by clients when they attempt to create a game in the lobby. 
    A game object is passed in with relevant properties such as name, max. players."""

    room = session.get('room')

    errors = [];

    #error checking
    if len(data['name']) < 1: errors.append("Name too short")
    if len(data['maxPlayers']) < 1 or not str(data['maxPlayers']).isdigit() or int(data['maxPlayers']) > 99: errors.append("Invalid max. number of players")
    if len(games) >= 10: errors.append("Lobby is full")
    for g in games: 
        if g.name == data['name']: errors.append("Name already taken")

    
    emit('game creation errors', errors)
    if len(errors) > 0: return

    game = Game(data['name'], int(data['maxPlayers']))

    games.append(game)
    emit('clear list', room=room)
    for i in games:
        emit('show game', i.serialize(), room=room)

@socketio.on('joined', namespace='/lobby')
def joined_lobby(data):
    room = lobby_room
    join_room(room)
    session['room'] = room
    emit('clear list', room=room)
    for i in games:
        emit('show game', i.serialize(), room=room)



@socketio.on('joined', namespace='/chat')
def joined(data):
    """Sent by clients when they enter a room. A status message is broadcast to all people in the room."""
    join_room(rooms[0])
    emit('status', {'message': name + ' has joined the room.'}, session.get('room'))

@socketio.on('text', namespace='/chat')
def text(data):
    """Sent by a client when the user entered a new message. The message is sent to all people in the room."""
    room = session.get('room')
    message_data = {'username': name, 'message':data['message']}
    messages.append(message_data)
    emit('text', message_data , room=room)

@socketio.on('left')
def left(data):
    """Sent by clients when they leave a room. A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'message': name + ' has left the room.'}, room=room)
