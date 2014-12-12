import time, threading
from flask.ext.socketio import emit
from .. import socketio
import routes
games = {}

def main_loop():
	for i in games:
		games[i].tick()
	threading.Timer(1, main_loop).start()

main_loop()

class Game(object):
	def __init__(self, name, max_players):
		self.players = []
		self.name = name
		self.max_players = max_players
		self.num_players = 0
		self.phase = 'PREP'
		self.saved_discussion_time = 0
		self.start_time = 0
		self.time_left = 0
		self.phase_duration = 0
		self.trial_user = ''

	def check_winner(self):
		#0 mafia town wins
		#0 town mafia wins
		#1 town 1 mafia mafia wins
		count_town = 0
		count_mafia = 0
		for player in self.players:
			if player.is_mafioso(): count_mafia += 1
			elif player.is_citizen(): count_town += 1
		if count_town == 0 or (count_town == 1 and count_mafia == 1): 
			return "Mafia"
		elif count_mafia == 0: 
			return "Town"
		return None

	def assign_roles(self):
		rolesLess15 = ['Mafioso','Doctor','Sheriff','Citizen','Citizen','Mafioso','Citizen','Mafioso','Citizen','Citizen','Mafioso','Citizen','Citizen','Mafioso','Citizen']
		rolesMore15 = ['Mafioso','Doctor','Sheriff','Citizen','Citizen','Mafioso','Citizen','Mafioso','Citizen','Citizen','Mafioso','Mafioso','Citizen','Mafioso','Doctor','Sheriff','Citizen','Citizen','Citizen']
		rolesMore19 = ['Mafioso','Doctor','Sheriff','Citizen','Citizen','Mafioso','Citizen','Mafioso','Citizen','Citizen','Mafioso','Mafioso','Citizen','Mafioso','Doctor','Sheriff','Citizen','Mafioso','Sheriff','Doctor']
		for player in self.players:
			import random
			
			if (self.num_players < 15):
				while True:
					integer = int(random.random()*self.num_players)
					player.role = rolesLess15[integer]
					if(player.role == 'Mafioso'):
						player.playerCanTalkAtNight = True
					rolesLess15[integer]=''
					if player.role != '':
						break
			elif (self.num_players > 19):
				while True:
					integer = int(random.random()*self.num_players)
					player.role = rolesMore19[integer]
					if(player.role == 'Mafioso'):
						player.playerCanTalkAtNight = True
					rolesMore19[integer] = ''
					if player.role != '':
						break
			else:
				while True:
					integer = int(random.random()*self.num_players)
					player.role = rolesMore15[integer]
					if(player.role == 'Mafioso'):
						player.playerCanTalkAtNight = True
					rolesMore15[integer] = ''
					if player.role != '':
						break

	def add_player(self,player):
		self.players.append(player)
		self.num_players += 1

	def remove_player(self, player):
		if player in self.players: 
			self.players.remove(player)
			self.num_players -= 1

	def serialize(self):
		obj = { 'maxPlayers': str(self.max_players), 
				'name': self.name,
				'numPlayers': str(self.num_players),
				'phase': self.phase,
				'timeLeft': self.time_left,
				'trialUser': self.trial_user
				 }
		return obj

	def get_player(self, token):
		for player in self.players:
			if player.token == token:
				return player
		return None

	def get_player_by_username(self, username):
		for player in self.players:
			if player.username == username:
				return player
		return None

	def list_players(self):
		list = []
		for player in self.players:
			list.append(player.serialize())
		return list

	def everyone_ready(self):
		for player in self.players:
			if player.ready == False: return False
		return True

	def start_game(self):
		self.change_phase(120)
		self.phase = 'DISCUSSION'
		self.assign_roles()

	def start_trial(self, token):
		self.saved_discussion_time = self.time_left
		self.change_phase(60)
		self.phase = 'TRIAL'
		self.trial_user = routes.username(token)
		for player in self.players:
			player.voted_for = ''
			player.votes = 0

	def continue_discussion(self):
		self.change_phase(self.saved_discussion_time)
		self.phase = 'DISCUSSION'

	def change_phase(self, duration):
		self.start_time = time.time()
		self.time_left = duration
		self.phase_duration = duration

	def tick(self):
		if self.phase != 'PREP':
			self.time_left = self.phase_duration - (time.time() - self.start_time)
			if self.time_left == 0:
				if self.phase == 'DISCUSSION':
					self.phase = 'NIGHT'
	def clear_votes(self):
		for i in self.players:
			i.votes = 0
			i.voted_for = ''

class Player(object):
	def __init__(self, token):
		self.role = 'Citizen'
		self.is_alive = True
		self.votes = 0
		self.voted_for = ''
		self.ready = False
		self.token = token
		self.username = routes.username(token)

	def serialize(self):
		obj = {'role':self.role,
				'username':self.username,
				'isAlive':self.is_alive,
				'votes':self.votes,
				'ready':str(self.ready),
				'votedFor':self.voted_for
				}
		return obj

	def can_talk_at_night(self):
		return self.role == 'Mafioso'

	def is_mafioso(self):
		return self.role == 'Mafioso'

	def is_citizen(self):
		return self.role == 'Doctor' or self.role == 'Citizen'


def get_game(name):
	return games[name]

def add_game(game):
	games[game.name] = game

add_game(Game("Game 1", 10))
add_game(Game("Mkdir dat shit", 4))