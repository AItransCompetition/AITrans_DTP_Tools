import time
import numpy as np
from data_process import data_process 
from torch_ddpg import DDPG

#####################  hyper parameters  ####################

MAX_EP_STEPS = 50
LR_A = 0.001    # learning rate for actor
LR_C = 0.002    # learning rate for critic
GAMMA = 0.9     # reward discount
TAU = 0.01      # soft replacement
MEMORY_CAPACITY = 100
BATCH_SIZE = 32
RENDER = False
ENV_NAME = 'Pendulum-v0'


################### env ###################

N_STATES = 6
N_ACTIONS = 3
N_BLOCKS = 5
a_bound = 1

onnx_file='ddpg_jay.onnx'
var = 3

class agent(object):

    def __init__(self, keys_prefix):
       self.agent = DDPG(N_ACTIONS,
                        N_STATES,
                        a_bound,
                        MEMORY_CAPACITY,
                        LR_A,
                        LR_C,
                        GAMMA,
                        BATCH_SIZE,
                        TAU,
                        N_BLOCKS
                        )
       self.data_process = data_process()
       self.keys_prefix = keys_prefix
       self.var = var

    def agent_run(self):
        
        #training_list= self.data_process.get_cur_list("STEP_15736661254142179328_ATTEMP")
        training_list= self.data_process.get_cur_list(self.keys_prefix)
        if training_list == None:
            return 

        last_state = [[1.0,1.0,1.0,1.0,1.0,1.0]] * 5
        last_block_reward = {}
        i_episode = 0
        ep_reward = 0

        print("start the training")
        ff = open("agent_client.log","w")
        for idx in range(len(training_list)):    
            cur_time_interval = self.data_process.get_unit_info(training_list[idx])
            #print(cur_time_interval)
            cur_data_info = self.data_process.handle_unit_info(cur_time_interval)
            if cur_data_info == None:
                continue
            state = self.data_process.organize_state(cur_data_info['state']) 
            action = cur_data_info['action'] 
            reward = cur_data_info["reward"]
            ff.write(str(state))
            ff.write("\n")
            r = 0
            for block_id,block_reward in reward.items():
                if block_id not in last_block_reward:
                    r += block_reward
                else:
                    r += block_reward-last_block_reward[block_id]
                last_block_reward[block_id] = block_reward
            self.agent.store_transition(last_state, action, r, state)

            last_state = state

            if self.agent.pointer > MEMORY_CAPACITY:
                self.var *= .9995  # decay the action randomness
                self.agent.learn()

            ep_reward += r
            i_episode += 1

            if  i_episode % MAX_EP_STEPS == 0:
                print('Episode:', i_episode, ' Reward: %i' % int(ep_reward), 'Explore: %.2f' % var, )
            #ddpg.store_transition(new_s, a, r, new_s_) 
        onnx_file = self.agent.save2onnx(self.keys_prefix)
        ff.close()
#agent = agent("STEP_15736661254142179328_ATTEMP")
#agent.agent_run()
