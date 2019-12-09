import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import argparse

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

params                = parser.parse_args()
server_ip             = params.ip
port                  = params.port
numbers               = params.numbers
container_server_name = params.server_name
container_client_name = params.client_name

client_run = "#!/bin/bash\n" \
             "cd /root/AItrans\n" \
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

sum = 0
with open('server.log', 'r') as f:
    f.seek(0)
    sum = int(os.popen('wc -l server.log').read().split()[0])

print(sum)
x = np.arange(0,sum)
y0 = np.arange(0, sum)
y1 = np.arange(0, sum)
y2 = np.arange(0, sum)

complete_sum = 0
i = 0
with open('server.log', 'r') as f:
    for line in f.readlines():
        arr = line.split()
        y0[i] = (int(arr[1]) / 200000) * 100
        y1[i] = arr[1]
        y2[i] = arr[2]
        i += 1
        if int(arr[1]) == 200000:
            complete_sum += 1

print("completion rate of all blocks before deadline ：", (complete_sum / sum) * 100, "%")

fig, ax = plt.subplots(1, 3, figsize =(16, 5))
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
ax[0].yaxis.set_major_formatter(yticks)
ax[0].plot(x, y0, color = "yellow")
ax[1].plot(x, y1, color = "blue")
ax[2].plot(x, y2, color = "red")
ax[0].set_title("result0")
ax[1].set_title('result1')
ax[2].set_title("result2")
ax[0].set_xlabel('block_index')
ax[1].set_xlabel('block_index')
ax[2].set_xlabel('block_index')
ax[0].set_ylabel("completed rate")
ax[1].set_ylabel('size') # the completed size before deadline
ax[2].set_ylabel("time") # the time after block used
plt.savefig("./result.png")
plt.show()

# example : sudo python3 start_server_client.py --numbers 45  --ip 172.17.0.2
