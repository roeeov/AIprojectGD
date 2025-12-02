import sys

import pygame
from scripts.player import Player
from scripts.tilemap import tile_map

from scripts.utils import *
from scripts.humanAgent import Agent
from scripts.environment import Environment
from scripts.clouds import Clouds
from scripts.constants import *
from scripts.gameStateManager import game_state_manager
from scripts.mapManager import map_manager
from collections import deque

class Game:
    def __init__(self, display):

        self.display = display
        self.agent = Agent()
        self.env = Environment(self)

        self.noclip = False
        self.checkPoints = deque()
        self.mode = 'normal'
        self.scroll = [0, 0]

        self.openMenu = False

        self.buttons = []

        back_text = Text('', pos = vh(60, 55), size=UIsize(5))
        back_button = Button(back_text, (0 ,255, 0), button_type='menu', image=load_image('UI/buttons/menu.png', scale=(UIsize(4*63/17), UIsize(4))), scale_factor=1.1)
        self.buttons.append(back_button)

        edit_text = Text('', pos = vh(40, 55), size=UIsize(5))
        edit_button = Button(edit_text, (0 ,255, 0), button_type='resume', image=load_image('UI/buttons/resume.png', scale=(UIsize(4*63/17), UIsize(4))), scale_factor=1.1)
        self.buttons.append(edit_button)

        practice_text = Text('', pos = vh(50, 70), size=UIsize(5))
        practice_button = Button(practice_text, (0 ,255, 0), button_type='practice', image=load_image('UI/buttons/practice.png', scale=(UIsize(4*67/17), UIsize(4))), scale_factor=1.1)
        self.buttons.append(practice_button)

        reset_text = Text('', pos = vh(50, 70), size=UIsize(5))
        reset_button = Button(reset_text, (0 ,255, 0), button_type='reset', image=load_image('UI/buttons/playAgain.png', scale=(UIsize(4*63/17), UIsize(4))), scale_factor=1.1)
        self.buttons.append(reset_button)

        pause_text = Text('', pos = vh(4, 4.5), size=UIsize(1.5))
        self.pause_button = Button(pause_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/pause.png', scale=(UIsize(2.5), UIsize(2.5))))

        self.pause_title_text = Text("Pause Menu", vh(50, 30), color=(255, 255, 255))

        self.assets = load_assets()
        for gamemode in GAMEMODES:
            IMG_scale = PLAYERS_IMAGE_SIZE[gamemode]
            base_path = 'player/' + gamemode
            self.assets[base_path + '/run'] = Animation(load_images(base_path + '/run', scale=IMG_scale), img_dur=4)
            self.assets[base_path + '/death'] = Animation(load_images(base_path + '/death', scale=IMG_scale), loop=False)
            if gamemode in GROUND_GAMEMODES:
                self.assets[base_path + '/jump'] = Animation(load_images(base_path + '/jump', scale=IMG_scale))
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self)
        

    def reset(self):    
        tile_map.assets = self.assets
        self.agent.reset()
        self.player.reset()

    def blitMenu(self, mouse_pressed, mouse_released):
        rect_width, rect_height = DISPLAY_SIZE[0]//2, DISPLAY_SIZE[1]//3*2 # size of the black rectangle
        black_rect = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)  # enable per-pixel alpha
        black_rect.fill((0, 0, 0, 128))  # RGBA, 128 = 50% opacity

        # Position the rectangle in the center of the screen
        x = (DISPLAY_SIZE[0] - rect_width) // 2
        y = (DISPLAY_SIZE[1] - rect_height) // 2

        self.display.blit(black_rect, (x, y))

        if self.player.finishLevel:
                
                finish_text = Text("Level Complete!", vh(50, 30), color=(255, 255, 255))
                finish_text.blit(self.display)

                for button in self.buttons:

                    if button.type == 'menu':
                        button.set_offset(vh(-10, -5)[0], vh(-10, -5)[1])
                        button.update(mouse_pressed, mouse_released)
                        if button.is_clicked():
                                self.openMenu = False
                                #self.reset()
                                game_state_manager.returnToPrevState()
                        button.blit(self.display)

                    if button.type == 'reset':
                        button.update(mouse_pressed, mouse_released)
                        if button.is_clicked():
                                self.openMenu = False
                                self.reset()
                        button.blit(self.display)

        else:

            self.pause_title_text.blit(self.display)

            for button in self.buttons:  

                if button.type == 'menu':
                    button.set_offset(0, 0)
                    button.update(mouse_pressed, mouse_released)
                    if button.is_clicked():
                            self.openMenu = False
                            self.reset()
                            game_state_manager.returnToPrevState()
                    button.blit(self.display)

                if button.type == 'resume':
                    button.update(mouse_pressed, mouse_released)
                    if button.is_clicked():
                            self.openMenu = False
                    button.blit(self.display)

                if button.type == 'practice':
                    button.update(mouse_pressed, mouse_released)
                    if button.is_clicked():
                            self.mode = 'practice' if self.mode == 'normal' else 'normal'
                            self.checkPoints.clear()
                            self.openMenu = False
                            self.reset()
                    button.blit(self.display)
    
    def getCheckpoint(self):
        if len(self.checkPoints) > 0:
            return self.checkPoints[0]
        return {'pos': PLAYER_POS.copy(), 'scroll': [0, 0].copy(),
                'velocity': 0, 'gravity': 'down', 'gamemode': 'cube'}

    def run(self):

        if game_state_manager.justSwitched('game'):
            self.mode = 'normal'
            self.checkPoints.clear()
            self.reset()

        mouse_pressed = False
        mouse_released = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_released = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if not self.openMenu:
                        self.reset()
                if event.key == pygame.K_n:
                    if not self.openMenu:
                        self.noclip = not self.noclip
                if event.key == pygame.K_z:
                     if self.mode == 'practice':
                        self.checkPoints.appendleft({'pos': self.player.pos.copy(), 'scroll': self.scroll.copy(),
                            'velocity': self.player.Yvelocity, 'gravity': self.player.gravityDirection, 'gamemode': self.player.gamemode})
                if event.key == pygame.K_x:
                     if self.mode == 'practice' and len(self.checkPoints) > 0:
                          self.checkPoints.popleft()
                if event.key == pygame.K_ESCAPE:
                    if not self.openMenu:
                        self.openMenu = True
                    else:
                        self.openMenu = False
                        self.reset()
                        game_state_manager.returnToPrevState()

        self.display.blit(self.assets['background'], (0, 0))
            
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 3 - self.scroll[0]) / 20 * 60 / FPS
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20 * 60 / FPS
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
        self.clouds.update()
        self.clouds.render(self.display, offset=render_scroll)
            
        tile_map.render(self.display, offset=render_scroll)
     
        self.pause_button.update(mouse_pressed, mouse_released)
        if self.pause_button.is_clicked():
                self.openMenu = True
        self.pause_button.blit(self.display)
        
        if not map_manager.current_map_id.startswith('-'): self.noclip = False
        if not self.openMenu: self.env.move(self.agent.getAction(events))
        self.player.render(self.display, offset=render_scroll)

        if self.mode == 'practice':
            img = self.assets['practiceButtons']
            pos = vh(50, 90)
            centered_pos = (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2)
            self.display.blit(img, centered_pos)

        if (self.player.finishLevel): self.openMenu = True

        if self.openMenu: self.blitMenu(mouse_pressed, mouse_released)

        # check if the player death animation has ended
        if self.player.respawn: self.reset()
