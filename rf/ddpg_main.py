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
N_BLOCKS = 5
a_bound = 1

# redis
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379

REDIS_DATA_CIRCLE=N_STATES*2+N_ACTIONS+1 #s、a、r、s_
REDIS_DATA_P_MAX=2
REDIS_DATA_BW_MAX=10000
REDIS_DATA_RTT_MAX=2000
REDIS_DATA_PATTERN="FIRST_ATTEMP-*"

Iters2Save=1000
Seconds2Save=20.
STATES_KEYS=['bandwidth', 'rtt', 'loss_rate', 'priority', 'remaing_time', 'send_buf_len']

pre_reward = {}
global_sars_=[]
pre_redis_list_id=None

statis=[0, 0]

ATTEMP_NUMS=3


def clear_single_data(raw_data):
    '''
    clear single redis list data
    :param raw_data:
    :return: [[a, r, s] ...], total reward
    '''


    def get_the_best_block(list_data, key_col='remaing_time', topN=5, reverse=False):

        res = sorted(list_data, key=lambda x: float(x[key_col]), reverse=reverse)

        return res[:topN]


    # cal reward
    state_idx=-1
    redis_reward={}
    fir=True
    last_states={}
    log_s_reward = .0

    # cal reward
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

        if now_reward == 0:
            continue

        if id not in pre_reward.keys():
            pre_reward[id] = 0

        # the lastest, the biggest reward
        if id not in redis_reward.keys():
            redis_reward[id] = now_reward
            log_s_reward += redis_reward[id] - pre_reward[id]

    # no state in this list
    if state_idx == -1:
        return None, None

    # cal states
    order_data={}
    fir=True
    ## cal 'bandwidth', 'rtt', 'loss_rate'
    for item in raw_data[-state_idx-1:0:-1]:

        if "ID" in item:
            continue

        item = json.loads(item)

        if item['block_size'] == 0 or item['deadline'] == 0:
            continue

        if item['block_id'] not in order_data.keys():
            order_data[item['block_id']] = item
            # use the latest network states
            if fir:
                last_states['bandwidth'] = item['bandwidth'] / REDIS_DATA_BW_MAX
                last_states['rtt'] = item['rtt'] / REDIS_DATA_RTT_MAX
                last_states['loss_rate'] = item['loss_rate']
                action = [item['priority_params'], item['deadline_params'], item['finish_params']]
                fir = False

    best_blocks = get_the_best_block(list(order_data.values()), topN=N_BLOCKS)
    del order_data

    last_states['priority'] = [0] * N_BLOCKS
    last_states['remaing_time'] = [0] * N_BLOCKS
    last_states['send_buf_len'] = [0] * N_BLOCKS

    for idx, val in enumerate(best_blocks):

        last_states['priority'][idx] = val['priority'] / REDIS_DATA_P_MAX
        last_states['remaing_time'][idx] = val['remaing_time'] / val['deadline']
        if last_states['remaing_time'][idx] < 0:
            print("error data? remain {0}, deadline {1}, ID {2}".format(val['remaing_time'], val['deadline'], val['block_id']))
            # time.sleep(1)
        last_states['send_buf_len'][idx] = val['send_buf_len'] / val['block_size']

        # ret[key] = action + [redis_reward[key] - pre_reward[key]] + [val[item] for item in STATES_KEYS]

    # update old reward
    for item in redis_reward.keys():
        pre_reward[item] = redis_reward[item]

    ret = action + [log_s_reward] + [last_states[item] for item in STATES_KEYS]

    return ret, log_s_reward


def gen_next_data(id_list, block_list):

    global global_sars_

    for idx, block in enumerate(block_list):
        # print("func gen_next_data block id {0} info {1}".format(id_list[idx], block))
        now_ars, s_reward = clear_single_data(block)
        redis_key = id_list[idx]

        if now_ars == None:
            # print("!!block id {0}, info {1} is useless data".format(id_list[idx], block))
            statis[0] += 1
            continue

        if s_reward < 0:
            print(redis_key, s_reward)

        with open("reward.log", "a") as f:
            f.write(str(s_reward))
            f.write("\n")

        global_sars_ = global_sars_[-N_STATES:]
        global_sars_.extend(now_ars)

        if len(global_sars_) == REDIS_DATA_CIRCLE:

            yield id_list[idx], global_sars_


def ddpg_runner():

    global pre_redis_list_id

    env = Redis_py(REDIS_HOST, REDIS_PORT)

    ddpg = DDPG(N_ACTIONS,
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

        real_pattern = REDIS_DATA_PATTERN.replace("FIRST", "STEP_%d" % ATTEMP_NUMS)
        latest_block_id_list, latest_block_list = env.get_latest_block_info(pattern=real_pattern, size=0, pre_block=pre_redis_list_id)

        if not latest_block_id_list or len(latest_block_id_list) == 0:
            print("there is no data with pattern %s in redis" % (real_pattern))
            # restart_rust('ddpg_jay.onnx')
            time.sleep(1)
            continue

        # print("id list {0} pre id {1}".format(latest_block_id_list, pre_redis_list_id))
        pre_redis_list_id = latest_block_list[-1]

        for latest_block_id, latest_block in gen_next_data(latest_block_id_list, latest_block_list):
            # print(latest_block_id, len(latest_block), REDIS_DATA_CIRCLE)
            if not latest_block_id or len(latest_block) % REDIS_DATA_CIRCLE:
                # redis没完整数据时等待
                print("there is no complete data in redis...")
                continue

            # 从redis中提取数据
            s = latest_block[:N_STATES]
            s = s[:3] + s[3] + s[4] + s[5]
            a = latest_block[N_STATES: N_STATES+N_ACTIONS]
            r = [latest_block[N_STATES+N_ACTIONS]]
            s_ = latest_block[-N_STATES:]
            s_ = s_[:3] + s_[3] + s_[4] + s_[5]

            statis[1] += 1

            ddpg.store_transition(s, a, r, s_)

            if ddpg.pointer > MEMORY_CAPACITY:
                var *= .9995  # decay the action randomness
                ddpg.learn()

            ep_reward += r[0]
            i_episode += 1

            if i_episode and i_episode % MAX_EP_STEPS == 0:
                print('Episode:', i_episode, ' Reward: %i' % int(ep_reward), 'Explore: %.2f' % var, )
                if ep_reward > -300: RENDER = True
                # break

        if time.time() - t1 >= Seconds2Save:
            print("i_episode : {0}, it's time to restart!".format(i_episode))
            print("valid data {0}, invalid data {1}, rate {2}".format(statis[1], statis[0], statis[1] / statis[0]))
            t1 = time.time()
            # update redis data
            file_name = ddpg.save2onnx()
            # restart_rust(file_name)
            # leave time for rust
            # time.sleep(5)

    print('Running time: ', time.time() - t1)


if __name__ == '__main__':

    ddpg_runner()