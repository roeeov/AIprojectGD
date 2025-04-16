import sys

import pygame
from scripts.utils import *
from scripts.gameStateManager import game_state_manager
from scripts.mapManager import map_manager
from scripts.constants import *

class LevelSelect:
    
    def __init__(self, display):

        self.display = display
        self.scroll = 0
        self.levelInfoIMG = load_image(path='UI/buttons/levelInfo.png', scale=(UIsize(75), UIsize(6)))
        self.background = load_image('UI/backgrounds/menuBG.png', scale=DISPLAY_SIZE)
        self.reloadButtons()

    def reloadButtons(self):
        self.buttons = []

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        reload_text = Text('reload', pos = (vh(90, -1)[0], vh(-1, 90)[1]), size=UIsize(3))
        reload_button = Button(reload_text, (0 ,255, 0), button_type='reload')
        self.buttons.append(reload_button)

        online_map_dict = map_manager.getOnlineMapsDict()
        for idx, map in enumerate(online_map_dict.values()):
            map_text = map['info']['name'] + ' '*5 + map['info']['creator'] + ' '*5 + map['info']['difficulty']
            map_text = Text(map_text, pos = (vh(50, -1)[0], (idx+1)*vh(-1, 14)[1] - vh(-1, 3)[1]), size=UIsize(4), color=(40, 40, 40))
            map_button = Button(map_text, (0 ,255, 0), "map_idx: " + map['info']['id'], scale_factor=1.05, image=self.levelInfoIMG)
            self.buttons.append(map_button)

        self.max_scroll = -vh(-1, 14)[1] * len(online_map_dict)
        
    def run(self):
        
        self.display.blit(self.background, (0, 0))

        mouse_pressed = False
        mouse_released = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state_manager.returnToPrevState()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_released = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                if self.scroll < 0:
                    self.scroll += LEVEL_SELECTOR_SCROLL
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                self.scroll -= LEVEL_SELECTOR_SCROLL
                if self.scroll < self.max_scroll:
                    self.scroll = self.max_scroll

        for button in self.buttons:
            if button.type not in {'prev', 'reload'}: button.set_offset(0, self.scroll)
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'prev':
                    game_state_manager.returnToPrevState()
                elif button.type == 'reload':
                    map_manager.update_map_dict()
                    self.reloadButtons()
                else:
                    map_id = button.type.split()[-1]
                    map_manager.setMap(map_id)
                    game_state_manager.setState('level_page')

            button.blit(self.display)

class LevelPage:

    def __init__(self, display, level_select):
        self.display = display
        self.level_select = level_select
        self.buttons = []

        play_text = Text('play', pos = vh(60, 60), size=UIsize(6))
        play_button = Button(play_text, (0 ,255, 0), button_type='play')
        self.buttons.append(play_button)

        edit_text = Text('edit', pos = vh(40, 60), size=UIsize(6))
        edit_button = Button(edit_text, (0 ,255, 0), button_type='edit')
        self.buttons.append(edit_button)

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        self.diff_faces = {diff: load_image(f'UI/difficulity/{diff}.png', scale=(UIsize(3), UIsize(3))) for diff in DIFFICULTIES}

    def run(self):

        self.display.fill((245, 137, 49))

        map_info = map_manager.getMapInfo(map_manager.current_map_id)

        map_name = map_info["name"]
        map_name_text = Text(map_name, pos = vh(50, 25), size=UIsize(5), color=(255, 255, 255))
        map_name_text.blit(display=self.display)

        map_creator = map_info["creator"]
        map_creator_text = Text("creator: " + map_creator, pos = vh(35, 40), size=UIsize(3), color=(255, 255, 255))
        map_creator_text.blit(display=self.display)

        map_difficulty = map_info["difficulty"]
        map_difficulty_text = Text("difficulty: ", pos =vh(65, 40), size=UIsize(3), color=(255, 255, 255))
        map_difficulty_text.blit(display=self.display)
        # blit difficulity face
        diff_faces_rect = self.diff_faces[map_difficulty].get_rect(center=vh(74, 40))
        self.display.blit(self.diff_faces[map_difficulty], diff_faces_rect)

        mouse_pressed = False
        mouse_released = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.level_select.reloadButtons()
                    game_state_manager.returnToPrevState()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_released = True

        for button in self.buttons:
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'prev':
                    self.level_select.reloadButtons()
                    game_state_manager.returnToPrevState()
                elif button.type == 'play':
                    map_manager.loadMap()
                    game_state_manager.setState('game')
                elif button.type == 'edit':
                    map_manager.loadMap()
                    game_state_manager.setState('edit')
            button.blit(self.display)

        

