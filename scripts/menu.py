import sys

import pygame
from scripts.utils import *
from scripts.gameStateManager import game_state_manager
from scripts.constants import DISPLAY_SIZE

class Menu:
    
    def __init__(self, display):

        self.display = display
        self.background = load_image('UI/backgrounds/menuBG.png', scale=DISPLAY_SIZE)

        select_level_text = Text('', pos = vh(50, 45), size=UIsize(5))
        select_level_button = Button(select_level_text, (59, 189, 30), 'level_select', image=load_image('UI/buttons/levelSelect.png', scale=(UIsize(64/3), UIsize(17/3))))

        create_map_text = Text('', pos = vh(50, 60), size=UIsize(5))
        create_map_button = Button(create_map_text, (29, 53, 207), 'create_map', image=load_image('UI/buttons/createMap.png', scale=(UIsize(64/3), UIsize(17/3))))

        quit_text = Text('', pos = vh(50, 75), size=UIsize(5))
        quit_button = Button(quit_text, (194, 25, 25), 'quit', image=load_image('UI/buttons/quit.png', scale=(UIsize(33/3), UIsize(17/3))))

        self.buttons = [create_map_button, select_level_button, quit_button]

        self.title_text = Text("GeoRush", vh(50, 20), color=(209, 154, 15), size=UIsize(10))

    def run(self):

        self.display.blit(self.background, (0, 0))

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

        self.title_text.blit(self.display)

        for button in self.buttons:
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'create_map':
                    game_state_manager.setState('my_levels')
                if button.type == 'level_select':
                    game_state_manager.setState('level_select')
                if button.type == 'quit':
                    pygame.quit()
                    sys.exit()
            button.blit(self.display)
