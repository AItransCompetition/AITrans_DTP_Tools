#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : controller
# @Function : 
# @Author : Dan Yang
# @Time : 2019/11/14
'''

import os
import time

class Env_rust(object):

    def __init__(self, ip="127.0.0.1", port=6666):

        ################### rust controler ###################

        '''self.rust_path = "" # ""/root/junjay/examples-11-9/"
        self.ddpg_path = "" # ""/root/junjay/AITrans_DTP/rf/"
        self.file_model_path = "config/model_path"
        self.order_list = [
            "./server 127.0.0.1 %d > ddpg_server.log & " % (port),
            "./client 127.0.0.1 %d config/config-DTP.txt 0.5 0.5 > ddpg_client.log & " % (port)
        ]'''
        self.ip = ip
        self.port = port

    def start(self):

        #os.system("./server %s %d > ddpg_server.log 2>&1 & " % (self.ip , self.port))
        os.system("./server %s %d > ddpg_server.log  & " % (self.ip , self.port))
        os.system("./client %s %d config/config-DTP.txt 0.5 0.5 > ddpg_client.log & " % (self.ip , self.port))
    
    def close_env(self):
        # kill server
        print("kill server")
        ret = os.popen("lsof -i:%d" % (self.port)).read()
        if len(ret) >= 9:
            os.system("kill -9 %s" % ret.split()[10])
        # kill client
        print("kill client")

        ret = os.popen('ps -aux | grep "client %s"' % (self.ip)).read()
        if 'client %s %d' % (self.ip, self.port) in ret:
            p = ret.index('client %s %d' % (self.ip, self.port))
            ps = ret[:p].split()[1]
            os.system("kill -9 %s" % ps) 

if __name__ == '__main__':

    obj = Env_rust("127.0.0.1",6666)
    obj.start()
    time.sleep(5)
    obj.close_env()
