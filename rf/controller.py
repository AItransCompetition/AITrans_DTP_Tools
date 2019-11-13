#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : controller
# @Function : 
# @Author : azson
# @Time : 2019/11/7 16:16
'''

import os
from redis_py import Redis_py


class Env_rust(object):

    def __init__(self, port=6666):

        ################### rust controler ###################

        self.rust_path = "" # ""/root/junjay/examples-11-9/"
        self.ddpg_path = "" # ""/root/junjay/AITrans_DTP/rf/"
        self.file_model_path = "config/model_path"
        self.order_list = [
            "./server 127.0.0.1 %d > ddpg_server.log & " % (port),
            "./client 127.0.0.1 %d config/config-DTP.txt 0.5 0.5 > ddpg_client.log & " % (port)
        ]

        self.port = port


    def reset(self, redis_cursor, REDIS_DATA_PATTERN):

        print("reset env")

        # reset model_path file

        # reset redis

        # reset log
        with open("reward.log", "w") as f:
            f.write('\n')

        self.restart_rust('output/ddpg_jay.onnx', REDIS_DATA_PATTERN)


    def restart_rust(self, onnx_file, REDIS_DATA_PATTERN):
        '''
        to do
         1. split client(server) start, status check
         2. split model_path change
         3. dont use absolute path
        '''

        def cmd_content(cmd):

            f = os.popen(cmd, "r")
            return f.read()

        if '*' in REDIS_DATA_PATTERN:
            REDIS_DATA_PATTERN = REDIS_DATA_PATTERN[:-1]
        print("restart_rust")
        print(onnx_file, REDIS_DATA_PATTERN)

        os.system("echo restart rust")
        os.system("cp %s %s" % (onnx_file, self.rust_path + "ddpg_jay.onnx"))
        # change file model_path
        print("change model path file")
        with open(self.rust_path + self.file_model_path, "w") as f:
            # f.write(onnx_file+'\n')
            f.write("ddpg_jay.onnx\n")
            f.write(REDIS_DATA_PATTERN+"\n")
            f.write("0.9")

        # kill server
        print("kill server")
        ret = cmd_content("lsof -i:%d" % (self.port))
        if len(ret) >= 9:
            os.system("kill -9 %s" % ret.split()[10])
            print("killed server")

        # kill client
        print("kill client")
        ret = cmd_content('ps -aux | grep "client 127.0.0.1"')

        if 'client 127.0.0.1 %d' % (self.port) in ret:
            p = ret.index('client 127.0.0.1 %d' % (self.port))
            ps = ret[:p].split()[1]
            os.system("kill -9 %s" % ps)
            print("killed client")

        os.system("echo restart rust")
        for od in self.order_list:
            os.system(od)
            print(od)

        print("finish restart")


if __name__ == '__main__':

    obj = Env_rust()
    obj.restart_rust('ddpg_jay.onnx', 'STEP_15735763836267857920_ATTEMP-')