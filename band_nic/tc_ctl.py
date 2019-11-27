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
        bw = float(kwargs['bandwith'])

    os.system('tc qdisc add dev {0} root handle 1:0 tbf rate {1}mbit buffer {2} latency 10ms'.format(nic_name, bw, bw*1100))
    print("changed nic {0}, bandwith to {1}mbit".format(nic_name, bw))

    # delay
    mx_delay_ms = float(kwargs['max_delay'])
    mn_delay_ms = float(kwargs['min_delay'])

    if 'delay' not in kwargs:
        delay_ms = random.random() * (mx_delay_ms - mn_delay_ms) + mn_delay_ms
    else:
        delay_ms = float(kwargs['delay'])

    os.system('tc qdisc add dev {0} parent 1:1 handle 10: netem delay {1}ms'.format(nic_name, delay_ms))
    print("changed nic {0}, delay_time to {1}ms".format(nic_name, delay_ms))


def load_file(**kwargs):

    file_path = kwargs['file_path'] if 'file_path' in kwargs else None

    if not file_path:
        print("please specify the file path that you want load!")
        return

    with open(file_path, 'r') as f:
        # file content pattern :
        # time_stamp,bandwith,delay
        info_list = list(map(lambda x: x.strip().split(','), f.readlines()))
        print(info_list)

    for idx, item in enumerate(info_list):
        kwargs['bandwith'] = item[1]
        kwargs['delay'] = item[2]
        pre_time = time.time()

        if idx:
            sleep_sec = (float(item[0]) - float(info_list[idx-1][0])) - (time.time() - pre_time)
            if sleep_sec > 0:
                time.sleep(sleep_sec)

        tc_easy_bandwith(**kwargs)


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


def helper():
    help_info = '''
    Parameters Explain:
    1. op=load_file file_path=test.txt 
        You can change the bandwith and delay according to the 'test.txt' file
        The 'test.txt' file should be the pattern : "timestamp,bandwith_mbit,delay_ms". Just like below
           1,10,20
           5.2,5.5,10,
           ......
        Then it will use '1' as now timestamp, and changed eth0's bandwith to 10Mbit and delay to 20ms.
        After 4.2s (5.2-1), it changed eth0's bandwith to 5.5Mbit and delay to 10ms.
        
        PS : eth0 is the parameter of nic default value, you can specify like this "nic=eth0"
        
    2. op=show 
        You can get eth0's all queue discplines.
        
    3. op=reset
        You will delete eth0's all queue discplines.
        
    4. op=bw_delay
        You can change the eth0's bandwith and delay per internal ms.
        By default, 
            the bandwith is an random value in [1, 10), you can specify the "min_bw=1" and "max_bw=10" to config;
            the delay is an random value in [0, 100), you can specify the "min_delay=0" and "max_delay=100" to config;
            internal is 5, you can specify "internal=5" to config.
        
    5. internal=-1
        You can change the eth0's bandwith and delay once.
        By default,
            You can specify "bandwith=10" to set bandwith to 10Mbit;
            You can specify "delay=10" to set delay to 10ms.
    '''
    print(help_info)


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

    # change once
    if params['internal'] == "-1":
        if op_type == 'bw_delay':
            tc_easy_bandwith(**params)

    # change bandwith and delay according file
    elif op_type == 'load_file':
        load_file(**params)

    elif op_type == 'reset':
        os.system('tc qdisc del dev {0} root'.format(params['nic']))

    elif op_type == 'show':
        os.system('tc qdisc show dev {0}'.format(params['nic']))

    # change per internal
    elif op_type == 'bw_delay':
        while True:
            if time.time()-pre_time >= internal_sec:
                pre_time=time.time()

                print("time {0}".format(pre_time))
                if op_type == 'bw_delay':
                    tc_easy_bandwith(**params)

                time.sleep(internal_sec)

    else:
        helper()
