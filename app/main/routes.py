from flask import session, render_template
from . import main
from game import *
import uuid
import time

guest_num = 1
connected = {}

@main.route('/', methods=['GET', 'POST'])
def lobby():
	"""
	Default page is lobby for now
	"""
	global guest_num


	#if 'token' in session and session['token'] in connected and connected[session['token']]: return "You may already be connected in another tab. If you aren't, please wait 10 seconds and try again."

	if not 'token' in session or not 'username' in session: 
		session['token'] = uuid.uuid4()
		session['username'] = "player" + str(guest_num)
		guest_num += 1

	connect(session['token'])
	print time.time()

	return render_template('lobby.html', name=session['username'])

@main.route('/game/<name>', methods=['GET', 'POST'])
def game(name):
	"""
	Game and chat page
	"""
	return render_template('chatsystem.html', name=name)

@main.route('/login', methods=['GET','POST'])
def login():
	form = Login()

def connect(token):
	connected[token] = True

def disconnect(token):
	connected[token] = False
