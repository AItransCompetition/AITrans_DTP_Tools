#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <sys/time.h>

#include "common.h"

#include <net/if.h>
void quit()
{                                                                                                                       
        exit(-1);
}               
/* get the current time */
double get_time()
{
    struct timeval tv;
    struct timezone tz;
    double cur_time;
    if (gettimeofday(&tv, &tz) < 0) {  
      perror("get_time() fails, exit\n");
      quit(); 
    }
    cur_time = (double)tv.tv_sec * 1000 + ((double)tv.tv_usec/(double)1000.0);
    return cur_time;
}                        


int main()
{
    int sin_len;
    char message[BUFF_SIZE];
    char buf[BUFF_SIZE];
    int socket_fd, fd;
    struct sockaddr_in sin;
    struct sockaddr_in address;
    printf("Waiting for data from sender\n");
    int err;
    struct timeval send_time, recv_time;
    char *buff_p, *buff_s;
    int pkt_len, i;
    double last_rtime, rtime;
    int ALL_NUM = 500;

    // Initialize socket address structure for Internet Protocols
    // for send
    bzero(&address, sizeof(address)); // empty data structure
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(SEND_IP);
    address.sin_port = htons(SEND_PORT);
    // for receive
    bzero(&sin, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = htonl(INADDR_ANY);
    sin.sin_port = htons(RECV_PORT);
    sin_len = sizeof(sin);

    /* Create a UDP socket for send*/
    fd = socket(AF_INET, SOCK_DGRAM, 0);    
    //Create a UDP socket and bind it to the RECV_PORT
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    //bind(socket_fd, (struct sockaddr *)&sin, sizeof(sin));
    
    //bind nic
    struct ifreq interface;
    //strncpy(interface.ifr_ifrn.ifrn_name, INTERFAXENAME, sizeof(INTERFAXENAME));
    strncpy(interface.ifr_name, RECV_INTERFAXENAME, strlen(RECV_INTERFAXENAME));
    if (setsockopt(socket_fd, SOL_SOCKET, SO_BINDTODEVICE, (char *)&interface, sizeof(interface))  < 0) {
           perror("nic SO_BINDTODEVICE failed");
    }
   bind(socket_fd, (struct sockaddr *)&sin, sizeof(sin));
    //Loop forever (or until a termination message is received)
    // Received data through the socket and process it.The processing in this program is really simple --printing
    int count = 0;
    /*while(1)
    {
        err = recvfrom(socket_fd, message, sizeof(message), 0, (struct sockaddr *)&sin, &sin_len);
        //printf("Response from server : %s err = %d\n", message, err);

        buff_p = message;
        memcpy(&i, buff_p, sizeof(i));
        buff_p += sizeof(i);

        memcpy(&pkt_len, buff_p, sizeof(pkt_len));
        buff_p += sizeof(pkt_len);
        
        if(count==0){
           last_rtime = get_time();
        }else{
           last_rtime = rtime;
        }
        rtime = get_time();
         
        printf("%f %f %d %d %d\n", rtime, rtime - last_rtime, pkt_len, i, 3);
        if(i >= ALL_NUM - 200)
           break;
    }
    count = 0;
    printf("--------------------------start send ---------------------"); 
    for(int i = 0; i<ALL_NUM; i++){

        buff_s = (char *)&buf;
        memcpy(buff_s, &count, sizeof(count));
        buff_s += sizeof(count);
        count++;

        //double rtime_gap = rtime - last_rtime;
        double rtime_gap = 2.32;
        memcpy(buff_s, &rtime_gap, sizeof(rtime_gap));
        buff_s += sizeof(rtime_gap);
         
        err = sendto(fd, buf, sizeof(buf), 0, (struct sockaddr *)&address, sizeof(address));
        printf("%f %f %d %d\n", rtime, rtime_gap, i, 2);
        
    }*/
    // start   
    printf("---------------------- real algorithm ---------------------\n"); 
    count = 0;
    int id = 0;
    int queue_flag = 1000000;
    float queue_delay_ms = 0;
    float bandwidth = 0;
    while(1)
    {
        err = recvfrom(socket_fd, message, sizeof(message), 0, (struct sockaddr *)&sin, &sin_len);
        if(count==0){
           last_rtime = get_time();
        }else{
           last_rtime = rtime;
        }
        rtime = get_time();
        //printf("Response from server : %s err = %d\n", message, err);

        buff_p = message;
        memcpy(&id, buff_p, sizeof(id));
        buff_p += sizeof(id);
        if(count != id){
          continue;
        }

        double rtime_gap = rtime - last_rtime;
        count++;

        /*memcpy(&pkt_len, buff_p, sizeof(pkt_len));
        buff_p += sizeof(pkt_len);
        
        //printf("%f %f %d %d %d\n", rtime, rtime - last_rtime, pkt_len, i, 3);

        buff_s = (char *)&buf;
        memcpy(buff_s, &id, sizeof(id));
        buff_s += sizeof(id);
        count++;

        double rtime_gap = rtime - last_rtime;
        memcpy(buff_s, &rtime_gap, sizeof(rtime_gap));
        buff_s += sizeof(rtime_gap);
        
         
        err = sendto(fd, buf, sizeof(buf), 0, (struct sockaddr *)&address, sizeof(address));*/
 
        queue_delay_ms = (float)queue_flag / 1000.0;
        bandwidth = BUFF_SIZE / queue_delay_ms;
        printf("%f %f %d %d  queue_delay = %f BWE = %f \n", rtime, rtime_gap, id, count,rtime_gap - queue_delay_ms, bandwidth);
        
	char *client_ip = inet_ntoa(sin.sin_addr);
	int client_port = ntohs(sin.sin_port);
	printf("client %s %d\n", client_ip, client_port);
	
	client_ip = inet_ntoa(address.sin_addr);
        client_port = ntohs(address.sin_port);
        printf("server %s %d\n", client_ip, client_port);

	if(count > 1){
           queue_flag = queue_flag / RATIO;
        }
    }  
         
    close(socket_fd);
    close(fd);
    return 0;
}
