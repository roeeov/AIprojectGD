import sys

import pygame
from scripts.utils import *
from scripts.gameStateManager import game_state_manager
from scripts.mapManager import map_manager
from scripts.constants import *

class myLevels:
    
    def __init__(self, display):

        self.display = display
        self.scroll = 0
        self.levelInfoIMG = load_image(path='UI/buttons/levelInfo.png', scale=(UIsize(80), UIsize(6)))
        self.background = load_image('UI/backgrounds/menuBG.png', scale=DISPLAY_SIZE)
        self.reloadButtons()

    def reloadButtons(self):
        self.buttons = []

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        new_map_text = Text('new map', pos = vh(90, 90), size=UIsize(3))
        new_map_button = Button(new_map_text, (0 ,255, 0), button_type='new_map')
        self.buttons.append(new_map_button)

        my_maps_dict = map_manager.getEditorMapsDict()
        for idx, map in enumerate(my_maps_dict.values()):
            map_text = map['info']['name'] + ' '*5 + map['info']['creator'] + ' '*5 + map['info']['difficulty']
            map_text = Text(map_text, pos = (vh(50, -1)[0], (idx+1)*vh(-1, 14)[1] - vh(-1, 3)[1]), size=UIsize(4), color=(40, 40, 40))
            map_button = Button(map_text, (0 ,255, 0), "map_idx: " + map['info']['id'], scale_factor=1.05, image=self.levelInfoIMG)
            self.buttons.append(map_button)

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

        for button in self.buttons:
            if button.type not in {'prev', 'new_map'}: button.set_offset(0, self.scroll)
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                if button.type == 'prev':
                    game_state_manager.returnToPrevState()
                elif button.type == 'new_map':
                    map_manager.createNewMap()
                    game_state_manager.setState('my_level_page')
                    self.reloadButtons()
                else:
                        map_id = button.type.split()[-1]
                        map_manager.setMap(map_id)
                        game_state_manager.setState('my_level_page')

            button.blit(self.display)

class myLevelPage:

    def __init__(self, display, level_select):
        self.display = display
        self.level_select = level_select
        self.buttons = []

        play_text = Text('play', pos = vh(50, 62), size=UIsize(6))
        play_button = Button(play_text, (0 ,255, 0), button_type='play')
        self.buttons.append(play_button)

        edit_text = Text('edit', pos = vh(30, 62), size=UIsize(6))
        edit_button = Button(edit_text, (0 ,255, 0), button_type='edit')
        self.buttons.append(edit_button)

        post_text = Text('post', pos = vh(70, 62), size=UIsize(6))
        post_button = Button(post_text, (0 ,255, 0), button_type='post')
        self.buttons.append(post_button)

        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        creator_input = InputBox(vh(21, 47), width=0, height=UIsize(3), box_type='creator', placeholder='edit creator name...')
        name_input = InputBox(vh(42, 29), width=0, height=UIsize(3), box_type='name', placeholder='edit level name...')
        self.inputBoxes = (creator_input ,name_input)

        diffs = []
        diffLen = len(DIFFICULTIES)
        for idx, difficulity in enumerate(DIFFICULTIES):
            diff_text = Text(difficulity, pos = vh(70 - (diffLen/2 - 0.5)*7 + idx * 7, 47), size=UIsize(1.5))
            diff_button = Button(diff_text, (129, 98, 252), button_type=difficulity, scale_factor=1.1)
            diffs.append(diff_button)
        self.diffRadio = radionButton(diffs)

        self.diff_faces = {diff: load_image(f'UI/difficulity/{diff}.png', scale=(UIsize(3), UIsize(3))) for diff in DIFFICULTIES}
        self.diff_faces['NA'] = load_image(f'UI/difficulity/NA.png', scale=(UIsize(3), UIsize(3)))


    def run(self):

        self.display.fill((245, 137, 49))

        map_info = map_manager.getMapInfo(map_manager.current_map_id)

        map_name = map_info["name"]
        map_name_text = Text(map_name, pos = vh(50, 20), size=UIsize(5), color=(255, 255, 255))
        map_name_text.blit(display=self.display)

        map_creator = map_info["creator"]
        map_creator_text = Text("creator: " + map_creator, pos = vh(30, 40), size=UIsize(3), color=(255, 255, 255))
        map_creator_text.blit(display=self.display)

        map_difficulty = map_info["difficulty"]
        map_difficulty_text = Text("difficulty: ", pos =vh(70, 40), size=UIsize(3), color=(255, 255, 255))
        map_difficulty_text.blit(display=self.display)
        # blit difficulity face
        diff_faces_rect = self.diff_faces[map_difficulty].get_rect(center=vh(79, 40))
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

            for inputBox in self.inputBoxes:
                output = inputBox.handle_event(event)
                if output:
                    match inputBox.type:
                        case 'creator':
                            map_manager.updateMapInfo(creator=output)
                        case 'name':
                            map_manager.updateMapInfo(name=output)

        for inputBox in self.inputBoxes:
            inputBox.update()
            inputBox.draw(self.display)

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
                elif button.type == 'post':
                    map_info = map_manager.getMapInfo(map_manager.current_map_id)
                    creator, name = map_info['creator'].replace(" ", ""), map_info['name'].replace(" ", "")
                    if map_info['difficulty'] != 'NA' and creator not in {'', 'notentered'} and name not in {'', 'unnamed'}:
                        map_manager.updateMapInfo(id= map_manager.generateOnlineId())
                        map_manager.update_map_dict()
                        self.level_select.reloadButtons()
                        game_state_manager.returnToPrevState()
            button.blit(self.display)

        self.diffRadio.chosen = DIFFICULTIES.index(map_info['difficulty']) if map_info['difficulty'] != 'NA' else -1
        diff = self.diffRadio.update(mouse_pressed, mouse_released)
        if diff not in {None, map_info['difficulty']}:
            map_manager.updateMapInfo(difficulty=diff)
        self.diffRadio.blit(self.display)

        

