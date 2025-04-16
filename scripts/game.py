import sys

import pygame

from scripts.utils import *
from scripts.player import Player
from scripts.tilemap import tile_map
from scripts.clouds import Clouds
from scripts.constants import *
from scripts.gameStateManager import game_state_manager
from scripts.mapManager import map_manager

class Game:
    def __init__(self, display):

        self.display = display
        
        self.input = {'w': False, 'space': False, 'up_arrow': False, 'mouse': False}
        self.up = False
        self.noclip = False

        self.openMenu = False
        self.buttons = []

        back_text = Text('menu', pos = vh(60, 55), size=UIsize(5))
        back_button = Button(back_text, (0 ,255, 0), button_type='menu')
        self.buttons.append(back_button)

        edit_text = Text('resume', pos = vh(40, 55), size=UIsize(5))
        edit_button = Button(edit_text, (0 ,255, 0), button_type='resume')
        self.buttons.append(edit_button)

        reset_text = Text('play again', pos = vh(50, 70), size=UIsize(5))
        reset_button = Button(reset_text, (0 ,255, 0), button_type='reset')
        self.buttons.append(reset_button)

        pause_text = Text('pause', pos = vh(4, 4.5), size=UIsize(1.5))
        self.pause_button = Button(pause_text, (0 ,255, 0), button_type='prev')

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
        
        self.scroll = [0, 0]

    def reset(self):    
        # Then set assets
        tile_map.assets = self.assets
        
        # Reset scroll and up state
        self.scroll = [0, 0]
        self.up = False
        
        # Reset player after tilemap is cleared
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
                                self.reset()
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
                



    def run(self):

        mouse_pressed = False
        mouse_released = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_released = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.input['up_arrow'] = True
                if event.key == pygame.K_w:
                    self.input['w'] = True
                if event.key == pygame.K_SPACE:
                    self.input['space'] = True  
                if event.key == pygame.K_r:
                    if not self.openMenu:
                        self.reset()
                if event.key == pygame.K_n:
                    if not self.openMenu:
                        self.noclip = not self.noclip
                if event.key == pygame.K_ESCAPE:
                    if not self.openMenu:
                        self.openMenu = True
                    else:
                        self.openMenu = False
                        self.reset()
                        game_state_manager.returnToPrevState()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.input['up_arrow'] = False
                if event.key == pygame.K_w:
                    self.input['w'] = False
                if event.key == pygame.K_SPACE:
                    self.input['space'] = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.input['mouse'] = True     
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.input['mouse'] = False     

        self.up = self.input['space'] or self.input['w'] or self.input['up_arrow'] or self.input['mouse']

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
        if not self.openMenu: self.player.update(tile_map, self.up)
        self.player.render(self.display, offset=render_scroll)
        if (self.player.finishLevel): self.openMenu = True


        if self.openMenu: self.blitMenu(mouse_pressed, mouse_released)

        # check if the player death animation has ended
        if self.player.respawn: self.reset()
