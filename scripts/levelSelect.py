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
        self.sort = 'recent'
        self.reloadButtons()

    def reloadButtons(self):
        self.buttons = []

        prev_text = Text('', pos = (50, 50), size=0)
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        reload_text = Text('', pos = (vh(93, -1)[0], vh(-1, 90)[1]), size=0)
        reload_button = Button(reload_text, (0 ,255, 0), button_type='reload', image=load_image('UI/buttons/reload.png', scale=(UIsize(3*35/11), UIsize(3))), scale_factor=1.1)
        self.buttons.append(reload_button)

        sorting = []
        for idx, srt in enumerate(SORTING):
            spacing = 6
            sort_text = Text(srt, pos = vh(93, 30 + spacing * idx), size=UIsize(1.5))
            sort_button = Button(sort_text, (129, 98, 252), button_type=srt, scale_factor=1.1)
            sorting.append(sort_button)
        self.sortRadio = radionButton(sorting)

        self.online_map_dict = map_manager.list_online_levels()
        self.resortLevels()
        self.max_scroll = -vh(-1, 14)[1] * len(self.online_map_dict)

    def resortLevels(self):
        self.buttons = self.buttons[:2]  # Keep the first two buttons (prev and reload)
        
        match self.sort:
            case 'recent':
                self.online_map_dict = {k: self.online_map_dict[k] for k in sorted(self.online_map_dict, key=lambda x: x, reverse=True)}
            case 'difficulty':
                self.online_map_dict = {k:self. online_map_dict[k] for k in sorted(self.online_map_dict, key=lambda x: DIFFICULTIES.index(self.online_map_dict[x]['difficulty']))}

        for idx, map in enumerate(self.online_map_dict.items()):
            map_text = map[1]['name'] + ' '*5 + map[1]['creator'] + ' '*5 + map[1]['difficulty']
            map_text = Text(map_text, pos = (vh(47, -1)[0], (idx+1)*vh(-1, 14)[1] - vh(-1, 3)[1]), size=UIsize(4), color=(40, 40, 40))
            map_button = Button(map_text, (0 ,255, 0), "map_idx: " + map[0], scale_factor=1.05, image=self.levelInfoIMG)
            self.buttons.append(map_button)

        
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
                    blitLoading(self.display, 'LOADING LEVELS...')
                    self.reloadButtons()
                else:
                    map_id = button.type.split()[-1]
                    map_manager.setMap(map_id)
                    game_state_manager.setState('level_page')
            button.blit(self.display)

        self.sortRadio.chosen = SORTING.index(self.sort)
        srt = self.sortRadio.update(mouse_pressed, mouse_released)
        if srt != self.sort:
            self.sort = srt
            self.resortLevels()
            self.scroll = 0
        self.sortRadio.blit(self.display)

class LevelPage:

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

        sync_text = Text('', pos = (vh(93, -1)[0], vh(-1, 93)[1]), size=0)
        sync_button = Button(sync_text, (0 ,255, 0), button_type='sync', image=load_image('UI/buttons/sync.png', scale=(UIsize(3*35/11), UIsize(3))))
        self.buttons.append(sync_button)

        self.diff_faces = {diff: load_image(f'UI/difficulity/{diff}.png', scale=(UIsize(3), UIsize(3))) for diff in DIFFICULTIES}

    def run(self):

        self.display.blit(self.background, (0, 0))

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
                    if not map_manager.isMapLoaded(map_manager.current_map_id):
                        blitLoading(self.display, 'DOWNLOADING MAP...')
                        map_manager.sync_level(map_manager.current_map_id)
                    map_manager.loadMap()
                    game_state_manager.setState('game')
                elif button.type == 'sync':
                    blitLoading(self.display, 'SYNCING MAP...')
                    map_manager.sync_level(map_manager.current_map_id)
                elif button.type == 'edit':
                    if not map_manager.isMapLoaded(map_manager.current_map_id):
                        blitLoading(self.display, 'DOWNLOADING MAP...')
                        map_manager.sync_level(map_manager.current_map_id)
                    map_manager.loadMap()
                    game_state_manager.setState('edit')
            button.blit(self.display)

        

