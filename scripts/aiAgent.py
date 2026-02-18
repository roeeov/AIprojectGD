import os
import torch
from scripts.DQN import DQN
import numpy as np
from scripts.ReplayBuffer import ReplayBuffer
from scripts.constants import *
import random
import wandb

class aiAgent():
    def __init__(self, envronment):
        self.env = envronment
        self.DQN = DQN()
        self.replayBuffer = ReplayBuffer()
        
        self.DQN_hat = self.DQN.copy()
        learning_rate = 0.00001
        self.optim = torch.optim.Adam(self.DQN.parameters(), lr=learning_rate)
        self.epoch = 0
        self.step = 0
        self.scheduler = torch.optim.lr_scheduler.MultiStepLR(self.optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
        # ephocs = 200000
        # loss = torch.tensor(-1)
        self.avg = 0
        self.end_reached = 0
        self.scores, self.losses, self.avg_score = [], [], []
        self.current_model_avg_score = 0
        self.best_model_avg_score = float('-inf')
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        # step = 0
        self.load_checkpoint()

        num = 5 # wandb run number, change if you want to start a new run instead of resuming
        project_name = "GeoRush"
        entity_name = "roeeovadia1-"
        self.run = wandb.init(
            resume='allow',
            id=f'AIprojectGD-{num}',
            config={
            "name": project_name,
            "entity": entity_name
        })

    def getAction(self, state, train = False):
        if TEST_REWARD_SYSTEM:
            return int(self.env.calculate_reward(1, state) > self.env.calculate_reward(0, state))
        
        actions = self.get_actions()
        if train:
            epsilon = self.epsilon_greedy(counter=self.step)
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
        if len(self.replayBuffer) < MIN_BUFFER:
            return
        self.train(gave_over=done, player_won=(reward > 0))
        if done:
            self.select_better_model()
            self.epoch += 1
        
    def select_better_model(self):
        if self.epoch % 100 == 0:
            if self.current_model_avg_score > self.best_model_avg_score:
                self.best_model_avg_score = self.current_model_avg_score
                self.save_checkpoint()
                print(f"New best model with average score: {self.current_model_avg_score}")
            else:
                self.load_checkpoint()
                print(f"Model did not improve. Loaded best model with average score: {self.best_model_avg_score}")
            self.current_model_avg_score = 0
    
    def compare_model_values(self, counter = None):
        if counter is None: counter = self.epoch
        C = 5 # update target network every C epochs
        if counter % C == 0:
            self.DQN_hat.load_state_dict(self.DQN.state_dict())
        
    def push_to_replayBuffer(self, state, action, reward, next_state, done):
        self.replayBuffer.push(torch.from_numpy(state).to(torch.float32),
                                                   torch.tensor(action, dtype=torch.int32),
                                                   torch.tensor(reward, dtype=torch.float32),
                                                   torch.from_numpy(next_state).to(torch.float32),
                                                   torch.tensor(done, dtype=torch.float32))
        
    def train(self, gave_over=False, player_won=False):
        batch_size = BATCH_SIZE
        states, actions, rewards, next_states, dones = self.replayBuffer.sample(batch_size)
        Q_values = self.Q(states = states, actions = actions)
        next_actions, Q_hat_Values = self.get_Actions_Values(next_states, modle= self.DQN_hat)

        loss = self.DQN.loss(Q_values, rewards, Q_hat_Values, dones)
        loss.backward()
        self.optim.step()
        self.optim.zero_grad()
        self.scheduler.step()

        self.step += 1
        self.compare_model_values(counter=self.step)

        if gave_over:
            self.end_reached += int(player_won)
            self.avg = (self.avg * (self.epoch % 10) + self.env.score) / (self.epoch % 10 + 1)
            if self.epoch % 10 == 0:
                self.scores.append(self.env.score)
                self.losses.append(loss.item())

            if (self.epoch + 1) % 10 == 0:
                self.avg_score.append(self.avg)
                self.log(
                    score=self.env.score,
                    loss=loss.item(),
                    avg_score=self.avg)
                if PRINT_AI_STATUS: print(f'average score last 10 games: {self.avg} ')
                self.current_model_avg_score += self.avg
                self.avg = 0
            if (self.epoch + 1) % 50 == 0:
                self.log(
                    end_reached = self.end_reached,
                )
                self.end_reached = 0


    def save_checkpoint(self):
        checkpoint_path, buffer_path = self.get_checkpoint_path()
        checkpoint = {
                'epoch': self.epoch,
                'step': self.step,
                'model_state_dict': self.DQN.state_dict(),
                'optimizer_state_dict': self.optim.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
                'loss': self.losses,
                'scores':self.scores,
                'avg_score': self.avg_score,
                'best_model_avg_score': self.best_model_avg_score
        }
        torch.save(checkpoint, checkpoint_path)
        torch.save(self.replayBuffer, buffer_path)

    def load_checkpoint(self):
        checkpoint_path, buffer_path = self.get_checkpoint_path()
        if not os.path.exists(checkpoint_path): return
        checkpoint = torch.load(checkpoint_path, weights_only=False)

        self.epoch = checkpoint['epoch']+1
        self.step = checkpoint['step']+1
        self.DQN.load_state_dict(checkpoint['model_state_dict'])
        self.DQN_hat.load_state_dict(checkpoint['model_state_dict'])
        self.optim.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.replayBuffer = torch.load(buffer_path, weights_only=False)

        self.losses = checkpoint['loss']
        self.scores = checkpoint['scores']
        self.avg_score = checkpoint['avg_score']
        self.best_model_avg_score = checkpoint['best_model_avg_score']

    def get_checkpoint_path(self):
        checkpoint_path = "data/checkpoint_data/checkpoint1.pth"
        buffer_path = "data/checkpoint_data/buffer1.pth"
        return checkpoint_path, buffer_path

    def log(self, score = None, loss = None, avg_score = None, end_reached = None):
        if self.run is not None:
            if score is not None:
                self.run.log({"score": score})
            if loss is not None:
                self.run.log({"loss": loss})
            if avg_score is not None:
                self.run.log({"avg_score": avg_score})
            if end_reached is not None:
                self.run.log({"end_reached": end_reached})
        
    def Q(self, states, actions):
        Q_values = self.DQN(states)
        rows = torch.arange(Q_values.shape[0]).reshape(-1,1)
        cols = actions.reshape(-1,1)
        return Q_values[rows, cols]
    
    def epsilon_greedy(self, counter = None, start=EPSILON_START, final=EPSILON_FINAL, decay=EPSILON_DECAY):
        if counter is None: counter = self.step
        # res = final + (start - final) * math.exp(-1 * epoch/decay)
        if counter < decay:
            return start - (start - final) * counter/decay
        return final