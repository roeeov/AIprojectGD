import torch
import torch.nn as nn
import torch.nn.functional as F
from scripts.constants import *
import copy

# Parameters
input_size = len(STATE_ANGLES) * 2 # distances and angles of each ray
layer1 = 128
layer2 = 64
output_size = 2 #value of each action
gamma = 0.99 
MSELoss = nn.MSELoss()

class DQN (nn.Module):
    def __init__(self) -> None:
        super().__init__()
        if torch.cuda.is_available:
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')
        
        self.linear1 = nn.Linear(input_size, layer1)
        self.linear2 = nn.Linear(layer1, layer2)
        self.output = nn.Linear(layer2, output_size)
        self.MSELoss = nn.MSELoss()
        
    def forward (self, x):
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        x = F.relu(x)
        x = self.output(x)
        return x
    
    def loss (self, Q_values, rewards, Q_next_Values, dones ):
        gamma = GAMMA
        Q_new = rewards + gamma * Q_next_Values * (1- dones)
        return self.MSELoss(Q_values, Q_new)
    
    def load_params(self, path):
        self.load_state_dict(torch.load(path))

    def copy (self):
        return copy.deepcopy(self)
    
    def __call__(self, states):
        return self.forward(states)