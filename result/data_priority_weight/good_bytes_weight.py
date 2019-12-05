# good bytes: sum of bytes before deadline of all blocks
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

step=0.1 #rtt间隔
weight_num=11 #11种权值
deadline=200 #deadline 200ms
block_num=300 #总共发包量

def sum_good_bytes(f):
    sum=0
    for line in f.readlines():
        arr=line.split()
        good_bytes=arr[1]
        sum+=int(good_bytes)
    return sum

def get_y(y):
    for i in range(weight_num):
        # fpath=path+str(i)
        fpath='./'+'DTP'+'/'+'DTP'+'-priority'+'-'+str(i/10.0)+'.txt'
        f=open(fpath,'r')
        # 文件格式：每一行第一个参数为ID，第二个参数为该block的good bytes，第三个为block完成时间毫秒
        y[i-1]=sum_good_bytes(f)
    return y

x = np.arange(1.0,weight_num+1)
y = np.arange(1.0, weight_num+1)
for i in range(weight_num):
    x[i]=i*step
fig, ax = plt.subplots()
get_y(y)
ax.plot(x,y)

ax.set_title('priority weight low->high')
ax.set_xlabel('priority weight')
ax.set_ylabel('Good Bytes')
ax.legend()
ax.set_xticks(x)
plt.show()