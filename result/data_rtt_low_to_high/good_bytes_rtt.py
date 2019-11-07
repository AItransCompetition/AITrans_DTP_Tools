# good bytes: sum of bytes before deadline of all blocks
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

step=40 #rtt间隔
rtt_num=5 #假设测5种rtt
deadline=200 #deadline 200ms
block_num=600 #总共发包量

def sum_good_bytes(f):
    sum=0
    for line in f.readlines():
        arr=line.split()
        good_bytes=arr[1]
        sum+=int(good_bytes)
    return sum

def get_y(case,y):
    for i in range(1,rtt_num+1):
        # fpath=path+str(i)
        fpath='./'+case+'/'+case+'-rtt'+'-'+str(40*i-40)+'ms.txt'
        f=open(fpath,'r')
        # 文件格式：每一行第一个参数为ID，第二个参数为该block的good bytes，第三个为block完成时间毫秒
        y[i-1]=sum_good_bytes(f)
    return y

x = np.arange(1,rtt_num+1)
y = np.arange(1.0, rtt_num+1)
for i in range(rtt_num):
    x[i]=i*step
fig, ax = plt.subplots()
case=['DTP','QUIC','Deadline','Priority']
for i in range(4):
    get_y(case[i],y)
    ax.plot(x,y,label=case[i])

ax.set_title('rtt low->high')
ax.set_xlabel('rtt/ms')
ax.set_ylabel('Good Bytes')
ax.legend()
ax.set_xticks(x)
plt.show()

