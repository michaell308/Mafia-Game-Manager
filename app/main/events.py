from flask import session, make_response
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
from game import *
from flask import jsonify
from run import *
import json
import uuid
from routes import *

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

@socketio.on('disconnect', namespace='/lobby')
def left_lobby():
    """Sent by clients when they leave a room. A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    disconnect(session['token'])
    update_session()
    

@socketio.on('joined', namespace='/chat')
def joined(data):
    """Sent by clients when they enter a room. A status message is broadcast to all people in the room."""
    print "player join detected"
    game = games[data['name']]
    if game.num_players > game.max_players: return

    if not game.get_player(session.get('token')):
        emit('join game', {'name': data['name']})
        emit('status', {'message': username(session['token']) + ' has joined the room.'}, room=session.get('room'))
        game.add_player(Player(session.get('token')))

    join_room(data['name'])
    session['room'] = data['name']
    update_session()
    
    update_game(session.get('room'))
    update_lobby_list()


@socketio.on('text', namespace='/chat')
def text(data):
    """Sent by a client when the user entered a new message. The message is sent to all people in the room."""
    room = session.get('room')
    if not games[room].get_player(session['token']) or games[room].get_player(session['token']).role != 'Mafioso' and games[room].phase == 'NIGHT': return
    message_data = {'username': username(session['token']) , 'message':data['message']}
    emit('text', message_data , room=room)

@socketio.on('leave', namespace='/chat')
def left_chat():
    """Sent by clients when they leave a room. A status message is broadcast to all people in the room."""
    print "player disconnect just detected"
    room = session.get('room')
    game = games[room]
    
    for player in game.players:
        if player.token == session['token']:
            game.remove_player(player)
    update_lobby_list()
    


    leave_room(room)
    update_session()
    emit('status', {'message': username(session['token'])  + ' has left the room.'}, room=room)
    
    update_game(session['room'])
    disconnect(session['token'])
    update_lobby_list()

@socketio.on('toggle ready', namespace='/chat')
def player_ready():
    game = games[session['room']]
    if (game.phase == 'PREP'):
        player = game.get_player(session['token'])
        player.ready = not player.ready
        if game.everyone_ready() and len(game.players) >= 4:
            game.start_game()
        update_game(session['room'])

@socketio.on('update game', namespace='/chat')
def update_game():
    game = games[session['room']]
    emit('game data', game.serialize())

@socketio.on('toggle vote', namespace='/chat')
def toggle_vote(data):
    name = data['name']
    game = games[session['room']]
    player = game.get_player(session['token'])
    target_player = game.get_player_by_username(name)
    if player == None or target_player == None: return
    if player.voted_for == name:
        player.voted_for = ''
        target_player.votes -= 1
    else:
        player.voted_for = name
        target_player.votes += 1
    total_voting_power = len(game.players)
    if target_player.votes > total_voting_power/2:
        if game.phase == 'DISCUSSION':
            game.start_trial(target_player.token)
        elif game.phase == 'TRIAL':
            game.players.remove(target_player)
            winner = game.check_winner()
            emit('status', {'message': target_player.username + ' has been lynched.'}, room=session.get('room'))
            emit('status', {'message': target_player.username + ' was '+target_player.role}, room=session.get('room'))
            if not winner:
               
                game.continue_discussion()
            elif winner == "Mafia":
                emit('status', {'message': 'Mafia wins!'}, room=session.get('room'))
            elif winner == "Town":
                emit('status', {'message': 'Town wins!'}, room=session.get('room'))
                
            game.clear_votes()
            

    update_game(session['room'])

def update_session():
    session.modified = True
    app.save_session(session,make_response("42.14159 horse sized ducks"))

def update_lobby_list():
    emit('list games', json.dumps([games[i].serialize() for i in games]), room = lobby_room, namespace='/lobby')

def update_game(room):
    emit('update game', json.dumps({'game':games[room].serialize(),'players':games[room].list_players(),'username':username(session.get('token'))}), room=room)

