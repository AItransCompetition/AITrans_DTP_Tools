import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

deadline=200
fig, ax = plt.subplots()
case=['DTP','QUIC','Deadline','Priority']
x = np.arange(1.0,21.0,1.0)
y = np.arange(1.0,21.0,1.0)
for c in case:
    fpath=c+'/'+c+'-square-wave.txt'
    f=open(fpath,'r')
    Block = [999 for n in range(600)]
    # 文件格式：每一行第一个参数为ID，第三个参数为离发出的ms
    for line in f.readlines():
        arr=line.split()
        block_id=int(arr[0])
        block_num=int(block_id/4-1)
        t=int(arr[2])
        Block[block_num]=t

    sum=0
    block_num=0
    i=0
    for block_num in range(600):
        if Block[block_num]<=200:
            sum+=1
        # 30 blocks each sec
        if (block_num+1)%30==0:
            y[i]=sum/30.0
            i+=1
            sum=0
    y=y*100 # 为了之后百分比显示
    ax.plot(x,y,label=c)


x1 = np.linspace(0,20,1000)
y1 = np.linspace(0,0,1000)
y2 = np.linspace(0,0,1000)
for i in range(x1.size):
    if (x1[i]+1)%10<5:
        y1[i]=180
        if (x1[i]-1)%5<0.02:
            plt.text(x1[i],y1[i]+1,"12MB/s",fontsize=12)
    else:
        y1[i]=60
        if x1[i]%5<0.02:
            plt.text(x1[i],y1[i]+1,"4MB/s",fontsize=12)

ax.fill_between(x1,y1,y2,color='b',where=y1>y2,interpolate=True,alpha=0.1)
# 设置百分比显示
fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
yticks = mtick.FormatStrFormatter(fmt)
ax.yaxis.set_major_formatter(yticks)
ax.set_title('Brandwidth Square Wave')
ax.set_xlabel('Time/s')
ax.set_ylabel('completion rate(each sec)')
plt.xlim(0)
plt.ylim(0)
ax.legend()
ax.set_xticks(x)
plt.show()






