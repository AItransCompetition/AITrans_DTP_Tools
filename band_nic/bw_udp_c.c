#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <time.h>
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
    int fd, socket_fd;
    int i = 0, j = 0;
    char buf[BUFF_SIZE], message[BUFF_SIZE];
    int sin_len;
    struct sockaddr_in address;
    struct sockaddr_in sin;
    int err;
    double send_time;
    double last_send_time;
    char *buff_p, *buff_s;
    int pkt_len;
    int ALL_NUM = 500;
    /* Initialize socket address structure for Interner Protocols */
    // for send
    bzero(&address, sizeof(address)); // empty data structure
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(RECV_IP);
    address.sin_port = htons(RECV_PORT);

    // for receive
    bzero(&sin, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = htonl(INADDR_ANY);
    sin.sin_port = htons(SEND_PORT);
    sin_len = sizeof(sin);

    /* Create a UDP socket */
    fd = socket(AF_INET, SOCK_DGRAM, 0);    
    //Create a UDP socket and bind it to the RECV_PORT
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    bind(socket_fd, (struct sockaddr *)&sin, sizeof(sin));
   
   //bind nic
    struct ifreq interface;
    strncpy(interface.ifr_ifrn.ifrn_name, INTERFAXENAME, sizeof(INTERFAXENAME));
    //strncpy(interface.ifr_name, INTERFAXENAME, strlen(INTERFAXENAME));
    if (setsockopt(fd, SOL_SOCKET, SO_BINDTODEVICE, (char *)&interface, sizeof(interface))  < 0) {
           perror("nic SO_BINDTODEVICE failed");
    }

    //Loop 20 times (a nice round number ) sending data
    int count = 0;
    /*for (i = 0; i  < ALL_NUM; i++) {

        buff_p = (char *)&buf;
        memcpy(buff_p, &count, sizeof(count));
        buff_p += sizeof(count);
        count++;

        pkt_len = sizeof(buf);
        memcpy(buff_p, &pkt_len, sizeof(pkt_len));
        buff_p += sizeof(pkt_len);

 
        if(i == 0){
            last_send_time = get_time();
        }else{
            last_send_time = send_time;
        }
        send_time = get_time();

        err = sendto(fd, buf, sizeof(buf), 0, (struct sockaddr *)&address, sizeof(address));
        printf("i = %d, size = %d send_time_gap = %f \n ", i, err, send_time - last_send_time);
    }*/
    count = 0;
    printf("-----------------------start receive ---------------------------\n");
    /*while(1){
        double diff;
        err = recvfrom(socket_fd, message, sizeof(message), 0, (struct sockaddr *)&sin, &sin_len);
        buff_s = message;
        memcpy(&i, buff_s, sizeof(i));
        buff_s += sizeof(i);

        memcpy(&diff, buff_s, sizeof(diff));
        buff_s += sizeof(diff); 

        printf("%f %d %d\n", diff, i, count); 
        count++;
        if(i >= ALL_NUM - 50)
           break;
    }*/ 
    // the preview start to solve the netem issue
    printf("-----------------------start receive ---------------------------\n");
    int id = 0, id_rec = 0;
    int sleep_unit = 1000000;
    for (i = 0; i  < 10; i++) {

        buff_p = (char *)&buf;
        memcpy(buff_p, &id, sizeof(id));
        buff_p += sizeof(id);

        pkt_len = sizeof(buf);
        memcpy(buff_p, &pkt_len, sizeof(pkt_len));
        buff_p += sizeof(pkt_len);

        if(i == 0){
            last_send_time = get_time();
        }else{
            last_send_time = send_time;
        }
        send_time = get_time();

        err = sendto(fd, buf, sizeof(buf), 0, (struct sockaddr *)&address, sizeof(address));
        //printf("i = %d, size = %d send_time_gap = %f \n ", i, err, send_time - last_send_time);

        /*double diff;
        err = recvfrom(socket_fd, message, sizeof(message), 0, (struct sockaddr *)&sin, &sin_len);
        buff_s = message;
        memcpy(&id_rec, buff_s, sizeof(id_rec));
        buff_s += sizeof(id_rec);

        memcpy(&diff, buff_s, sizeof(diff));
        buff_s += sizeof(diff); */
      
        usleep(sleep_unit);
        printf("i = %d, size = %d , sleep = %d send_gap = %f \n", i, err,sleep_unit, send_time - last_send_time);
        sleep_unit = sleep_unit/RATIO;
        //printf("id = %d, id_rec = %d,  size = %d send_time_gap = %f receive_time_gap = %f, queue_delay = %f \n", id, id_rec , err, send_time - last_send_time, diff, diff - (send_time - last_send_time));

        id++;
	printf("error: %d\n", err);
        //printf("%f %d %d\n", diff, i, count); 
    }
    
    /* send a termination message */
    sprintf(buf, "stop\n");
    //err = sendto(fd, buf, sizeof(buf), 0, (struct sockaddr *)&address, sizeof(address)); 
    printf("i = %d, size = %d\n", i, err);
   
    close (fd);
    close(socket_fd);
    printf("Message Sent, Terminating\n");
    return 0;
}
