import torch
from scripts.DQN import DQN
import numpy as np
from scripts.ReplayBuffer import ReplayBuffer
from scripts.constants import MIN_BUFFER

class aiAgent():
    def __init__(self):
        self.DQN = DQN()
        self.replayBuffer = ReplayBuffer()
        
        self.DQN_hat = self.DQN.copy()
        batch_size = 50
        learning_rate = 0.00001
        ephocs = 200000
        start_epoch = 0
        C = 3
        loss = torch.tensor(-1)
        avg = 0
        scores, losses, avg_score = [], [], []
        optim = torch.optim.Adam(self.DQN.parameters(), lr=learning_rate)
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
        step = 0
        
        

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
        
    def train(self):
        if len(self.replayBuffer) < MIN_BUFFER:
            return
        
            