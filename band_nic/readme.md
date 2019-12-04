Tc_ctl  readeMe.md

## Introduce

The tc_ctl.py main functions is based on the **tc** order in linux. And its argument parser is based on the **argparse** in python library. All of the functions was tested in the python3.x .

So, if you want to run this script, making sure there are tc n your os or docker container and argparser library in python packages. For tc, we have prepared the docker container with the ubuntu 16.04 for you. For argparse, just pip it ! Like :

> pip install argparse

After above, just input 

> python3 tc_ctl.py --show eth0

This order will out all the queue discipline on the NIC eth0. If there are none error about tc or argparser, congratulations to you ! Now, You can use it to do more things.

## Function Examples

- Change both of the bandwith and delay on a NIC according to a file.

  Suppose there is a file named "test.txt".And it's content is below :

  > 1,23,10
  >
  > 5,10,20
  >
  > 15,7,23
  >
  > 30,100.213,23.34
  

For the above data, you can see it as an csv file. 

For the first columns, it means the timestamp; The second columns means the bandwith (Mb) ; And the last is delay (ms).

Then you can input below :

> python3 tc_ctl.py -load test.txt
  > 

For the ouput, it will regard the "1" as the nowtime and change the NIC eth0's bandwith to 23Mbit and delay time to 10ms.

After 4s (5-1=4), it will change the NIC eth0's bandwith to 10Mbit and delay time to 20ms.

……

In the last,  the NIC eth0's bandwith will be 100.213Mbit and delay time will be 23.34ms.

By default, the script will operate on the NIC eth0. And you can specify another NIC by "-nic", like "-nic eth0".

- Show all the queue disciplines on a NIC.

  If you want to show all the queue disciplines on the NIC eth0, you can input below :

  > python3 tc_ctl.py -sh eth0
  > 

  If you run the script according to the steps above, the NIC eth0's bandwith will be 100.213Mbit and delay time will be 23.34ms. So, the ouput now is like below :

  > qdisc tbf 1: root refcnt 3 rate 100213Kbit burst 110222b lat 4.4s
  >
  > qdisc netem 10: parent 1:1 limit 1000 delay 23.3ms

  The output involes the knowledge about tc order in linux. So, we recommend you to [Click me!](https://www.badunetworks.com/traffic-shaping-with-tc/)

   if you want to learn more.

- Delete all the queue disciplines on a NIC.

  If you want to delete all the queue disciplines on the NIC eth0, you can input below :

  >  python3 tc_ctl.py -r eth0
  >  

  If the output is nothing or "RTNETLINK answers: No such file or directory", it means there is no queue disciplines on the NIC eth0 now.

## Tips

All of above functions are enough for you in the competitions . For more detail about parameters, just run

> python3 tc_ctl.py -h
> 