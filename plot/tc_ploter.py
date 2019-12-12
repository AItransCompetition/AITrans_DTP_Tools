#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : main
# @Function : 
# @Author : azson
# @Time : 2019/12/11 16:05
'''


import matplotlib.pyplot as plt
import numpy as np


trace='''
0,30,0.001
5,20,0.001
10,15,0.001
15,10,0.001
20,9,0.001
25,7,0.001
30,5,0.001
'''

all_data=\
'''
54706251.0 36163.0
58890790.0 30886.0
50113687.0 49247.0
46183921.0 52063.0
53579838.0 40297.0
57300562.0 33404.0
57699271.0 32248.0
56407610.0 35794.0
58910260.0 30574.0
57684335.0 31517.0
58833039.0 31124.0
57742535.0 33808.0
'''

tc='python3 ../TC/traffic_control.py -once 1 -bw 25 -dl 0.001 -bf 24897388'

def plot_all():

    x_data = [25., 20., 15, 10, 8, 6, 4, 2, 0.5, 0.1, 0.01, 0.0001]
    arr1 = list(map(lambda x: x.split(' '), all_data.strip().split('\n')))
    arr = np.array(arr1, dtype=np.float64)
    print(arr)
    ax = plt.subplot(2, 2, 1)
    ax.plot(np.arange(arr.shape[0]), arr[:, 0])
    ax.set_xlabel('Different bandwith')
    ax.set_ylabel('All block size')

    ax = plt.subplot(2, 2, 2)
    ax.scatter(np.arange(arr.shape[0]), arr[:, 0], s=3, color='r')
    ax.set_xlabel('Different bandwith')
    ax.set_ylabel('All block size')

    ax = plt.subplot(2, 2, 3)
    ax.plot(np.arange(arr.shape[0]), arr[:, 1])
    ax.set_xlabel('Different bandwith')
    ax.set_ylabel('All cost time')

    ax = plt.subplot(2, 2, 4)
    ax.scatter(np.arange(arr.shape[0]), arr[:, 1], s=3, color='r')
    ax.set_xlabel('Different bandwith')
    ax.set_ylabel('All cost time')
    plt.show()


def plot_single(file=None, suffix="tmp", saveFig=False):

    if not file:
        file = "server_result-%s.log" % (suffix)

    with open(file, "r") as f:
        raw_data = f.readlines()
        list_data = list(map(lambda x:x.split(' '), raw_data))

    arr = np.array(list_data, dtype=float)

    height, width = 2, 2

    plt.figure(figsize=(10, 5))

    ax = plt.subplot(height, width, 1)
    ax.plot(np.arange(arr.shape[0]), arr[:, 1])
    ax.set_xlabel('Time')
    ax.set_ylabel('Send block size')

    ax = plt.subplot(height, width, 2)
    ax.scatter(np.arange(arr.shape[0]), arr[:, 1], s=3, color='r')
    ax.set_xlabel('Time')
    ax.set_ylabel('Send block size')

    ax = plt.subplot(height, width, 3)
    ax.plot(np.arange(arr.shape[0]), arr[:, 2])
    ax.set_xlabel('Time')
    ax.set_ylabel('Cost time')

    ax = plt.subplot(height, width, 4)
    ax.scatter(np.arange(arr.shape[0]), arr[:, 2], s=3, color='r')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cost time')

    print("block size {0}, cost time {1}".format(arr[:, 1].sum(), arr[:, 2].sum()))
    print("低于200K的block 错过200ms的block")
    print("{0} {1}".format(sum(arr[:, 1] < 200000), sum(arr[:, 2] > 200)))

    if saveFig:
        plt.savefig("server_result-%s.jpg" % (suffix))
    plt.show()

if __name__ == '__main__':

    plot_single()



