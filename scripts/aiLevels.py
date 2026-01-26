import sys

import pygame
from scripts.utils import *
from scripts.gameStateManager import game_state_manager
from scripts.mapManager import map_manager
from scripts.constants import *

class aiLevels:
    
    def __init__(self, display):

        self.display = display
        self.scroll = 0
        self.levelInfoIMG = load_image(path='UI/buttons/levelInfo.png', scale=(UIsize(80), UIsize(6)))
        self.background = load_image('UI/backgrounds/menuBG.png', scale=DISPLAY_SIZE)
        self.reloadButtons()
        self.setTexts()

    def setTexts(self):
        self.texts = []

        visual_text = Text("visuals:", pos = vh(94, 46), size=UIsize(1.5), color=(0,0,0))
        self.texts.append(visual_text)

        map_switch_text = Text("map switch:", pos = vh(94, 62), size=UIsize(1.5), color=(0,0,0))
        self.texts.append(map_switch_text)

    def reloadButtons(self):
        self.buttons = []

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        aiMode = []
        for idx, Mode in enumerate(('ai-train', 'ai-test', 'human')):
            spacing = 7
            aiMode_text = Text(Mode, pos = vh(94, 20 + spacing * idx), size=UIsize(2))
            aiMode_button = Button(aiMode_text, (129, 98, 252), button_type=Mode, scale_factor=1.1)
            aiMode.append(aiMode_button)
        self.aiModeRadio = radionButton(aiMode)

        visuals = []
        for idx, vls in enumerate(VISUALS):
            spacing = 4
            visuals_text = Text(vls, pos = vh(94, 50 + spacing * idx), size=UIsize(1))
            visuals_button = Button(visuals_text, (129, 98, 252), button_type=vls, scale_factor=1.1)
            visuals.append(visuals_button)
        self.visualsRadio = radionButton(visuals)

        mapSwitch = []
        for idx, msw in enumerate(MAP_SWITCH):
            spacing = 4
            mapSwitch_text = Text(msw, pos = vh(94, 66 + spacing * idx), size=UIsize(1))
            mapSwitch_button = Button(mapSwitch_text, (129, 98, 252), button_type=msw, scale_factor=1.1)
            mapSwitch.append(mapSwitch_button)
        self.mapSwitchRadio = radionButton(mapSwitch)
        
        my_maps_dict = map_manager.getAIMapsDict()
        for idx, map in enumerate(my_maps_dict.values()):
            map_text = map['info']['name'] + ' '*5 + map['info']['creator'] + ' '*5 + map['info']['difficulty']
            map_text = Text(map_text, pos = (vh(47, -1)[0], (idx+1)*vh(-1, 14)[1] - vh(-1, 3)[1]), size=UIsize(4), color=(40, 40, 40))
            map_button = Button(map_text, (0 ,255, 0), "map_idx: " + map['info']['id'], scale_factor=1.05, image=self.levelInfoIMG)
            self.buttons.append(map_button)

        new_map_text = Text('new map', pos = vh(90, 90), size=UIsize(3))
        new_map_button = Button(new_map_text, (0 ,255, 0), button_type='new_map')
        self.buttons.append(new_map_button)

        self.max_scroll = -vh(-1, 14)[1] * len(my_maps_dict)

        
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

        for text in self.texts:
            text.blit(display=self.display)

        for button in self.buttons:
            if button.type not in {'prev', 'new_map'}: button.set_offset(0, self.scroll)
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'prev':
                    game_state_manager.returnToPrevState()
                elif button.type == 'new_map':
                    map_manager.createNewAIMap()
                    game_state_manager.setState('ai_level_page')
                    self.reloadButtons()
                else:
                        map_id = button.type.split()[-1]
                        map_manager.setMap(map_id)
                        game_state_manager.setState('ai_level_page')

            button.blit(self.display)

        self.visualsRadio.chosen = VISUALS.index(game_state_manager.getGameSettings('visual'))
        vsl = self.visualsRadio.update(mouse_pressed, mouse_released)
        if vsl != game_state_manager.getGameSettings('visual'):
            game_state_manager.setGameSettings('visual', vsl)
        self.visualsRadio.blit(self.display)

        self.aiModeRadio.chosen = ('ai-train', 'ai-test', 'human').index(game_state_manager.getGameMode())
        Mode = self.aiModeRadio.update(mouse_pressed, mouse_released)
        if Mode != game_state_manager.getGameMode():
            game_state_manager.setGameMode(Mode)
        self.aiModeRadio.blit(self.display)

        self.mapSwitchRadio.chosen = MAP_SWITCH.index(game_state_manager.getGameSettings('map switch'))
        msw = self.mapSwitchRadio.update(mouse_pressed, mouse_released)
        if msw != game_state_manager.getGameSettings('map switch'):
            game_state_manager.setGameSettings('map switch', msw)
        self.mapSwitchRadio.blit(self.display)

class aiLevelPage:

    def __init__(self, display, level_select):
        self.display = display
        self.level_select = level_select
        self.background = load_image('UI/backgrounds/levelPage.png', scale=DISPLAY_SIZE)
        self.buttons = []

        play_text = Text('', pos = vh(60, 60), size=0)
        play_button = Button(play_text, (0 ,255, 0), button_type='play', scale_factor=1.1, image=load_image('UI/buttons/play.png', scale=(UIsize(5*35/11), UIsize(5))))
        self.buttons.append(play_button)

        edit_text = Text('', pos = vh(40, 60), size=0)
        edit_button = Button(edit_text, (0 ,255, 0), button_type='edit', scale_factor=1.1, image=load_image('UI/buttons/edit.png', scale=(UIsize(5*35/11), UIsize(5))))
        self.buttons.append(edit_button)

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        self.diff_faces = {diff: load_image(f'UI/difficulity/{diff}.png', scale=(UIsize(3), UIsize(3))) for diff in DIFFICULTIES}
        self.diff_faces['NA'] = load_image(f'UI/difficulity/NA.png', scale=(UIsize(3), UIsize(3)))

    def run(self):

        self.display.blit(self.background, (0, 0))

        map_info = map_manager.getAIMapInfo(map_manager.current_map_id)

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
                    game_state_manager.returnToPrevState()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_released = True

        for button in self.buttons:
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'prev':
                    game_state_manager.returnToPrevState()
                elif button.type == 'play':
                    print(map_manager.current_map_id)
                    map_manager.loadMap(isAi=True)
                    game_state_manager.setState('game')
                elif button.type == 'edit':
                    map_manager.loadMap(isAi=True)
                    game_state_manager.setState('edit')
            button.blit(self.display)

        

