import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import argparse
from tc_ploter import plot_single

# the numbers that you can control
numbers = 60
server_ip = "172.17.0.5"
port = "2222"

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, required=True, help="the ip of container_server_name that required")

parser.add_argument('--port', type=str, default="2222",help="the port of dtp_server that required,default is 2222, and you can randomly choose")

parser.add_argument('--numbers', type=int, default=60, help="the numbers of blocks that you can control")

parser.add_argument('--server_name', type=str, default="dtp_server", help="the container_server_name ")

parser.add_argument('--client_name', type=str, default="dtp_client", help="the container_client_name ")

parser.add_argument('--bw', type=float, default="48", help="bandwith ")

params                = parser.parse_args()
server_ip             = params.ip
port                  = params.port
numbers               = params.numbers
container_server_name = params.server_name
container_client_name = params.client_name
bandwith              = params.bw

tc_sentence = "python3 ../TC/traffic_control.py -once -bw %f -dl 0 \n" % (bandwith)

client_run = "#!/bin/bash\n" \
             "cd /root/AItrans\n" \
             + tc_sentence +    \
             "./client " + server_ip + " " + port + " config/config-DTP.txt " + str(
    numbers) + " 1> client.log 2> client_logging"

server_run = "#!/bin/bash\n" \
             "cd /root/AItrans\n./server " + server_ip + " " + port + " 1> server.log  2> server_logging"

with open("server_run.sh", "w")  as f:
    f.write(server_run)

with open("client_run.sh", "w") as f:
    f.write(client_run)

os.system("sudo docker cp ./server_run.sh " + container_server_name + ":/root/")
os.system("sudo docker cp ./client_run.sh " + container_client_name + ":/root/")
os.system("sudo docker exec -itd " + container_server_name + "  /bin/bash /root/server_run.sh")
os.system("sudo docker exec -it " + container_client_name + "  /bin/bash /root/client_run.sh")
os.system("sudo docker cp " + container_server_name + ":/root/AItrans/server.log .")

stop_server = "#!/bin/bash\n" \
              "ps -ef | grep server_run.sh | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty kill\n"
with open("stop_server.sh", "w")  as f:
    f.write(stop_server)
os.system("sudo docker cp ./stop_server.sh " + container_server_name + ":/root/")
os.system("sudo docker exec -it " + container_server_name + "  /bin/bash /root/stop_server.sh")

plot_single("server.log")