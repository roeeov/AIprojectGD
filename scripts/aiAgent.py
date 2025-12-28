import torch
from scripts.DQN import DQN
import numpy as np

class aiAgent():
    def __init__(self):
        self.DQN = DQN()

    def getAction(self, state):
        # Flatten the state from (19, 2) to (38,)
        state_tensor = torch.from_numpy(state).flatten().float()
        actions = self.get_actions()
        
        # actions is [0, 1], we need to make it (2, 1) for concatenation
        action_tensor = actions.unsqueeze(1).float()
        
        # Expand flattened state to match number of actions: (2, 38)
        expand_state_tensor = state_tensor.unsqueeze(0).repeat((len(actions), 1))
        
        # Debug: check shapes before DQN call
        print(f"expand_state_tensor shape: {expand_state_tensor.shape}")
        print(f"action_tensor shape: {action_tensor.shape}")
        
        with torch.no_grad():
            Q_values = self.DQN(expand_state_tensor, action_tensor)
        
        # Get the index as a Python int
        max_index = torch.argmax(Q_values).item()
        
        # Return the action value as a Python int/float
        return actions[max_index].item()

    def get_actions(self):
        actions = torch.tensor([0, 1])
        return actions