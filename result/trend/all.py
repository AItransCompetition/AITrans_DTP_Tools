import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

block_num=600 #总共发包量

x = np.arange(1,block_num+1)
y = np.arange(1,block_num+1)

for i in range(block_num):
    x[i]=i+1
fpath=sys.argv[1]
f=open(fpath,'r')
for line in f.readlines():
    arr=line.split()
    block_ID=int(arr[0])/4
    block_ID=int(block_ID)
    finished_time=int(arr[2])
    y[block_ID-1]=finished_time

fig, ax = plt.subplots()

ax.set_ylabel('complete time/ms')
ax.set_xlabel('block ID')
ax.set_title('all 600 block')

ax.plot(x,y,label='all')
ax.legend()
plt.show()
