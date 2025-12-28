import torch
import torch.nn as nn
import torch.nn.functional as F
from scripts.constants import *

# Parameters
input_size = len(STATE_ANGLES) * 2 + 1 # distances and angles of each ray + action
layer1 = 128
layer2 = 64
output_size = 1 # Q(s,a)
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
        
    def forward (self, x):
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        x = F.relu(x)
        x = self.output(x)
        return x
    
    def __call__(self, states, actions):
        state_action = torch.cat((states,actions), dim=1)
        return self.forward(state_action)