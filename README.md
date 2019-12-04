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

> Enter sever container and start the sever(receiver), find your ip with ifconfig
                     
                             docker exec -it {container name/AItrans_server} /bin/bash
                             cd /root/AItrans/
                             ./server {IP} {Port} 
                             
> Enter client container and start the client(sender), find your ip with ifconfig
                     
                             docker exec -it {container name/AItrans_client} /bin/bash
                             cd /root/AItrans/
                             ./client {Server IP} {Port} config/config-DTP.txt

> You will wacth the logging in your cmd.

#### The scheduler document

>@Notice. The logging function will bring overhead for your schedule. so you should close the logging into your console.

```diff
-                            ./server {IP} {Port} 
+                            ./server {IP} {Port} 1> server_result.log 2> server.log
-                            ./client {Server IP} {Port} config/config-DTP.txt
+                            ./client {Server IP} {Port} config/config-DTP.txt 1> client_result.log 2>client.log
```                      
                            
> You can see the server_result.log for your performance.
                            
#### The Traffic document 

#### The debug tools document

![Pandao editor.md](https://pandao.github.io/editor.md/images/logos/editormd-logo-180x180.png "Pandao editor.md")
