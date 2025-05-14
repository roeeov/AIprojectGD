import pygame
from scripts.tilemap import tile_map

class Environment:

    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def move(self, action):
        boolAction = bool(action)
        self.game.player.update(boolAction)

    def state(self):
        player_pos = self.game.player.pos.copy()
        return tile_map.getState(player_pos)