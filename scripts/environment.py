import pygame
from scripts.tilemap import tile_map

class Environment:
    def __init__(self, game):
        self.game = game
        self.done = False
        self.score = 0

    def reset(self):
        self.game.reset()  # Make sure Game has a reset() method
        self.done = False
        self.score = 0
        return self.state()

    def step(self, action):
        self.move(action)
        self.game.update()  # Main game update logic
        reward = self.compute_reward()
        self.done = self.check_done()
        return self.state(), reward, self.done, {}

    def move(self, action):
        boolAction = bool(action)
        self.game.player.update(boolAction)

    def state(self):
        player_pos = self.game.player.pos.copy()
        return tile_map.getState(self.game.player)

    def compute_reward(self):
        # Example reward logic
        if self.game.player.dead:
            return -1
        elif getattr(self.game.player, "reached_goal", False):
            return 10
        else:
            return 0

    def check_done(self):
        return self.game.player.dead or getattr(self.game.player, "reached_goal", False)

    def render(self, display):
        self.game.render(display)