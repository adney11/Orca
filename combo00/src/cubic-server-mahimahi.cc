//============================================================================
// Author      : Adney Cardoza (adapted from Soheil)
// Version     : 1.0
//============================================================================

/*
  MIT License
  Copyright (c) Soheil Abbasloo 2020 (ab.soheil@gmail.com)

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

#include <cstdlib>
#include <sys/select.h>
#include "define.h"

#include "http_helpers.h"
//#define CHANGE_TARGET 1
#define MAX_CWND 10000
#define MIN_CWND 4

int main(int argc, char **argv)
{
    DBGPRINT(DBGSERVER,4,"Main\n");
    if(argc<15)
	{
        DBGERROR("argc:%d\n",argc);
        for(int i=0;i<argc;i++)
        	DBGERROR("argv[%d]:%s\n",i,argv[i]);
		usage();
		return 0;
	}
    
    srand(raw_timestamp());

	signal(SIGSEGV, handler);   // install our handler
	signal(SIGTERM, handler);   // install our handler
	signal(SIGABRT, handler);   // install our handler
	signal(SIGFPE, handler);   // install our handler
    signal(SIGKILL,handler);   // install our handler
    int flow_num;
	flow_num=FLOW_NUM;
	client_port=atoi(argv[1]);
    path=argv[2];
    target=50;
    target_ratio=1;
    report_period=atoi(argv[3]);
   	first_time=atoi(argv[4]);
    scheme=argv[5];
    actor_id=atoi(argv[6]);
    downlink=argv[7];
    uplink=argv[8];
    delay_ms=atoi(argv[9]);
    log_file=argv[10];
    duration=atoi(argv[11]);
    qsize=atoi(argv[12]);
    duration_steps=atoi(argv[13]);
    char* abr_algo=argv[14];

    start_server(flow_num, client_port);
	DBGMARK(DBGSERVER,5,"DONE!\n");
    shmdt(shared_memory);
    shmctl(shmid, IPC_RMID, NULL);
    shmdt(shared_memory_rl);
    shmctl(shmid_rl, IPC_RMID, NULL);
    return 0;
}

void usage()
{
	DBGMARK(0,0,"./server [port] [path to ddpg.py] [Report Period: 20 msec] [First Time: 1=yes(learn), 0=no(continue learning), 2=evaluate] [actor id=0, 1, ...] [downlink] [uplink] [one-way delay]\n");
}

void start_server(int flow_num, int client_port)
{
	cFlow *flows;
    int num_lines=0;
	sInfo *info;
	info = new sInfo;
	flows = new cFlow[flow_num];
	if(flows==NULL)
	{
		DBGMARK(0,0,"flow generation failed\n");
		return;
	}

	//threads
	pthread_t data_thread;
	pthread_t cnt_thread;
	pthread_t timer_thread;

	//Server address
	struct sockaddr_in server_addr[FLOW_NUM];
	//Client address
	struct sockaddr_in client_addr[FLOW_NUM];
	//Controller address
	//struct sockaddr_in ctr_addr;
    for(int i=0;i<FLOW_NUM;i++)
    {
        memset(&server_addr[i],0,sizeof(server_addr[i]));
        //IP protocol
        server_addr[i].sin_family=AF_INET;
        //Listen on "0.0.0.0" (Any IP address of this host)
        server_addr[i].sin_addr.s_addr=INADDR_ANY;
        //Specify port number
        server_addr[i].sin_port=htons(client_port+i);

        //Init socket
        if((sock[i]=socket(PF_INET,SOCK_STREAM,0))<0)
        {
            DBGMARK(0,0,"sockopt: %s\n",strerror(errno));
            return;
        }

        int reuse = 1;
        if (setsockopt(sock[i], SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse)) < 0)
            perror("setsockopt(SO_REUSEADDR) failed");
        //Bind socket on IP:Port
        if(bind(sock[i],(struct sockaddr *)&server_addr[i],sizeof(struct sockaddr))<0)
        {
            DBGMARK(0,0,"bind error srv_ctr_ip: 000000: %s\n",strerror(errno));
            close(sock[i]);
            return;
        }
        DBGPRINT(0, 0, "server bind: successful\n");
        if (scheme) 
        {
            if (setsockopt(sock[i], IPPROTO_TCP, TCP_CONGESTION, scheme, strlen(scheme)) < 0) 
            {
                DBGMARK(0,0,"TCP congestion doesn't exist: %s\n",strerror(errno));
                return;
            } 
        }
    }

    char container_cmd[500];
    sprintf(container_cmd,"sudo -u `whoami` %s/client $MAHIMAHI_BASE 1 %d",path,client_port);
    char cmd[1000];
    char final_cmd[1000];

    if (first_time==4 || first_time==2)
        sprintf(cmd, "sudo -u `whoami`   mm-delay %d mm-link %s/../traces/%s %s/../traces/%s --downlink-log=%s/log/down-%s --uplink-queue=droptail --uplink-queue-args=\"packets=%d\" --downlink-queue=droptail --downlink-queue-args=\"packets=%d\" -- sh -c \'%s\' &",delay_ms,path,uplink,path,downlink,path,log_file,qsize,qsize,container_cmd);
    else
        sprintf(cmd, "sudo -u `whoami`  mm-delay %d mm-link %s/../traces/%s %s/../traces/%s --uplink-queue=droptail --uplink-queue-args=\"packets=%d\" --downlink-queue=droptail --downlink-queue-args=\"packets=%d\" -- sh -c \'%s\' &",delay_ms,path,uplink,path,downlink,qsize,qsize,container_cmd);
    
    sprintf(final_cmd,"%s",cmd);

    DBGPRINT(DBGSERVER,0,"final_cmd: %s\n",final_cmd);
    info->trace=trace;
    info->num_lines=num_lines;
    initial_timestamp();
    usleep(actor_id*10000+10000);
    //Now its time to start the server-client app and tune C2TCP socket.
    system(final_cmd);
        
    //Start listen
    int maxfdp=-1;
    fd_set rset; 
    FD_ZERO(&rset);
    //The maximum number of concurrent connections is 1
	for(int i=0;i<FLOW_NUM;i++)
    {
        listen(sock[i],1);
        //To be used in select() function
        FD_SET(sock[i], &rset); 
        if(sock[i]>maxfdp)
            maxfdp=sock[i];
    }

    //Timeout {1Hour} if something goes wrong! (Maybe  mahimahi error...!)
    maxfdp=maxfdp+1;
    struct timeval timeout;
    timeout.tv_sec  = 60 * 60;
    timeout.tv_usec = 0;
    int rc = select(maxfdp, &rset, NULL, NULL, &timeout);
    /**********************************************************/
    /* Check to see if the select call failed.                */
    /**********************************************************/
    if (rc < 0)
    {
        DBGERROR("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=- select() failed =-=-=-=-=-=--=-=-=-=-=\n");
        return;
    }
    /**********************************************************/
    /* Check to see if the time out expired.                  */
    /**********************************************************/
    if (rc == 0)
    {
        DBGERROR("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=- select() Timeout! =-=-=-=-=-=--=-=-=-=-=\n");
        return;
    }

	int sin_size=sizeof(struct sockaddr_in);
	while(flow_index<flow_num)
	{
        if (FD_ISSET(sock[flow_index], &rset)) 
        {
            int value=accept(sock[flow_index],(struct sockaddr *)&client_addr[flow_index],(socklen_t*)&sin_size);
            if(value<0)
            {
                perror("accept error\n");
                DBGMARK(0,0,"sockopt: %s\n",strerror(errno));
                DBGMARK(0,0,"sock::%d, index:%d\n",sock[flow_index],flow_index);
                close(sock[flow_index]);
                return;
            }
            sock_for_cnt[flow_index]=value;
            flows[flow_index].flowinfo.sock=value;
            flows[flow_index].dst_addr=client_addr[flow_index];
            if(pthread_create(&data_thread, NULL , DataThread, (void*)&flows[flow_index]) < 0)
            {
                perror("could not create thread\n");
                close(sock[flow_index]);
                return;
            }
                      
                if (flow_index==0)
                {
                    if(pthread_create(&timer_thread, NULL , TimerThread, (void*)info) < 0)
                    {
                        perror("could not create timer thread\n");
                        close(sock[flow_index]);
                        return;
                    }
                }
                
            DBGPRINT(0,0,"ID: [%d] Server is Connected to the client...\n", actor_id);
            flow_index++;
        }
    }
    pthread_join(data_thread, NULL);
}

