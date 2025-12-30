import pygame
import math
from scripts.tilemap import tile_map
from scripts.constants import *

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
    
    def update_visuls(self):
        self.game.display.blit(self.game.assets['background'], (0, 0))
            
        self.game.scroll[0] += (self.game.player.rect().centerx - self.game.display.get_width() / 3 - self.game.scroll[0]) / 20 * 60 / FPS
        self.game.scroll[1] += (self.game.player.rect().centery - self.game.display.get_height() / 2 - self.game.scroll[1]) / 20 * 60 / FPS
        render_scroll = (int(self.game.scroll[0]), int(self.game.scroll[1]))
            
        self.game.clouds.update()
        self.game.clouds.render(self.game.display, offset=render_scroll)
            
        tile_map.render(self.game.display, offset=render_scroll)
        
        self.game.pause_button.blit(self.game.display)
            
        self.game.player.render(self.game.display, offset=render_scroll)

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
        player = self.game.player
        state_info = tile_map.getState(player)
        
        if DRAW_PLAYER_STATE:
            player_pos = player.pos.copy()
            for (distance, type), angle_deg in zip(state_info, STATE_ANGLES):
                angle_rad = math.radians(float(angle_deg))
                dx = math.cos(angle_rad) * distance * tile_map.tile_size
                dy = math.sin(angle_rad) * distance * tile_map.tile_size
                rect_pos = (player_pos[0] + dx, player_pos[1] + dy)

                offset = (int(self.game.scroll[0]), int(self.game.scroll[1]))

                colrect = player.rect(rect_pos)
                colrect.center=(rect_pos[0] + player.size[0] // 2 - offset[0],
                                                        rect_pos[1] + player.size[1] // 2 - offset[1])
                pygame.draw.rect(self.game.display, (0, 0, 255), colrect)
            
                colrect = player.hitbox_rect(rect_pos)
                colrect.center=(rect_pos[0] + player.size[0] // 2 - offset[0],
                                                        rect_pos[1] + player.size[1] // 2 - offset[1])
                pygame.draw.rect(self.game.display, (0, 255, 0), colrect)

        return state_info
    

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