import torch
from scripts.DQN import DQN
import numpy as np
from scripts.ReplayBuffer import ReplayBuffer

class aiAgent():
    def __init__(self):
        self.DQN = DQN()
        self.replayBuffer = ReplayBuffer()

    def getAction(self, state):
        # Flatten the state from (19, 2) to (38,)
        state_tensor = torch.from_numpy(state).flatten().float()
        actions = self.get_actions()
      
        with torch.no_grad():
            Q_values = self.DQN(state_tensor)
        max_index = torch.argmax(Q_values).item()
        
        # Return the action value as a Python int/float
        return actions[max_index].item()

    def get_actions(self):
        actions = torch.tensor([0, 1])
        return actions
    
    def get_Actions_Values (self, states):
        with torch.no_grad():
            Q_values = self.DQN(states)
            max_values, max_indices = torch.max(Q_values,dim=1) # best_values, best_actions
            return max_indices.reshape(-1,1), max_values.reshape(-1,1)
        
    def push_to_replayBuffer(self, state, action, reward, next_state, done):
        self.replayBuffer.push(state, action, reward, next_state, done)
        
    def train():
        pass