#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : ddpg_main
# @Function : 
# @Author : azson
# @Time : 2019/10/31 12:54
'''

import time
from torch_ddpg import DDPG
from redis_py import Redis_py
import numpy as np


#####################  hyper parameters  ####################

MAX_EPISODES = 200
MAX_EP_STEPS = 200
LR_A = 0.001    # learning rate for actor
LR_C = 0.002    # learning rate for critic
GAMMA = 0.9     # reward discount
TAU = 0.01      # soft replacement
MEMORY_CAPACITY = 100
BATCH_SIZE = 32
RENDER = False
ENV_NAME = 'Pendulum-v0'


################### env ###################

N_STATES = 8
N_ACTIONS = 3
a_bound = 1

# redis
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_DATA_CIRCLE=N_STATES*2 + N_ACTIONS + 1 #s、a、r、s_

Iters2Save=10000


def clear_single_data(raw_data):

    order_data = [raw_data[i:i+REDIS_DATA_CIRCLE:] for i in range(0, len(raw_data), REDIS_DATA_CIRCLE)]
    order_data = np.array(order_data, dtype=np.float64)

    return order_data.mean(axis=0)


def test_redis_data(op='show_list'):

    if op == 'show_list':

        ls1 = env.get_latest_block_info(size=0)
        print(ls1)

    elif op == 'clear_block':

        print(env.reset())

    elif op == 'prepare_block_list':

        print("block_1")
        print(env.rpush_elem_by_blockId("block_1", [1, 2, 3, 4, 5, 6, 7, 8,
                                                    0.1, 0.3, 0.6,
                                                    10,
                                                    2, 3, 4, 1, 3, 5, 6, 7]))

        print("block_2")
        print(env.rpush_elem_by_blockId("block_2", [2, 3, 4, 1, 3, 5, 6, 7,
                                                    0.3, 0.2, 0.5,
                                                    7,
                                                    4, 5, 3, 5, 7, 4, 3, 6]))

        print("block_3")
        print(env.rpush_elem_by_blockId("block_3", [4, 5, 3, 5, 7, 4, 3, 6,
                                                    0.5, 0.1, 0.4,
                                                    -3,
                                                    6, 2, 3, 2, 9, 3, 5, 4]))



if __name__ == '__main__':

    env = Redis_py(REDIS_HOST, REDIS_PORT)

    ddpg = DDPG(N_ACTIONS,
                N_STATES,
                a_bound,
                MEMORY_CAPACITY,
                LR_A,
                LR_C,
                GAMMA,
                BATCH_SIZE,
                TAU
                )

    var = 3  # control exploration
    t1 = time.time()
    i_episode = 0
    ep_reward = 0

    while True:

        # 从redis中获取是否停止训练的信号
        done = env.get_set_item('done')

        if done == 'True':
            print('Ep: ', i_episode,
                  '| Ep_r: ', round(ep_reward, 2))

            break

        latest_block_id_list, latest_block_list = env.get_latest_block_info(size=100)

        if not latest_block_id_list:
            continue

        for latest_block_id, latest_block in zip(latest_block_id_list, latest_block_list):

            if not latest_block_id or len(latest_block) % REDIS_DATA_CIRCLE:
                # redis没完整数据时等待
                print("there is no complete data in redis...")
                continue

            latest_block = clear_single_data(latest_block)

            # 从redis中提取数据
            s = list(map(lambda x: np.float64(x), latest_block[:N_STATES]))
            a = list(map(lambda x: np.float64(x), latest_block[N_STATES: N_STATES+N_ACTIONS]))
            r = np.float64(latest_block[N_STATES+N_ACTIONS])
            s_ = list(map(lambda x: np.float64(x), latest_block[N_STATES+N_ACTIONS+1:]))

            # pred_a = ddpg.choose_action(s)
            # print("pred_a is {0}".format(pred_a))
            # pred_s = [8, 7, 6, 5, 4, 3, 2, 1]
            # pred_a = ddpg.choose_action(pred_s)
            # print("s is {1}, pred_a is {0}".format(pred_a, pred_s))

            # # Add exploration noise
            # a = ddpg.choose_action(s)
            # a = np.clip(np.random.normal(a, var), -2, 2)  # add randomness to action selection for exploration
            # s_, r, done, info = env.step(a)
            # print(s, a, r, s_)
            #reward 是否scale？

            ddpg.store_transition(s, a, r, s_)

            if ddpg.pointer > MEMORY_CAPACITY:
                var *= .9995  # decay the action randomness
                ddpg.learn()

            # 持久化NN
            if i_episode and i_episode % Iters2Save == 0:
                pass
                #ddpg.save2onnx()

            # s = s_
            ep_reward += r
            i_episode += 1

            if i_episode and i_episode % MAX_EP_STEPS == 0:
                print('Episode:', i_episode, ' Reward: %i' % int(ep_reward), 'Explore: %.2f' % var, )
                if ep_reward > -300: RENDER = True
                # break

    print('Running time: ', time.time() - t1)