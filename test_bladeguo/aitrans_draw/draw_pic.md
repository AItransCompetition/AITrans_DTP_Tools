##画图

### 前提要求
  - 本地有两个容器: 假设分别为dtp_server, dtp_client;

### 脚本配置
  - 在dtp_server 里面配置启动server的命令脚本server_run.sh；
  - 在dtp_client 里面配置启动client的命令脚本client_run.sh;
  - server_run.sh 和 client_run.sh 分别放在各自 /root/ 路径下；

### 画图
  - sudo python3 start_server_client.py 可以实现画图；
  - 完成度是计算后打印出来的；
  - 图是关于自定义的index(依次递增)和server_log第二、三列的的折线图。
  - 图中纵坐标的命名可能表达不正确。
  - 图片保存为当前路径下的result.png。