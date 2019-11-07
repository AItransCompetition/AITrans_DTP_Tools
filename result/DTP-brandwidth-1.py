import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

step=2 #带宽间隔
brandwidth_num=5 #假设测5种带宽
deadline=200 #deadline 200ms
block_num=600 #总共发包量
def completion_rate(f):
    sum=0
    for line in f.readlines():
        arr=line.split()
        t=arr[2]
        if float(t)<200:
            sum+=1
    return sum/block_num
def get_y(case,y):
    for i in range(1,brandwidth_num+1):
        # fpath=path+str(i)
        fpath='data/'+case+'/'+case+'-brandwidth'+'-'+str(12-i*2)+'M.txt'
        f=open(fpath,'r')
        # 文件格式：每一行第一个参数为ID，第三个参数为离发出的ms
        y[i-1]=completion_rate(f)
    return y

x = np.arange(1,brandwidth_num+1)
y = np.arange(1.0, brandwidth_num+1)
for i in range(brandwidth_num):
    x[i]=(brandwidth_num-i)*step
fig, ax = plt.subplots()
case=['DTP','QUIC','Deadline','Priority']
path=['data/DTP/DTP-brandwidth','data/QUIC/QUIC-brandwidth','data/Deadline/Deadline-brandwidth','data/Priority/Priority-brandwidth']
for i in range(4):
    get_y(case[i],y)
    y=y*100 # 为了之后百分比显示
    ax.plot(x,y,label=case[i])
# 设置百分比显示
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_title('Brandwidth high->low')
ax.set_xlabel('Brandwidth/Mbps')
ax.set_ylabel('completion rate before deadline')
ax.legend()
ax.set_xticks(x)
plt.gca().invert_xaxis()
plt.show()

