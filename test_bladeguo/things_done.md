# 构建images:

## 构建ubuntu + python3.5
  - sudo docker pull ubuntu:16.04
  - sudo docker run  -dit {Images_id}  获取container_id1
  - sudo docker exec -it {container_id1} /bin/bash

      进入bash 后安装 python3.5
      下载安装包 -> 编译安装：大致命令如下：
      RUN apt-get update && \
      apt-get install -y \
                    wget \
                    xz-utils \
                    build-essential \
                    libsqlite3-dev \
                    libreadline-dev \
                    libssl-dev \
                    openssl
                        
      WORKDIR /tmp
      RUN wget https://www.python.org/ftp/python/3.5.4/Python-3.5.4.tar.xz
      RUN tar -xf Python-3.5.0.tar.xzs
      WORKDIR /tmp/Python-3.5.0
      RUN ./configure
      RUN make
      RUN make install

      WORKDIR /
      RUN rm -rf /tmp/Python-3.5.0.tar.xz /tmp/Python-3.5.0

      RUN pip3 install ipython


  - 保存成镜像
    sudo docker commit -m "added python3.5.4" {container_id1} ubuntu_python

## 构建 ubuntu + python + redis

 - sudo docker run -dit ubuntu_python   #获取container_id2
 - sudo docker run exec {container_id}
 - 进入容器后安装 redis
   具体过程 https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04

 - 保存成镜像
    sudo docker commit -m "add redis2" {container_id2} ubuntu_python_redis
 - 保存到本地
    sudo docker save ubuntu_python_redis > ubuntu_python_redis.tar 

## 上传到docker hub
  - sudo docker tag 36405d7d9008 bladeguo/ubuntu_python_redis:v1.0 # 36405d7d9008 是u_p_r的images_id
 
  - sudo docker login
  
  - sudo docker push bladeguo/ubuntu_python_redis:v1.0    












