import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

step=2 #带宽间隔
brandwidth_num=5 #假设测5种带宽
deadline=200 #deadline 200ms
block_num=300 #总共发包量
def completion_rate(f):
    sum=0
    for line in f.readlines():
        arr=line.split()
        t=arr[1]
        if float(t)<200:
            sum+=1
    return sum/block_num
def get_y(case,y):
    for i in range(1,brandwidth_num+1):
        fpath='data/'+case+'/'+case+'-brandwidth'+'-'+str(12-i*2)+'M.txt'
        f=open(fpath,'r')
        # 文件格式：每一行第一个参数为ID，第二个参数为离发出的ms
        y[i-1]=completion_rate(f)
        if i==5:
            print(case+" of 2M: "+str(y[i-1]))
    return y

x = np.arange(1,brandwidth_num+1)
y = np.arange(1.0, brandwidth_num+1)
for i in range(brandwidth_num):
    x[i]=(brandwidth_num-i)*step
fig, ax = plt.subplots()
case=['DTP','QUIC','Deadline','Priority']
for i in range(4):
    get_y(case[i],y)
    y=y*100 # 为了之后百分比显示
    

