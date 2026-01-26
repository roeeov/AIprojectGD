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
        # ephocs = 200000
        # loss = torch.tensor(-1)
        # avg = 0
        # scores, losses, avg_score = [], [], []
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        # step = 0
        
        

    def getAction(self, state, train = False):
        actions = self.get_actions()
        if train:
            epsilon = self.epsilon_greedy()
            rnd = random.random()
            if rnd < epsilon:
                return random.choice(actions).item()
      
        state_tensor = torch.from_numpy(state).flatten().float()
        with torch.no_grad():
            Q_values = self.DQN(state_tensor)
        max_index = torch.argmax(Q_values).item()
        
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
        
    def handle_training(self, state, action, reward, next_state, done):
        self.push_to_replayBuffer(state, action, reward, next_state, done)
        self.train()
        #if done: self.increment_epoch()
    
    def increment_epoch(self):
        self.epoch += 1
        C = 3 # update target network every C epochs
        if self.epoch % C == 0:
            self.DQN_hat.load_state_dict(self.DQN.state_dict())
        
    def push_to_replayBuffer(self, state, action, reward, next_state, done):
        self.replayBuffer.push(torch.from_numpy(state).to(torch.float32),
                                                   torch.tensor(action, dtype=torch.int32),
                                                   torch.tensor(reward, dtype=torch.float32),
                                                   torch.from_numpy(next_state).to(torch.float32),
                                                   torch.tensor(done, dtype=torch.float32))
        
    def train(self):
        if len(self.replayBuffer) < MIN_BUFFER:
            return
        
        batch_size = BATCH_SIZE
        states, actions, rewards, next_states, dones = self.replayBuffer.sample(batch_size)
        print(f"States shape: {states.shape}, Actions shape: {actions.shape}, Rewards shape: {rewards.shape}, Next_states shape: {next_states.shape}, Dones shape: {dones.shape}")  # Debugging line
        Q_values = self.Q(states = states, actions = actions)
        next_actions, Q_hat_Values = self.get_Actions_Values(next_states, modle= self.DQN_hat)

        loss = self.DQN.loss(Q_values, rewards, Q_hat_Values, dones)
        loss.backward()
        self.optim.step()
        self.optim.zero_grad()
        self.scheduler.step()

        self.increment_epoch()

        
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