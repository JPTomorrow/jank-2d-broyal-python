from player import Player
class GameState:
    def __init__(self):
        self.players = []
        self.projectiles = []
        self.buildings = []
        self.human_player = Player