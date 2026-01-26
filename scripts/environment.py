import pygame
import math
from scripts.tilemap import tile_map
from scripts.constants import *
from scripts.gameStateManager import game_state_manager

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

    def update_visuals(self, state_info):
        visuals_mode = game_state_manager.getGameSettings('visual')
        visuals_mode_index = VISUALS.index(visuals_mode)
        
        self.game.display.fill((0, 0, 0))
        
        if visuals_mode_index < 2:
            self.game.scroll[0] += (self.game.player.rect().centerx - self.game.display.get_width() / 3 - self.game.scroll[0]) / 20 * 60 / FPS
            self.game.scroll[1] += (self.game.player.rect().centery - self.game.display.get_height() / 2 - self.game.scroll[1]) / 20 * 60 / FPS
            render_scroll = (int(self.game.scroll[0]), int(self.game.scroll[1]))
            
            if visuals_mode_index < 1:
                self.game.display.blit(self.game.assets['background'], (0, 0))
                self.game.clouds.update()
                self.game.clouds.render(self.game.display, offset=render_scroll)
                
            tile_map.render(self.game.display, offset=render_scroll)
            self.game.player.render(self.game.display, offset=render_scroll)
            
            if visuals_mode_index < 1: self.blit_state(state_info)
        
        self.game.pause_button.blit(self.game.display)

    def move(self, action, state, isTraining):
        boolAction = bool(action)
        self.game.player.update(boolAction)
        next_state, reward = None, None
        if isTraining:
            next_state = self.state()
            reward = self.calculate_reward(action, state)
        return next_state, reward

    def calculate_reward(self, action, state): 
        if self.game.player.finishLevel:
            return 1000
        if self.game.player.respawn:
            return -200

        reward = 0.4 # reward for surviving
        a, b, c, d, flag_scalar = 0.6, 0, 5, 1.5, 2
        safe_distance = 0.5 # safe distance until penalty starts

        best_dir_dist, best_dir_angle = -1, -1 # (distance, angle)
        min_danger_distance = MAX_DISTANCE + STEP
        flag_proximity_bonus = 0

        distances , types = state[0::2], state[1::2]
        for (distance, type), deg in zip(zip(distances, types), STATE_ANGLES):
            
            if type == TILE_TYPE_MAP["finish"]:
                
                flag_proximity_bonus = max(flag_proximity_bonus, (MAX_DISTANCE + STEP - distance) * flag_scalar)

                virtual_dist = MAX_DISTANCE * 2 
                if abs(deg) == 45 and virtual_dist > best_dir_dist:
                    best_dir_dist = virtual_dist
                    best_dir_angle = deg

            else:
                min_danger_distance = min(min_danger_distance, distance)
                
                if distance < safe_distance:
                    reward -= b * ((safe_distance - distance)**2)
                
                if abs(deg) == 45 and distance > best_dir_dist:
                    best_dir_dist = distance
                    best_dir_angle = deg
        
        dist_up, dist_down = distances[0], distances[-1]
        total_vertical_gap = dist_up + dist_down
        if total_vertical_gap > 0:
            off_center = abs(dist_up - dist_down) / total_vertical_gap
            reward += (1.0 - off_center) * d

        reward += c * ((best_dir_angle > 0) == action)
        reward += min_danger_distance * a
        reward += flag_proximity_bonus

        return reward

    def state(self):
        player = self.game.player
        state_info = tile_map.getState(player)
        return state_info;
    
    def blit_state(self, state_info):
        if DRAW_PLAYER_STATE and state_info is not None:
            player = self.game.player
            player_pos = player.pos.copy()
            for distance, angle_deg in zip(state_info[0::2], STATE_ANGLES):
                angle_rad = math.radians(float(angle_deg))
                dx = math.cos(angle_rad) * distance * tile_map.tile_size
                dy = math.sin(angle_rad) * distance * tile_map.tile_size
                rect_pos = (player_pos[0] + dx, player_pos[1] - dy)

                offset = (int(self.game.scroll[0]), int(self.game.scroll[1]))

                colrect = player.rect(rect_pos)
                colrect.center=(rect_pos[0] + player.size[0] // 2 - offset[0],
                                                        rect_pos[1] + player.size[1] // 2 - offset[1])
                pygame.draw.rect(self.game.display, (0, 0, 255), colrect) 
            
                colrect = player.hitbox_rect(rect_pos)
                colrect.center=(rect_pos[0] + player.size[0] // 2 - offset[0],
                                                        rect_pos[1] + player.size[1] // 2 - offset[1])
                pygame.draw.rect(self.game.display, (0, 255, 0), colrect)

    def check_done(self):
        return self.game.player.finishLevel or self.game.player.respawn

    def render(self, display):
        self.game.render(display)