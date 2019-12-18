# AITrans DTP Competition

**The Second AItrans Competition**

![AItrans](http://i1.fuimg.com/520739/2fb6d0b37df98506.jpg "AItrans")

The AItrans competition 's topic is Dealine Awared Transport portocol(DTP), DTP is a new transport protocol for low latency  application like VR,RTC and online games,which is based on [QUIC](https://www.chromium.org/quic) protocol.md”

# DTP basic info

* The DTP basic info website is in [DTP](https://www.aitrans.online/)

* The DTP basic info slides is in [PPT]()

* The DTP basic paper is in [APNET18](https://dl.acm.org/citation.cfm?id=3343191)

## Competition Documents

#### The Architecuture of competition

#### Download the environment

> The DTP basic environment is based on [Docker](https://hub.docker.com).  The document for using docker is [中文教程](https://www.runoob.com/docker/docker-tutorial.html)（Chinese）.[Docker Document](https://docs.docker.com/get-started/)（English）

> The DTP is developed by [RUST](https://www.rust-lang.org/),which can support the cross platform like Linux,Android,IOS.


                             docker pull y654125664/aitrans:2.0  
                             
```diff
+ For the second AItrans competiton, we recommend use the ubuntu to participate.
```

> Download the images, which images provided 
  * The DTP sender and receiver
  * The Traffic control shell
  * The DTP logging function
  * The DTP debug tools
  * The Net tools like ifconfig
#### Start the container

> Start a sender(client) and a server(receiver) container

                   docker run --privileged -dit --name {container name/AItrans_client} y654125664/aitrans:2.0
                   docker run --privileged -dit --name {container name/AItrans_server} y654125664/aitrans:2.0
                             
#### Quick Start with DTP
#### This is the demo code of reiforcement learning

> Enter sever container and start the sever(receiver), find your ip with ifconfig
                     
                             docker exec -it {container name/AItrans_server} /bin/bash
                             cd /root/AItrans/
                             git clone -b rl_demo https://github.com/NGnetLab/AITrans_DTP.git
                             cd AITrans_DTP/
                             cp *.py ../
                             cd ..
                             python3 controller.py server {IP} {Port}

                             
> Enter client container and start the client(sender), find your ip with ifconfig
                     
                             docker exec -it {container name/AItrans_client} /bin/bash
                             cd /root/AItrans/
                             git clone -b rl_demo https://github.com/NGnetLab/AITrans_DTP.git
                             cd AITrans_DTP/
                             cp *.py ../
                             cd ..
                             python3 controller.py client {IP} {Port} -c config/config-DTP.txt

> You will wacth the logging in your cmd.

#### The scheduler document

>@Notice. The logging function will bring overhead for your schedule. so you should close the logging into your console.

```diff
-                            python3 controller.py server {IP} {Port} 
+                            python3 controller.py server {IP} {Port} --log
-                            python3 controller.py client {Server IP} {Port} -c config/config-DTP.txt
+                            python3 controller.py client {Server IP} {Port} -c config/config-DTP.txt --log
```                      
                            
> You can see the server_result.log for your performance.
                            
#### Specification

> You can change the learning algorithm in ``` user_func.py ```.

> Function ``` get_action(state, model) ``` will return the action to DTP system.



![Pandao editor.md](https://pandao.github.io/editor.md/images/logos/editormd-logo-180x180.png "Pandao editor.md")
