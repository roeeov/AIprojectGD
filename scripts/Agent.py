import pygame

class Agent():

    def __init__(self):
        self.reset()

    def reset(self):
        self.input = {'w': False, 'space': False, 'up_arrow': False, 'mouse': False}

    def getAction(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.input['up_arrow'] = True
                if event.key == pygame.K_w:
                    self.input['w'] = True
                if event.key == pygame.K_SPACE:
                    self.input['space'] = True  

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

        return 1 if self.input['space'] or self.input['w'] or self.input['up_arrow'] or self.input['mouse'] else 0