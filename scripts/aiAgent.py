import torch
from scripts.DQN import DQN
import numpy as np
from scripts.ReplayBuffer import ReplayBuffer
from scripts.constants import *
import random

class aiAgent():
    def __init__(self):
        self.DQN = DQN()
        self.replayBuffer = ReplayBuffer()
        
        self.DQN_hat = self.DQN.copy()
        learning_rate = 0.00001
        self.optim = torch.optim.Adam(self.DQN.parameters(), lr=learning_rate)
        self.epoch = 0
        self.scheduler = torch.optim.lr_scheduler.MultiStepLR(self.optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
        ephocs = 200000
        loss = torch.tensor(-1)
        avg = 0
        scores, losses, avg_score = [], [], []
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        step = 0
        
        

    def getAction(self, state, train = False):
        # Flatten the state from (19, 2) to (38,)
        actions = self.get_actions()
        if train:
            epsilon = self.epsilon_greedy()
            rnd = random.random()
            if rnd < epsilon:
                return random.choice(actions)
      
        state_tensor = torch.from_numpy(state).flatten().float()
        with torch.no_grad():
            Q_values = self.DQN(state_tensor)
        max_index = torch.argmax(Q_values).item()
        
        # Return the action value as a Python int/float
        return actions[max_index].item()

    def get_actions(self):
        actions = torch.tensor([0, 1])
        return actions
    
    def get_Actions_Values (self, states, modle = None):
        with torch.no_grad():
            DQN_modle = self.DQN if modle is None else modle
            Q_values = DQN_modle(states)
            max_values, max_indices = torch.max(Q_values,dim=1) # best_values, best_actions
            return max_indices.reshape(-1,1), max_values.reshape(-1,1)
        
    def push_to_replayBuffer(self, state, action, reward, next_state, done):
        self.replayBuffer.push(state, action, reward, next_state, done)
        
    def train(self):
        if len(self.replayBuffer) < MIN_BUFFER:
            return
        
        batch_size = 50
        states, actions, rewards, next_states, dones = self.replayBuffer.sample(batch_size)
        Q_values = self.Q(states, actions)
        next_actions, Q_hat_Values = self.get_Actions_Values(next_states, modle= self.DQN_hat)

        loss = self.DQN.loss(Q_values, rewards, Q_hat_Values, dones)
        loss.backward()
        self.optim.step()
        self.optim.zero_grad()
        self.scheduler.step()

        C = 3
        if self.epoch % C == 0:
            self.DQN_hat.load_state_dict(self.DQN.state_dict())
        self.epoch += 1
        
    def Q(self, states, actions):
        Q_values = self.DQN(states) # try: Q_values = self.DQN(states).gather(dim=1, actions) ; check if shape of actions is [-1, 1] otherwise dim=0
        rows = torch.arange(Q_values.shape[0]).reshape(-1,1)
        cols = actions.reshape(-1,1)
        return Q_values[rows, cols]
    
    def epsilon_greedy(self, epoch = None, start=EPSILON_START, final=EPSILON_FINAL, decay=EPSILON_DECAY):
        if epoch is None: epoch = self.epoch
        # res = final + (start - final) * math.exp(-1 * epoch/decay)
        if epoch < decay:
            return start - (start - final) * epoch/decay
        return final