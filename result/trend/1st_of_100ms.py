import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

block_num=600 #总共发包量
one_order=int(block_num/3)

x = np.arange(1,one_order+1)
y = np.arange(1,one_order+1)

for i in range(one_order):
    x[i]=i+1
fpath='QUIC-brandwidth-4M-cctest.txt'
f=open(fpath,'r')
for line in f.readlines():
    arr=line.split()
    block_ID=int(arr[0])/4
    block_ID=int(block_ID)
    if block_ID%3==1:
        finished_time=int(arr[2])
        y[int(block_ID/3)]=finished_time

fig, ax = plt.subplots()

ax.set_ylabel('complete time/ms')
ax.set_xlabel('block ID')
ax.set_title('1st block of every 100ms')

ax.plot(x,y,label='1st')
ax.legend()
plt.show()
