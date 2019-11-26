#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : tc_ctl
# @Function : 
# @Author : azson
# @Time : 2019/11/25 14:00
'''

import random
import time, os, sys


def tc_easy_bandwith(**kwargs):

    nic_name = kwargs['nic']
    # bandwith
    mx_bw = float(kwargs['max_bw'])
    mn_bw = float(kwargs['min_bw'])

    # del old qdisc
    os.system('tc qdisc del dev {0} root'.format(nic_name))

    if 'bandwith' not in kwargs:
        # generate bandwith in [mn_bd, mx_bd)
        bw = random.random() * (mx_bw - mn_bw) + mn_bw
    else:
        bw = kwargs['bandwith']

    os.system('tc qdisc add dev {0} root handle 1:0 tbf rate {1}mbit buffer 1600 limit 3000'.format(nic_name, bw))
    print("changed nic {0}, bandwith to {1}mbit".format(nic_name, bw))

    # delay
    mx_delay_ms = float(kwargs['max_delay'])
    mn_delay_ms = float(kwargs['min_delay'])

    if 'delay' not in kwargs:
        delay_ms = random.random() * (mx_delay_ms - mn_delay_ms) + mn_delay_ms
    else:
        delay_ms = kwargs['delay']

    os.system('tc qdisc add dev {0} parent 1:1 handle 10: netem delay {1}ms'.format(nic_name, delay_ms))
    print("changed nic {0}, delay_time to {1}ms".format(nic_name, delay_ms))


def get_params_dict(arg_list):

    # default parameters
    params = {
        "op" : "bw_delay",
        "nic" : "eth0",
        "max_bw" : "10",
        "min_bw" : "1",
        "internal" : "5",

        "max_delay" : "100",
        "min_delay" : "0",
    }

    for item in arg_list:
        tmp = item.split("=")
        if len(tmp) == 2:
            params[tmp[0]]=tmp[1]

    return params


if __name__ == '__main__':
    '''
    order : 
    tc_ctl.py [op_type] [nic_name] [params]...
    like :
    tc_ctl op=bw_delay nic=eth0 max_bw=10 min_bw=1 internal=10 min_delay=0 max_delay=100
    '''
    pre_time = time.time()
    params=get_params_dict(sys.argv[1:])

    internal_sec=float(params['internal'])
    op_type=params['op']

    if params['internal'] == "-1":
        if op_type == 'bw_delay':
            tc_easy_bandwith(**params)

    else:
        while True:
            if time.time()-pre_time >= internal_sec:
                pre_time=time.time()

                print("time {0}".format(pre_time))
                if op_type == 'bw_delay':
                    tc_easy_bandwith(**params)

                time.sleep(internal_sec)
