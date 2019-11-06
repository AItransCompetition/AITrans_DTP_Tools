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
import re, os, json


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

N_STATES = 6
N_ACTIONS = 3
a_bound = 1

# redis
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379

REDIS_DATA_CIRCLE=N_STATES*2+N_ACTIONS+1 #s、a、r、s_
REDIS_DATA_P_MAX=2
REDIS_DATA_BW_MAX=10000
REDIS_DATA_RTT_MAX=2000

Iters2Save=1000
STATES_KEYS=['bandwidth', 'rtt', 'loss_rate', 'remaing_time', 'priority', 'send_buf_len']

pre_reward = {}
records = {}

statis=[0, 0]

def clear_single_data(raw_data):
    '''
    get (s, a, r)
    :param raw_data:
    :return:
    '''

    # cal reward
    state_idx=-1
    redis_reward={}
    fir=True
    for idx, item in enumerate(raw_data[::-1]):

        if "ID" not in item:
            if fir:
                continue
            state_idx=idx
            break

        if fir:
            fir=False

        id, now_reward = re.findall('[0-9]+', item)
        id, now_reward = int(id), float(now_reward)

        if id not in pre_reward.keys():
            pre_reward[id] = 0

        if id not in redis_reward.keys():
            redis_reward[id] = 0

        redis_reward[id] = max(redis_reward[id], now_reward)

    # no reward in this list
    if state_idx == -1:
        return None

    # cal states
    order_data = {}

    for item in raw_data[-state_idx-1:0:-1]:
        item = json.loads(item)

        if item['block_size'] == 0 or item['deadline'] == 0:
            continue

        if item['block_id'] not in order_data.keys():
            order_data[item['block_id']] = item

        # use the latest
        # 网络状态包含的block_id可能在reward中无记录
        if len(order_data) == len(set(list(redis_reward.keys()) + list(order_data.keys()))):
            break
    # print('clear_single_data', order_data)
    ret = {}

    for key, val in order_data.items():

        #bandwidth
        val['bandwidth'] /= REDIS_DATA_BW_MAX
        #rtt
        val['rtt'] /= REDIS_DATA_RTT_MAX
        #priority
        val['priority'] /= REDIS_DATA_P_MAX
        #remaing_time
        val['remaing_time'] /= val['deadline']
        #send_buf_len
        val['send_buf_len'] /= val['block_size']
        #abc
        action = [val['priority_params'], val['deadline_params'], val['finish_params']]

        if key not in redis_reward.keys():
            continue

        ret[key] = action + [redis_reward[key] - pre_reward[key]] + [val[item] for item in STATES_KEYS]

    # update old reward
    for item in redis_reward.keys():
        pre_reward[item] = redis_reward[item]

    return ret


def gen_next_data(id_list, block_list):

    for idx, block in enumerate(block_list):
        # print("func gen_next_data block id {0} info {1}".format(id_list[idx], block))
        now_dt = clear_single_data(block)

        if now_dt == None:
            print("!!block id {0}, info {1} is useless data".format(id_list[idx], block))
            statis[0] += 1
            continue

        for key, val in now_dt.items():
            # print("ok~~~~")
            if key not in records.keys():
                records[key] = val
                continue

            ret = records[key][-N_STATES:]
            ret = ret + val
            records[key] = val
            # print(len(ret), ret)
            if len(ret) == REDIS_DATA_CIRCLE:

                yield id_list[idx], ret


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
    pre_block=None

    while True:

        # 从redis中获取是否停止训练的信号
        done = env.get_set_item('done')

        if done == 'True':
            print('Ep: ', i_episode,
                  '| Ep_r: ', round(ep_reward, 2))

            break

        latest_block_id_list, latest_block_list = env.get_latest_block_info(pattern='*_ATTEMP-*', size=100)

        if not latest_block_id_list:
            continue

        for latest_block_id, latest_block in gen_next_data(latest_block_id_list, latest_block_list):
            # print(latest_block_id, len(latest_block), REDIS_DATA_CIRCLE)
            if not latest_block_id or len(latest_block) % REDIS_DATA_CIRCLE:
                    # or (pre_block and latest_block_id <= pre_block):
                # redis没完整数据时等待
                print("there is no complete data in redis...")
                continue

            pre_block = latest_block_id if not pre_block else max(latest_block_id, pre_block)

            # 从redis中提取数据
            s = list(map(lambda x: np.float64(x), latest_block[:N_STATES]))
            a = list(map(lambda x: np.float64(x), latest_block[N_STATES: N_STATES+N_ACTIONS]))
            r = np.float64(latest_block[N_STATES+N_ACTIONS])
            s_ = list(map(lambda x: np.float64(x), latest_block[N_STATES+N_ACTIONS+1:]))

            statis[1] += 1
            # print("clear!")
            # print(s, a, r, s_)
            if r > 0:
                print("reward > 0, block id-{0}-".format(latest_block_id))
                #time.sleep(1)

            ddpg.store_transition(s, a, r, s_)

            if ddpg.pointer > MEMORY_CAPACITY:
                var *= .9995  # decay the action randomness
                ddpg.learn()

            # 持久化NN
            if i_episode and i_episode % Iters2Save == 0:
                print("valid data {0}, invalid data {1}, rate {2}".format(statis[1], statis[0], statis[1]/statis[0]))
                file_name = ddpg.save2onnx()
                ddpg.load_onnx(file_name)
                # restart rust
                os.system("echo restart rust")

            # s = s_
            ep_reward += r
            i_episode += 1

            if i_episode and i_episode % MAX_EP_STEPS == 0:
                print('Episode:', i_episode, ' Reward: %i' % int(ep_reward), 'Explore: %.2f' % var, )
                if ep_reward > -300: RENDER = True
                # break

    print('Running time: ', time.time() - t1)