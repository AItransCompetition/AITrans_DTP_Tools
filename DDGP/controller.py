import os
import time
from single_env import Env_rust 
from agent import agent

MAX_STEP = 1
step_id_prefix = ""
onnx_file = "ddpg.onnx"

# intial the conifg file
f = open("./config/model_path", "w")
f.write("ddpg_jay.onnx\n")
cur_time = int(float(time.time()) * 100000)
f.write("step_" + str(cur_time) + "_ATTEMP-\n")
f.write("0.9")
f.close()


for step in range(MAX_STEP):
    #read the config
    rust_env = Env_rust("127.0.0.1",6666)
    rust_env.start()
    time.sleep(20)
    rust_env.close_env()
    # read the config
    config_handler = open("./config/model_path")
    lines = config_handler.readlines()
    step_id_prefix = lines[1].strip("\n")
    config_handler.close()
    #start leanring
    print("------step_id_prefix is -----",step_id_prefix)
    agent = agent(step_id_prefix)
    agent.agent_run()

    # cp the onnx model
    os.system("cp output/%s  ./%s" % (step_id_prefix + ".onnx","ddpg.onnx")) 
    # reset the config file
    f = open("./config/model_path", "w")
    f.write("ddpg.onnx\n")
    cur_time = int(float(time.time()) * 100000)
    f.write("step_" + str(cur_time) + "_ATTEMP-\n")
    f.write("0.9")
    