void* TimerThread(void* information)
{
    uint64_t start=timestamp();
    unsigned int elapsed; 
    if ((duration!=0))
    {
        while(send_traffic)
        {
            sleep(1);
            elapsed=(unsigned int)((timestamp()-start)/1000000);      //unit s
            if (elapsed>duration)    
            {
                send_traffic=false;
            }
        }
    }

    return((void *)0);
}

void* DataThread(void* info)
{
    // NOTE(ADNEY): edit this to behave like an HTTP server
    /*
	struct sched_param param;
    param.__sched_priority=sched_get_priority_max(SCHED_RR);
    int policy=SCHED_RR;
    int s = pthread_setschedparam(pthread_self(), policy, &param);
    if (s!=0)
    {
        DBGERROR("Cannot set priority (%d) for the Main: %s\n",param.__sched_priority,strerror(errno));
    }

    s = pthread_getschedparam(pthread_self(),&policy,&param);
    if (s!=0)
    {
        DBGERROR("Cannot get priority for the Data thread: %s\n",strerror(errno));
    }*/
    //pthread_t send_msg_thread;

    // manage flow id for local flow state

	cFlow* flow = (cFlow*)info;
	int sock_local = flow->flowinfo.sock;
	char* src_ip;
	char write_message[BUFSIZ+1];
	char read_message[1024]={0};
	int len;
	char *savePtr;
	char* dst_addr;
	u64 loop;
	u64  remaining_size;

	memset(write_message,1,BUFSIZ);
	write_message[BUFSIZ]='\0';
	/**
	 * Get the RQ from client : {src_add} {flowid} {size} {dst_add}
	 */
	len=recv(sock_local,read_message,1024,0);
	if(len<=0)
	{
		DBGMARK(DBGSERVER,1,"recv failed! \n");
		close(sock_local);
		return 0;
	}
	/**
	 * For Now: we send the src IP in the RQ to!
	 */
	src_ip=strtok_r(read_message," ",&savePtr);
	if(src_ip==NULL)
	{
		//discard message:
		DBGMARK(DBGSERVER,1,"id: %d discarding this message:%s \n",flow->flowinfo.flowid,savePtr);
		close(sock_local);
		return 0;
	}
	char * isstr = strtok_r(NULL," ",&savePtr);
	if(isstr==NULL)
	{
		//discard message:
		DBGMARK(DBGSERVER,1,"id: %d discarding this message:%s \n",flow->flowinfo.flowid,savePtr);
		close(sock_local);
		return 0;
	}
	flow->flowinfo.flowid=atoi(isstr);
	char* size_=strtok_r(NULL," ",&savePtr);
	flow->flowinfo.size=1024*atoi(size_);
    DBGPRINT(DBGSERVER,4,"%s\n",size_);
	dst_addr=strtok_r(NULL," ",&savePtr);
	if(dst_addr==NULL)
	{
		//discard message:
		DBGMARK(DBGSERVER,1,"id: %d discarding this message:%s \n",flow->flowinfo.flowid,savePtr);
		close(sock_local);
		return 0;
	}
	char* time_s_=strtok_r(NULL," ",&savePtr);
    char *endptr;
    start_of_client=strtoimax(time_s_,&endptr,10);
	got_message=1;
    DBGPRINT(DBGSERVER,2,"Got message: %" PRIu64 " us\n",timestamp());
    flow->flowinfo.rem_size=flow->flowinfo.size;
    DBGPRINT(DBGSERVER,2,"time_rcv:%" PRIu64 " get:%s\n",start_of_client,time_s_);

	//Get detailed address
	strtok_r(src_ip,".",&savePtr);
	if(dst_addr==NULL)
	{
		//discard message:
		DBGMARK(DBGSERVER,1,"id: %d discarding this message:%s \n",flow->flowinfo.flowid,savePtr);
		close(sock_local);
		return 0;
	}

	//Calculate loops. In each loop, we can send BUFSIZ (8192) bytes of data
	loop=flow->flowinfo.size/BUFSIZ*1024;
	//Calculate remaining size to be sent
	remaining_size=flow->flowinfo.size*1024-loop*BUFSIZ;
	//Send data with 8192 bytes each loop
	DBGPRINT(0,0,"Server is sending the traffic ...\n");

   // for(u64 i=0;i<loop;i++)
	while(send_traffic)
    {
		len=strlen(write_message);
		while(len>0)
		{
			DBGMARK(DBGSERVER,5,"++++++\n");
			len-=send(sock_local,write_message,strlen(write_message),0);
		    usleep(50);         
            DBGMARK(DBGSERVER,5,"------\n");
		}
        usleep(100);
	}
	flow->flowinfo.rem_size=0;
    done=true;
    DBGPRINT(DBGSERVER,1,"done=true\n");
    close(sock_local);
    DBGPRINT(DBGSERVER,1,"done\n");
	return((void *)0);
}
