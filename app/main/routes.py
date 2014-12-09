from flask import session, render_template
from . import main
from game import *
import uuid
import time

guest_num = 1
connected = {}
usernames = {}



def username(token):
	return usernames[token]

@main.route('/', methods=['GET', 'POST'])
def lobby():
	"""
	Default page is lobby for now
	"""
	global guest_num


	#if 'token' in session and session['token'] in connected and connected[session['token']]: return "You may already be connected in another tab. If you aren't, please wait 10 seconds and try again."

	if not 'token' in session: 
		session['token'] = uuid.uuid4()
	if not session['token'] in usernames:
		usernames[session['token']] = 'Player' + str(guest_num)
		guest_num += 1

	connect(session['token'])

	return render_template('lobby.html', name=username(session['token']))

@main.route('/game/<name>', methods=['GET', 'POST'])
def game(name):
	"""
	Game and chat page
	"""
	if not 'token' in session or not session['token'] in usernames: return "Please enter through the lobby!"
	if not name in games:return "This room does not exist, sorry!"
	if games[name].num_players >= games[name].max_players: return "Room full, sorry!"
	if not games[name].get_player(session['token']) and games[name].phase != 'PREP': return "The game is already in progress, sorry!"
	return render_template('game.html', name=name)

@main.route('/login', methods=['GET','POST'])
def login():
	form = Login()

def connect(token):
	connected[token] = True

def disconnect(token):
	connected[token] = False
