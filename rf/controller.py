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

    def __init__(self):

        ################### rust controler ###################

        self.rust_path = "/root/junjay/examples-11-9/"
        self.ddpg_path = "/root/junjay/AITrans_DTP/rf/"
        self.file_model_path = "config/model_path"
        self.order_list = [
            self.rust_path + "server 127.0.0.1 6666 > ddpg_server.log >/dev/null 2>&1 & ",
            self.rust_path + "client 127.0.0.1 6666 config/config-DTP.txt 0.5 0.5 >/dev/null 2>&1 & "
        ]


    def reset(self, redis_cursor, REDIS_DATA_PATTERN):

        print("reset env")

        # reset model_path file
        with open(self.rust_path + self.file_model_path, "w") as f:
            f.write("ddpg_jay.onnx\n")
            f.write("STEP_1_ATTEMP-1")

        # reset redis
        if isinstance(redis_cursor, Redis_py):
            redis_cursor.flush_all()

        # reset log
        with open("reward.log", "w") as f:
            f.write('\n')

        self.restart_rust('sss.onnx', REDIS_DATA_PATTERN)


    def restart_rust(self, onnx_file, REDIS_DATA_PATTERN):


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
            f.write(REDIS_DATA_PATTERN)

        # kill server
        print("kill server")
        ret = cmd_content("lsof -i:6666")
        if len(ret) >= 9:
            os.system("kill -9 %s" % ret.split()[10])

        # kill client
        print("kill client")
        ret = cmd_content('ps -aux | grep "client 127.0.0.1"')

        if 'client 127.0.0.1 6666' in ret:
            p = ret.index('client 127.0.0.1 6666')
            ps = ret[:p].split()[1]
            os.system("kill -9 %s" % ps)

        os.system("echo restart rust")
        for od in self.order_list:
            os.system(od)


if __name__ == '__main__':

    print(REDIS_DATA_CIRCLE)
    pass