

class Game(object):
	def __init__(self, name, max_players):
		self.players = []
		self.name = name
		self.max_players = max_players
		self.num_players = 0
		self.phase = 'PREP'
		self.mainTimer = -1

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
				 }
		return obj

	def get_player(self, username):
		for player in self.players:
			if player.username == username:
				return player

	def list_players(self):
		list = []
		for player in self.players:
			list.append(player.serialize())
		return list

	def everyone_ready(self):
		for player in self.players:
			if player.ready == False: return False
		return True

class Player(object):
	def __init__(self, token, username):
		self.role = 'Citizen'
		self.is_alive = True
		self.votes = 0
		self.voted_for = ''
		self.ready = False
		self.token = token
		self.username = username

	def serialize(self):
		obj = {'role':self.role,
				'username':self.username,
				'isAlive':self.is_alive,
				'votes':self.votes,
				'ready':str(self.ready),
				'votedFor':self.voted_for
				}
		return obj
games = {}

def get_game(name):
	return games[name]

def add_game(game):
	games[game.name] = game

add_game(Game("Game 1", 10))
add_game(Game("Other game", 2))


games["Game 1"].num_players