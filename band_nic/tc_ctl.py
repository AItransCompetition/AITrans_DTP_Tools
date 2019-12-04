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
import argparse

help_info = '''
    Examples :
    1. -load test.txt 
        You can change the bandwith and delay according to the 'test.txt' file
        The 'test.txt' file should be the pattern : "timestamp,bandwith_mbit,delay_ms". Just like below
           1,10,20
           5.2,5.5,10,
           ......
        Then it will use '1' as now timestamp, and changed eth0's bandwith to 10Mbit and delay to 20ms.
        After 4.2s (5.2-1), it changed eth0's bandwith to 5.5Mbit and delay to 10ms.

        PS : eth0 is the parameter of nic default value, you can specify like this "-nic eth0"

    2. -o bw_delay
        You can change the eth0's bandwith and delay per internal ms.
        By default, 
            the bandwith is an random value in [1, 10), you can specify the "-mn_bw 1" and "-mx_bw 10" to config;
            the delay is an random value in [0, 100), you can specify the "-mn_dl 0" and "-mx_dl 100" to config;
            internal is 5, you can specify "-i 5" to config.

    3. -once 1
        You can change the eth0's bandwith and delay once.
        By default,
            You can specify "--bandwith 10" to set bandwith to 10Mbit;
            You can specify "--delay 10" to set delay to 10ms.
    '''

def tc_easy_bandwith(**kwargs):

    nic_name = kwargs['nic']
    # bandwith
    mx_bw = float(kwargs['max_bandwith'])
    mn_bw = float(kwargs['min_bandwith'])

    # del old qdisc
    os.system('tc qdisc del dev {0} root'.format(nic_name))

    if not kwargs['bandwith']:
        # generate bandwith in [mn_bd, mx_bd)
        bw = random.random() * (mx_bw - mn_bw) + mn_bw
    else:
        bw = float(kwargs['bandwith'])

    # from the examples : rate 256kbit buffer 1600 latency 11.2ms
    buffer = bw*1100 if not kwargs['buffer'] else float(kwargs['buffer'])
    latency = bw*43.75 if not kwargs['latency'] else float(kwargs['latency'])

    os.system('tc qdisc add dev {0} root handle 1:0 tbf rate {1}mbit buffer {2} latency {3}ms'.format(
                nic_name, bw, buffer, latency))
    print("changed nic {0}, bandwith to {1}mbit".format(nic_name, bw))

    # delay
    mx_delay_ms = float(kwargs['max_delay'])
    mn_delay_ms = float(kwargs['min_delay'])

    if not kwargs['delay']:
        delay_ms = random.random() * (mx_delay_ms - mn_delay_ms) + mn_delay_ms
    else:
        delay_ms = float(kwargs['delay'])

    os.system('tc qdisc add dev {0} parent 1:1 handle 10: netem delay {1}ms'.format(nic_name, delay_ms))
    print("changed nic {0}, delay_time to {1}ms".format(nic_name, delay_ms))


def load_file(**kwargs):

    file_path = kwargs['load_file']

    try:
        with open(file_path, 'r') as f:
            # file content pattern :
            # time_stamp,bandwith,delay
            info_list = list(map(lambda x: x.strip().split(','), f.readlines()))
            # print(info_list)
    except Exception as e:
        print("File path %s is wrong!" % file_path)
        print(e)

    try:
        for idx, item in enumerate(info_list):
            kwargs['bandwith'] = item[1]
            kwargs['delay'] = item[2]
            pre_time = time.time()

            if idx:
                sleep_sec = (float(item[0]) - float(info_list[idx-1][0])) - (time.time() - pre_time)
                if sleep_sec > 0:
                    time.sleep(sleep_sec)

            tc_easy_bandwith(**kwargs)
    except Exception as e:
        print("Please check file %s content is right!" % file_path)
        print(e)


def get_params_dict(arg_list):

    # default parameters
    params = {
        "op" : "help",
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


def init_argparse():

    parser = argparse.ArgumentParser(
        prog="Easy TC Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=help_info)

    parser.add_argument("-o", "--oper",
                        choices=["bw_delay"],
                        default="bw_delay",
                        help="Choose the function you want to do")

    parser.add_argument("-load", "--load_file",
                        metavar="FILE_PATH",
                        help="You can change the bandwith and delay according to a file")

    parser.add_argument("-nic", nargs=1, default="eth0",
                        metavar="ETHERNET",
                        help="Network Interface Controller")

    parser.add_argument("-i", "--internal",
                        type=float,
                        help="The time you want to change the TC rule.")

    # detail parameters
    parser.add_argument("-mx_bw", "--max_bandwith",
                        type=float, default=10,
                        help="For random bandwith")
    parser.add_argument("-mn_bw", "--min_bandwith",
                        type=float, default=1,
                        help="For random bandwith")
    parser.add_argument("-mx_dl", "--max_delay",
                        type=float, default=100,
                        help="For random delay")
    parser.add_argument("-mn_dl", "--min_delay",
                        type=float, default=0,
                        help="For random delay")

    parser.add_argument("-once", "--change_once",
                        metavar="ANY",
                        help="You can change the nic's bandwith and delay once.")

    # detail parameters
    parser.add_argument("-bw", "--bandwith",
                        type=float,
                        help="The value of bandwith you want to change")
    parser.add_argument("-dl", "--delay",
                        type=float,
                        help="The value of delay you want to change")
    parser.add_argument("-bf", "--buffer",
                        type=float,
                        help="The value of buffer size you want to change in tbf")
    parser.add_argument("-lat", "--latency",
                        type=float,
                        help="The value of latency you want to change in tbf")

    parser.add_argument("-r", "--reset",
                        metavar="ETHERNET",
                        help="You will delete eth0's all queue discplines.")

    parser.add_argument("-sh", "--show",
                        metavar="ETHERNET",
                        help="You can get eth0's all queue discplines.")

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')


    return parser

if __name__ == '__main__':

    parser = init_argparse()


    pre_time = time.time()
    params=parser.parse_args()
    params=vars(params)
    # print(params)

    # change once
    if params['change_once']:
        if params['oper'] == 'bw_delay':
            tc_easy_bandwith(**params)

    # change bandwith and delay according file
    elif params['load_file']:
        load_file(**params)

    elif params["reset"]:
        os.system('tc qdisc del dev {0} root'.format(params['reset']))

    elif params["show"]:
        os.system('tc qdisc show dev {0}'.format(params['show']))

    # change per internal
    elif params['internal']:
        while True:
            if time.time()-pre_time >= params['internal']:
                pre_time=time.time()

                print("time {0}".format(pre_time))
                if params['oper'] == 'bw_delay':
                    tc_easy_bandwith(**params)

                time.sleep(params['internal'])
    else:
        parser.print_help()
