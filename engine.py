import pygame
from scripts.constants import DISPLAY_SIZE, FPS, SHOW_FPS_COUNTER
from scripts.game import Game
from scripts.menu import Menu
from scripts.levelSelect import LevelSelect, LevelPage
from scripts.myLevels import myLevels, myLevelPage
from scripts.aiLevels import aiLevels, aiLevelPage
from scripts.gameStateManager import game_state_manager
from scripts.utils import Text, blitLoading
from scripts.editor import Editor
from scripts.mapManager import map_manager

class Engine:

    def __init__(self):
        pygame.init()

        pygame.display.set_caption('geometry dash')
        self.display = pygame.display.set_mode(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        
        blitLoading(self.display, 'LOADING...')
        map_manager._initialize()

        game = Game(self.display)
        menu = Menu(self.display)
        level_select = LevelSelect(self.display)
        level_page = LevelPage(self.display, level_select)
        my_levels = myLevels(self.display)
        my_level_page = myLevelPage(self.display, my_levels)
        ai_levels = aiLevels(self.display)
        ai_level_page = aiLevelPage(self.display, ai_levels)
        editor = Editor(self.display)

        self.state = {'game': game, 'menu': menu, 'level_select': level_select,
                      'level_page': level_page, 'edit': editor, 'my_levels': my_levels,
                      'my_level_page': my_level_page, 'ai_levels': ai_levels, 'ai_level_page': ai_level_page}

    def run(self):
        while True:
            self.state[game_state_manager.getState()].run()

            # blit fps counter
            if SHOW_FPS_COUNTER:
                fpsTXT = Text(str(int(self.clock.get_fps())), (50, 50), (255, 0, 0))
                fpsTXT.blit(self.display)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':  
    Engine().run()