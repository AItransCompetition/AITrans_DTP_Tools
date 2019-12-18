

import threading
import os

            
# server 
class Env_server():
    def __init__(self, ip, port, with_log):
        self.with_log = with_log

        if self.with_log:
            self.start_cmd = "./server {} {} 1> server_result.log 2> server.log".format(ip, port)
        else:
            self.start_cmd = "./server {} {}".format(ip, port)
    
    def run(self):
        os.system(self.start_cmd)




# client
class Env_client():
    def __init__(self, ip, port, with_log, config):        
        self.with_log = with_log

        
        if self.with_log:
            self.start_cmd = "./client {} {} {} 1> client_result.log 2>client.log".format(ip, port, config)
        else:
            self.start_cmd = "./client {} {} {}".format(ip, port, config)
        
    
    def run(self):
        os.system(self.start_cmd)


