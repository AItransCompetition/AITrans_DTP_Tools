from redis_py import Redis_py
import numpy as np
import re, os, json, threading
from var_dump import var_dump

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
INPUT_DIM = 5

class data_process(object):

    def __init__(self):
        self.redis_con = Redis_py(REDIS_HOST, REDIS_PORT)

    def get_cur_list(self, keys_prefix):

        real_pattern = keys_prefix + "*"
        block_id_list = self.redis_con.rd.keys(pattern=real_pattern)

        if not len(block_id_list):
            return None

        block_id_list = sorted(block_id_list, key=lambda x:int(x.decode('utf8').split('-')[-1]))

        return block_id_list

    def get_unit_info(self, key):

        unit_info = self.redis_con.rd.lrange(key,0,-1)
        if not len(unit_info):
            return None
        return list(map(lambda x: x.decode(), unit_info))
 
    def handle_unit_info(self, unit_list):
       
        result = {}
        state_list = []
        reward_dict = {}
        action = []
        # get the state ,action and reward
        for i in range(len(unit_list)):
           if "ID" not in unit_list[i]:
               temp_dict = json.loads(unit_list[i])
               state_list.append(temp_dict)
           else:
               temp_array = unit_list[i].split(",")
               temp_ID = temp_array[0].split(":")[1]
               temp_reward = temp_array[1].split(":")[1]
               if temp_ID not in reward_dict:
                   reward_dict[temp_ID] = float(temp_reward)
               if reward_dict[temp_ID] < float(temp_reward):
                   reward_dict[temp_ID] = float(temp_reward)
        if len(state_list) == 0 or len(reward_dict) == 0:
            return None
        # handle action
        action.append(state_list[-1]["priority_params"]) 
        action.append(state_list[-1]["deadline_params"]) 
        action.append(state_list[-1]["finish_params"]) 
        # organize
        result['state'] = state_list 
        result['action'] = action 
        result['reward'] = reward_dict 
        return result 

    def organize_state(self,state_list):

        # handle the network situtation
        last_bw   = state_list[-1]['bandwidth'] / 10000.0
        last_rtt  = state_list[-1]['rtt'] / 2000.0
        last_loss = state_list[-1]['loss_rate'] 
        # get the All block id list 
        ID_map = {}
        for i in range(len(state_list)):
           ID_key = state_list[i]['block_id']
           if ID_key not in ID_map and state_list[i]["block_size"] != 0 and state_list[i]["deadline"] != 0:
               ID_map[ID_key]  = state_list[i]
           if ID_key in ID_map and ID_map[ID_key]['remaing_time'] > state_list[i]['remaing_time'] :
               if state_list[i]["block_size"] != 0 and state_list[i]["deadline"] != 0:
                   ID_map[ID_key] = state_list[i] 
        # organize the state
        result = []
        if len(ID_map) < INPUT_DIM:
           for key,value in ID_map.items(): 
               result.append(last_bw) 
               result.append(last_rtt) 
               result.append(last_loss) 
               result.append(value['priority'] / 2.0) 
               result.append(value['remaing_time'] / value['deadline']) 
               result.append(value['send_buf_len'] / value['block_size']) 
           for i in range(len(ID_map), INPUT_DIM):
               result.append(last_bw)
               result.append(last_rtt)
               result.append(last_loss)
               result.append(0.0)
               result.append(0.0)
               result.append(0.0)
        else:
           queue = {}
           res = [[],[],[],[],[]]
           for i in range(INPUT_DIM): 
               remaing_time = 9999999
               mark_key = ""
               for key,value in ID_map.items():
                   if key in queue:
                       continue 
                   else:	  
                       if value["remaing_time"] < remaing_time:
                          res[i] = value
                          remaing_time = value['remaing_time']
                          mark_key = key
               queue[mark_key] = 1
               result.append(last_bw)
               result.append(last_rtt)
               result.append(last_loss)
               result.append(res[i]['priority'] / 2.0)
               result.append(res[i]['remaing_time'] / res[i]['deadline'])
               result.append(res[i]['send_buf_len'] / res[i]['block_size'])
        return np.array(result).reshape((5,6))
		   
         
'''        
dp = data_process();
aa = dp.get_cur_list("STEP_15736661254142179328_ATTEMP")
bb = dp.get_unit_info(aa[4])
cc = dp.handle_unit_info(bb)
dd = dp.organize_state(cc['state'])
print(dd)'''
#var_dump()
