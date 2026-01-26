from collections import deque
from scripts.constants import MAP_SWITCH, VISUALS

class gameStateManager:

    def __init__(self, currentState) -> None:
        self.currentState = currentState
        self.defualtState = self.currentState
        self.previousStates = deque()
        self.previousStates.append(self.defualtState)
        self.just_switch = None
        
        # human / ai-train / ai-test
        self.gameMode = 'human'
        self.gameSettings = {'visual': VISUALS[0], 'map switch': MAP_SWITCH[0]} # default settings

    def getState(self):
        return self.currentState
    
    def returnToPrevState(self):
        if len(self.previousStates) > 1:
            self.previousStates.pop()
            self.currentState = self.previousStates[-1]
        else: self.currentState = self.defualtState
        self.just_switch = self.currentState
    
    def setState(self, state):
        self.currentState = state
        self.previousStates.append(self.currentState)
        self.just_switch = self.currentState

    def justSwitched(self, state):
        if self.just_switch == state:
            self.just_switch = None
            return True
        return False
    
    def setGameMode(self, gameMode):
        self.gameMode = gameMode
        
    def getGameMode(self):
        return self.gameMode

    def setGameSettings(self, setting, value):
        match setting:
            case 'visual':
                self.gameSettings['visual'] = value
            case 'map switch':
                self.gameSettings['map switch'] = value
            case _:
                print("setting not found")


    def getGameSettings(self, setting):
        match setting:
            case 'visual':
                if self.getGameMode() == 'human':
                    return VISUALS[0]
                return self.gameSettings['visual']
            case 'map switch':
                if self.getGameMode() == 'human':
                    return MAP_SWITCH[2]
                return self.gameSettings['map switch']

        print("setting not found")
        return None
    
game_state_manager = gameStateManager('menu')