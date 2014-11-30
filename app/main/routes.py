from flask import session, render_template
from . import main
from game import *

@main.route('/', methods=['GET', 'POST'])
def lobby():
	"""
	Default page is chat for now
	"""
	return render_template('lobby.html')
	

@main.route('/game/<name>', methods=['GET', 'POST'])
def game(name):
	"""
	Game and chat page
	"""
	return render_template('chatsystem.html', name=name)