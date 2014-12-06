from flask import session, make_response
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
from game import *
from flask import jsonify
from run import *
import json
import uuid
from routes import *

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
    #for g in games: 
    #    if data['name'] == g.name: 
    #        errors.append("Name already taken")

    
    emit('game creation errors', errors)
    if len(errors) > 0: return

    game = Game(data['name'], int(data['maxPlayers']))

    add_game(game)
    update_lobby_list()
    

@socketio.on('joined', namespace='/lobby')
def joined_lobby(data):
    """When a client just joins the lobby"""
    join_room(lobby_room)
    session['room'] = lobby_room
    update_session()
    update_lobby_list()

@socketio.on('join game', namespace='/lobby')
def join_game(data):
    if data['name'] in games:
        game = games[data['name']]
        
        if game.num_players > game.max_players: return
        for i in game.players:
            if session['token'] == i.token:return
        
        game.add_player(Player(session.get('token'), session.get('username')))
        emit('join game', {'name': data['name']})
        join_room(data['name'])
        session['room'] = data['name']
        update_session()
        update_lobby_list()
        


@socketio.on('disconnect', namespace='/lobby')
def left():
    """Sent by clients when they leave a room. A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    disconnect(session['token'])
    update_session()
    

@socketio.on('joined', namespace='/chat')
def joined(data):
    """Sent by clients when they enter a room. A status message is broadcast to all people in the room."""
    join_room(data['name'])
    session['room'] = data['name']
    update_session()
    emit('status', {'message': session['username'] + ' has joined the room.'}, room=session.get('room'))
    update_player_list(games[session.get('room')], session.get('room'))


@socketio.on('text', namespace='/chat')
def text(data):
    """Sent by a client when the user entered a new message. The message is sent to all people in the room."""
    room = session.get('room')
    message_data = {'username': session.get('username'), 'message':data['message']}
    messages.append(message_data)
    emit('text', message_data , room=room)

@socketio.on('disconnect', namespace='/chat')
def left():
    """Sent by clients when they leave a room. A status message is broadcast to all people in the room."""
    print "player disconnect just detected"
    game = games[room]
    room = session.get('room')
    for player in game.players:
        if player.token == session['token']:
            game.remove_player(player)

    update_lobby_list()
    update_player_list(game, session['room'])

    leave_room(room)
    update_session()
    emit('status', {'message': session['username'] + ' has left the room.'}, room=room)
    
    disconnect(session['token'])

@socketio.on('toggle ready', namespace='/chat')
def player_ready():
    game = games[session['room']]
    player = game.get_player(session['username'])
    player.ready = not player.ready
    update_player_list(game, session['room'])
    if game.everyone_ready(): print "ready!"

def update_session():
    session.modified = True
    app.save_session(session,make_response("20.14159 horse sized ducks"))

def update_lobby_list():
    emit('list games', json.dumps([games[i].serialize() for i in games]), room = lobby_room)

def update_player_list(game, room):
    emit('list players', json.dumps(game.list_players()), room=room)