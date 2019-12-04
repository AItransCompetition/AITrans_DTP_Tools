import os
import matplotlib.pyplot as plt
import numpy as np
os.system("sudo docker exec -it dtp_server /bin/bash /root/server_run.sh")
os.system("sudo docker exec -it dtp_client /bin/bash /root/client_run.sh")
os.system("sudo docker cp dtp_server:/root/AItrans/server.log .")

sum = 0
with open('server.log', 'r') as f:
    f.seek(0)
    sum = int(os.popen('wc -l server.log').read().split()[0])

x = np.arange(1,sum)
y1 = np.arange(1, sum)
y2 = np.arange(1, sum)
complete_sum = 0
i = 0
with open('server.log', 'r') as f:
    next(f)
    for line in f.readlines():
        arr = line.split()
        y1[i] = arr[1]
        y2[i] = arr[2]
        i += 1
        if int(arr[1]) == 200000:
            complete_sum += 1

# print(complete_sum)
# print(x)
# print(y)
print("completion rate before deadline ：", (complete_sum / (sum - 1)) * 100, "%")

fig, ax = plt.subplots(1, 2, figsize =(12, 5))
ax[0].plot(x, y1, color = "blue")
ax[1].plot(x, y2, color = "red")
ax[0].set_title('result')
ax[1].set_title("result")
ax[0].set_xlabel('index')
ax[1].set_xlabel('index')
ax[0].set_ylabel('send_buff')
ax[1].set_ylabel("remaining time")
plt.savefig("./result.png")
plt.show()




