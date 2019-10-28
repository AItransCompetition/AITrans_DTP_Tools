#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : main
# @Function : get the data from redis and train DQN by the data
# @Author : azson
# @Time : 2019/10/24 15:40
'''

from torch_dqn import DQN
from redis_py import Redis_py
import numpy as np
# from tf_dqn import DeepQNetwork


# DQN
BATCH_SIZE = 32
LR = 0.01  # learning rate
EPSILON = 0.9  # 最优选择动作百分比
GAMMA = 0.9  # 奖励递减参数
TARGET_REPLACE_ITER = 100  # Q 现实网络的更新频率
MEMORY_CAPACITY = 2000  # 记忆库大小

# env
N_ACTIONS = 3
N_STATES = 3
LEARN_START=200
LEARN_CIRCLE=10

# redis
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_DATA_CIRCLE=(N_STATES+1)*2 #s、a、r、s_

Iters2Save=10000


def clear_single_data(raw_data):

    order_data = [raw_data[i:i+REDIS_DATA_CIRCLE:] for i in range(0, len(raw_data), REDIS_DATA_CIRCLE)]
    order_data = np.array(order_data, dtype=np.float64)
    return order_data.mean(axis=0)


if __name__ == '__main__':
    #
    # # 创建torch DQN网络
    dqn = DQN(N_STATES=N_STATES,
             N_ACTIONS=N_ACTIONS,
             LR=LR,
             EPSILON=EPSILON,
             GAMMA=GAMMA,
             TARGET_REPLACE_ITER=TARGET_REPLACE_ITER,
             MEMORY_CAPACITY=MEMORY_CAPACITY,
             BATCH_SIZE=BATCH_SIZE)

    #tf qdn
    # dqn = DeepQNetwork(
    #     n_actions=N_ACTIONS,
    #     n_features=N_STATES,
    #     learning_rate=LR,
    #     e_greedy=EPSILON,
    #     reward_decay=GAMMA,
    #     replace_target_iter=TARGET_REPLACE_ITER,
    #     memory_size=MEMORY_CAPACITY,
    #     batch_size=BATCH_SIZE,
    # )

    # 获取redis连接
    env = Redis_py(REDIS_HOST, REDIS_PORT)

    print('\nCollecting experience...')

    ep_r = 0
    i_episode = 0
    while True:

        # 获取具有 block_[0-9]* 模式的block，取字典序最大，即时间戳最大，即最新的block
        latest_block_id_list, latest_block_list = env.get_latest_block_info(size=100)

        if not latest_block_id_list:
            continue

        for latest_block_id, latest_block in zip(latest_block_id_list, latest_block_list):

            if not latest_block_id or len(latest_block) % REDIS_DATA_CIRCLE:
                # redis没完整数据时等待
                print("there is complete data in redis...")
                continue

            # 测试数据少，不开启，用于保证该条block只用一次
            # env.del_block(latest_block_id)

            latest_block = clear_single_data(latest_block)

            # 从redis中提取数据
            s = list(map(lambda x:np.float64(x), latest_block[-N_STATES:][::-1]))
            a = np.float64(latest_block[-N_STATES-1])
            r = np.float64(latest_block[-N_STATES-2])
            s_ = list(map(lambda x:np.float64(x), latest_block[:N_STATES][::-1]))

            # 输入到记忆库
            dqn.store_transition(s, a, r, s_)

            ep_r += r

            # DQN learn
            if dqn.memory_counter > LEARN_START and dqn.memory_counter % LEARN_CIRCLE == 0:
                print("latest block {0}".format(latest_block))
                dqn.learn()

            # 持久化NN
            if i_episode and i_episode % Iters2Save == 0:
                dqn.save2onnx()

            i_episode += 1

        # 从redis中获取是否停止训练的信号
        done = env.get_set_item('done')

        if done == 'True':
            print('Ep: ', i_episode,
                  '| Ep_r: ', round(ep_r, 2))

            break

        # s = s_
