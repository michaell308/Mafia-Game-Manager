

class Game(object):
	def __init__(self, name, max_players):
		self.players = []
		self.name = name
		self.max_players = max_players
		pass
	def serialize(self):
		obj = { 'maxPlayers': str(self.players), 'name': self.name }
		return obj


class Player(object):
	def __init__(self):
		self.role = 'Citizen'
		self.is_alive = True
		self.name = 'Derp'
		self.votes = 0

games = [Game("test1", 10), Game("testicles", 2)]