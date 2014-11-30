

class Game(object):
	def __init__(self, name, max_players):
		self.players = []
		self.name = name
		self.max_players = max_players
		self.num_players = 0
		pass

	def addPlayer(self,player):
		self.players.append(player)
		self.num_players += 1

	def serialize(self):
		obj = { 'maxPlayers': str(self.max_players), 
				'name': self.name,
				'num_players': str(self.num_players) }
		return obj



class Player(object):
	def __init__(self):
		self.role = 'Citizen'
		self.is_alive = True
		self.name = 'Derp' 
		self.votes = 0

games = {}

def addGame(game):
	games[game.name] = game

addGame(Game("Game 1", 10))
addGame(Game("Other game", 2))