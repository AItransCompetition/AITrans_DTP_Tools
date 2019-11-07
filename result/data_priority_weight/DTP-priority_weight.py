import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

step=0.1 #rtt间隔
weight_num=11 #11种权值
deadline=200 #deadline 200ms
block_num=300 #总共发包量

def completion_rate(f):
    sum=0
    for line in f.readlines():
        arr=line.split()
        t=arr[2]
        if float(t)<200:
            sum+=1
    return sum/block_num

def get_y(y):
    for i in range(weight_num):
        fpath='./'+'DTP'+'/'+'DTP'+'-priority'+'-'+str(i/10.0)+'.txt'
        f=open(fpath,'r')
        # 文件格式：每一行第一个参数为ID，第二个参数为该block的good bytes，第三个为block完成时间毫秒
        y[i]=completion_rate(f)
    return y

x = np.arange(1.0,weight_num+1)
y = np.arange(1.0, weight_num+1)
for i in range(weight_num):
    x[i]=i*step
fig, ax = plt.subplots()
get_y(y)
y=y*100 # 为了之后百分比显示
ax.plot(x,y,label='DTP')
# 设置百分比显示
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_title('priority weight low->high')
ax.set_xlabel('priority weight')
ax.set_ylabel('completion rate before deadline')
ax.legend()
ax.set_xticks(x)
plt.show()
