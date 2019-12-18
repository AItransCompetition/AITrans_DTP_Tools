import os
import numpy as np
from itertools import count
from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal

import rl_hyperparameters

import threading

class rl_stats:

    #Current time
    current_time = 0.0

    #The Deadline
    deadline = 0

    # The latency
    latency = 0.0

    # The start time
    start_time = 0.0

    #The network states .
    bandwidth = 0.0

    #The network states .
    rtt = 0.0

    #The network states .
    loss_rate = 0.0

    #The remaining time
    remaing_time = 0.0

    #The Block size
    block_size = 0

    #The Piroity
    priority = 0

    #The Deadline
    deadline = 0

    #The Sender Buffer Len
    send_buf_len = 0

    #The Block id
    block_id = 0

    # The priority
    priority = 0


    # def __init__(self, current_time, deadline, latency, start_time, bandwidth, remaing_time, send_buf_len, loss_rate, block_id, rtt, block_size, priority):
    #     self.current_time = current_time
    #     self.deadline = deadline
    #     self.latency = latency
    #     self.start_time = start_time
    #     self.bandwidth = bandwidth
    #     self.remaing_time = remaing_time
    #     self.send_buf_len = send_buf_len
    #     self.loss_rate = loss_rate
    #     self.block_id = block_id
    #     self.rtt = rtt
    #     self.block_size = block_size
    #     self.priority = priority

    def __init__(self, state_dict):
        self.current_time = state_dict['current_time']
        self.deadline = state_dict['deadline']
        self.latency = state_dict['latency']
        self.start_time = state_dict['start_time']
        self.bandwidth = state_dict['bandwidth']
        self.send_buf_len = state_dict['send_buf_len']
        self.loss_rate = state_dict['loss_rate']
        self.block_id = state_dict['block_id']
        self.rtt = state_dict['rtt']
        self.block_size = state_dict['block_size']
        self.priority = state_dict['priority']
    
    def to_list(self):
        return [self.current_time, 
                self.deadline, 
                self.latency, 
                self.start_time, 
                self.bandwidth, 
                self.remaing_time, 
                self.send_buf_len, 
                self.loss_rate, 
                self.block_id, 
                self.rtt, 
                self.block_size, 
                self.priority]
    	
    
############## user rl Policy ################

class Policy(nn.Module):
    def __init__(self):
        super(Policy, self).__init__()


        self.fc1 = nn.Linear(rl_hyperparameters.state_space, 32)

        self.action_head = nn.Linear(32, rl_hyperparameters.action_space)
        self.value_head = nn.Linear(32, 1) # Scalar Value

        

        self.all_rl_stats = []
        self.len_of_rl_stats = 0
        self.dict_id_to_block_info = {}


        self.save_actions = [[1, 1]]
        self.rewards = []
        os.makedirs('./AC_demo', exist_ok=True)
    
    def update_dict_of_block(self):
        if len(self.all_rl_stats) > self.len_of_rl_stats and len(self.rewards) == len(self.save_actions):
            for i in range(len(self.all_rl_stats) - self.len_of_rl_stats):
                block_dict = self.all_rl_stats[self.len_of_rl_stats + i]
                for info in block_dict:
                    self.dict_id_to_block_info[int(info['block_id'])] = rl_stats(info)
            self.len_of_rl_stats = len(self.all_rl_stats)
            
            return True
        return False

    def forward(self, x):
        x = F.relu(self.fc1(x))
        action_score = self.action_head(x)
        state_value = self.value_head(x)

        return F.softmax(action_score, dim=-1), state_value

############### user rl algorithm Policy ##################





###############  user training code #####################
class Train():
    def __init__(self, policy):
        self.policy = policy
        self.optimizer = optim.Adam(policy.parameters(), lr=rl_hyperparameters.learning_rate)

    def run(self):

        episode = 0
        while True:
            if self.policy.update_dict_of_block():
                # there is a new state
                self.policy.save_actions.append([1, 1])

                if episode % 20 == 0:
                    finish_episode(self.policy, self.optimizer)

                if episode % 100 == 0:
                    model_path = './AC_model/ModelTraining' + str(episode) + 'Times.pkl'
                    torch.save(self.policy, model_path)

                episode += 1
                
                
###############  user training code #####################





class rl_thread(threading.Thread):
    def __init__(self, threadID, name, train):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

        self.train = train

    def run(self):

        self.train.run()


def select_action(state, model):
    state = torch.from_numpy(np.array(state)).float()
    probs, state_value = model(state)
    # print(probs[0:2])
    m = Normal(probs[0:2], probs[2:4])
    action = m.sample()
    # print(action)
    model.save_actions.append(rl_hyperparameters.SavedAction(m.log_prob(action), state_value))
    # print(action.item())
    return action.numpy().tolist()



def finish_episode(model, optimizer):
    R = 0
    save_actions = model.save_actions
    policy_loss = []
    value_loss = []
    rewards = []

    for r in model.rewards[::-1]:
        R = r + rl_hyperparameters.gamma * R
        rewards.insert(0, R)

    rewards = torch.tensor(rewards)
    rewards = (rewards - rewards.mean()) / (rewards.std() + rl_hyperparameters.eps)
    print(save_actions)
    print(rewards)
    for (log_prob , value), r in zip(save_actions, rewards):
        reward = r - value.item()
        policy_loss.append(-log_prob * reward)
        value_loss.append(F.smooth_l1_loss(value, torch.tensor([r])))
    print("1111", policy_loss)
    print("2222", value_loss)
    optimizer.zero_grad()
    loss = torch.stack(policy_loss).sum() + torch.stack(value_loss).sum()
    loss.backward()
    optimizer.step()

    del model.rewards[:]
    del model.save_actions[:]


# Return action to Zmq

def get_action(state, model):

    action_state = None
    for info in state:
        if info['send_buf_len'] < info['block_size']:
            action_state = rl_stats(info)

    # calculate action 
    action = select_action(action_state.to_list(), model)

    # add state
    model.rewards.append((action_state.block_size - action_state.send_buf_len) / action_state.block_size - 0.5)

    # action 
    action[0] = int(action[0])
    action[1] = int(max(action[1] * 10000000000, 7777777))

    return action




