from collections import deque

class gameStateManager:

    def __init__(self, currentState) -> None:
        self.currentState = currentState
        self.defualtState = self.currentState
        self.previousStates = deque()
        self.previousStates.append(self.defualtState)
        self.just_switch = None
        
        self.gameMode = None
        # human / ai-train / ai-test

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

game_state_manager = gameStateManager('menu')