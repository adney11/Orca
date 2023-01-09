//============================================================================
// Author      : Adney Cardoza ( adapted from original)
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

char* abr_algo;

int main(int argc, char **argv)
{
    DBGPRINT(DBGSERVER,4,"Main\n");
    if(argc!=15)
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

    
    abr_algo=argv[14];

    start_server(flow_num, client_port);
	DBGMARK(DBGSERVER,0,"DONE!\n");
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
    DBGMARK(0,0,"starting server in orca-server-mahimahi-http\n");
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
        DBGMARK(0,0, "scheme is: %s\n", scheme);
        if (scheme) 
        {   
            DBGMARK(0,0, "trying to set TCP_CONGESTION\n");
            if (setsockopt(sock[i], IPPROTO_TCP, TCP_CONGESTION, scheme, strlen(scheme)) < 0) 
            {
                DBGMARK(0,0,"TCP congestion doesn't exist: %s\n",strerror(errno));
                return;
            } 
        }
    }
    DBGMARK(0,0, "setting container command\n");
    //char trace_path[] = "/newhome/mahimahi_test_traces/";
    /*command = 'mm-delay ' + str(MM_DELAY) + \
					  ' mm-link 12mbps ' + traces + f + ' ' +	\
					  '/usr/bin/python3.6 ' + RUN_SCRIPT + ' ' + ip + ' ' + \
					  abr_algo + ' ' + str(RUN_TIME) + ' ' + \
					  process_id + ' ' + f + ' ' + str(sleep_time)*/
    //char client_cmd[] = "sudo -u `whoami` /users/acardoza/venv/bin/python /newhome/pensieve/real_exp/run_video.py RL 280 99 &";

    // /users/acardoza/venv/bin/python /newhome/Orca/orca_pensieve/pensieve/run_video.py 
    char container_cmd[500];
    DBGMARK(0,0, "initialized container cmd variable\n");
    char python_binary[] = "/users/acardoza/venv/bin/python";
    DBGMARK(0,0, "python binary is: %s\n", python_binary);
    char client_script[] = "/newhome/Orca/orca_pensieve/pensieve/run_video.py";
    DBGMARK(0,0, "client_script is: %s\n", client_script);
    char container_cmd_format_str[] = "sudo -u `whoami` %s %s %s %d %d %s %s";
    DBGMARK(0,0, "container_cmd_format_str: %s\n", container_cmd_format_str);
    char ip[] = "$MAHIMAHI_BASE";
    DBGMARK(0,0, "ip is: %s\n", ip);
    DBGMARK(0,0, "client_port: %d\n", client_port);
    DBGMARK(0,0, "actor_id: %d\n",actor_id);
    DBGMARK(0,0, "log_file: %s\n",log_file);
    DBGMARK(0,0, "abr_algo: %s\n",abr_algo);
    sprintf(container_cmd, container_cmd_format_str, python_binary, client_script, ip, client_port, actor_id, log_file, abr_algo);
    DBGMARK(0,0, "container_cmd: %s\n", container_cmd);
    char cmd[1000];
    DBGMARK(0,0, "initalised cmd\n");
    char final_cmd[1000];
    DBGMARK(0,0, "initalised final_cmd\n");

    if (first_time==4 || first_time==2)
    {
        DBGMARK(0,0, "first time == 4 or 2\n");
        sprintf(cmd, "sudo -u `whoami` mm-delay %d mm-link %s/../traces/%s %s/../traces/%s --downlink-log=%s/log/down-%s --uplink-queue=droptail --uplink-queue-args=\"packets=%d\" --downlink-queue=droptail --downlink-queue-args=\"packets=%d\" -- sh -c \'%s\' &",delay_ms,path,uplink,path,downlink,path,log_file,qsize,qsize,container_cmd);
        DBGMARK(0,0, "cmd is: %s\n", cmd);
    }
    else {
        DBGMARK(0,0, "inside else\n");
        sprintf(cmd, "sudo -u `whoami` mm-delay %d mm-link %s/../traces/%s %s/../traces/%s --uplink-queue=droptail --uplink-queue-args=\"packets=%d\" --downlink-queue=droptail --downlink-queue-args=\"packets=%d\" -- sh -c \'%s\' &",delay_ms,path,uplink,path,downlink,qsize,qsize,container_cmd);
        DBGMARK(0,0, "initalised cmd\n");
    }
    sprintf(final_cmd,"%s",cmd);

    
    info->trace=trace;
    info->num_lines=num_lines;
    /**
     *Setup Shared Memory
     */ 
    key=(key_t) (actor_id*10000+rand()%10000+1);
    key_rl=(key_t) (actor_id*10000+rand()%10000+1);
    // Setup shared memory, 11 is the size
    if ((shmid = shmget(key, shmem_size, IPC_CREAT | 0666)) < 0)
    {
        DBGERROR("Error getting shared memory id");
        return;
    }
        // Attached shared memory
    if ((shared_memory = (char*)shmat(shmid, NULL, 0)) == (char *) -1)
    {
        DBGERROR("Error attaching shared memory id");
        return;
    }
    // Setup shared memory, 11 is the size
    if ((shmid_rl = shmget(key_rl, shmem_size, IPC_CREAT | 0666)) < 0)
    {
        DBGERROR("Error getting shared memory id");
        return;
    }
    // Attached shared memory
    if ((shared_memory_rl = (char*)shmat(shmid_rl, NULL, 0)) == (char *) -1)
    {
        DBGERROR("Error attaching shared memory id");
        return;
    } 
    DBGPRINT(0,0, "Shared memory has been setup\n");
    if (first_time==1){
        sprintf(cmd,"/users/`whoami`/venv/bin/python %s/d5.py --tb_interval=1 --base_path=%s --task=%d --job_name=actor --train_dir=%s --mem_r=%d --mem_w=%d &",path,path,actor_id,path,(int)key,(int)key_rl);
        DBGPRINT(0,0,"Starting RL Module (Without load) ...\n%s",cmd);
    }
    else if (first_time==2 || first_time==4){
        sprintf(cmd,"/users/`whoami`/venv/bin/python %s/d5.py --tb_interval=1 --base_path=%s --load --eval --task=%d --job_name=actor --train_dir=%s  --mem_r=%d --mem_w=%d &",path,path,actor_id,path,(int)key,(int)key_rl);
        DBGPRINT(0,0,"Starting RL Module (No learning) ...\n%s",cmd);
    }
    else
    {
        sprintf(cmd,"/users/`whoami`/venv/bin/python %s/d5.py --load --tb_interval=1 --base_path=%s --task=%d --job_name=actor --train_dir=%s  --mem_r=%d --mem_w=%d &",path,path,actor_id,path,(int)key,(int)key_rl);
        DBGPRINT(0,0,"Starting RL Module (With load) ...\n%s",cmd);
    }
    
    DBGMARK(0,0,"cmd for RL module: %s\n", cmd);
    initial_timestamp();
    system(cmd);
    //Wait to get OK signal (alpha=OK_SIGNAL)
    bool got_ready_signal_from_rl=false;
    int signal;
    char *num;
    char*alpha;
    char *save_ptr;
    int signal_check_counter=0;
    while(!got_ready_signal_from_rl)
    {
        //Get alpha from RL-Module
        signal_check_counter++;
        num=strtok_r(shared_memory_rl," ",&save_ptr);
        alpha=strtok_r(NULL," ",&save_ptr);
        if(num!=NULL && alpha!=NULL)
        {
           signal=atoi(alpha);      
           if(signal==OK_SIGNAL)
           {
              got_ready_signal_from_rl=true;
           }
           else{
               usleep(1000);
           }
        }
        else{
            DBGPRINT(0,0, "Didn't get alpha, trying again\n");
            usleep(10000);
        }
        if (signal_check_counter>18000)
        {
            DBGERROR("After 3 minutes, no response (OK_Signal) from the Actor %d is received! We are going down down down ...\n",actor_id);
            return;
        }   
    }
    DBGPRINT(0,0,"RL Module is Ready. Let's Start ...\n\n");    
    usleep(actor_id*10000+10000);
        
    //Start listen
    int maxfdp=-1;
    fd_set rset; 
    FD_ZERO(&rset);
    //The maximum number of concurrent connections is 1
	for(int i=0;i<FLOW_NUM;i++)
    {
        DBGPRINT(0,0, "Listening for client connection\n");
        listen(sock[i],1);
        //To be used in select() function
        FD_SET(sock[i], &rset); 
        if(sock[i]>maxfdp)
            maxfdp=sock[i];
    }


    // NOTE(ADNEY): connect to compmon here before starting client - this will essentially have lower level connect to compMon first

    int compmon_sockfd;
    struct sockaddr_in compmon_server;
    char compmon_register_msg[] = "Hey! I am your CC component!";

    if ((compmon_sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        DBGPRINT(0,0, "couldn't make compmon socket\n");
        return;
    }
    memset(&compmon_server, 0, sizeof(compmon_server));

    compmon_server.sin_family = AF_INET; 
    compmon_server.sin_port = htons(31337);   // TODO - make this an argument
    compmon_server.sin_addr.s_addr = inet_addr("130.127.133.146");  // TODO - change this to argument later

    sendto(compmon_sockfd, compmon_register_msg, strlen(compmon_register_msg), 0, (sockaddr*)&compmon_server, sizeof(compmon_server));

    //Now its time to start the server-client app and tune C2TCP socket.
    DBGPRINT(0,0, "Starting the container command\n");


    DBGPRINT(0,0,"final_cmd: %s\n",final_cmd);
    system(final_cmd);

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
            DBGPRINT(0,0,"calling accept\n");
            int value=accept(sock[flow_index],(struct sockaddr *)&client_addr[flow_index],(socklen_t*)&sin_size);
            if(value<0)
            {
                perror("accept error\n");
                DBGMARK(0,0,"sockopt: %s\n",strerror(errno));
                DBGMARK(0,0,"sock::%d, index:%d\n",sock[flow_index],flow_index);
                close(sock[flow_index]);
                return;
            }
            DBGPRINT(0,0,"Accepted connection with value: %d, flow_index: %d\n", value, flow_index);
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
                    DBGPRINT(0,0, "Flow index is 0, so we are attempting to start Control and Timer Thread\n");
                    if(pthread_create(&cnt_thread, NULL , CntThread, (void*)info) < 0)
                    {
                        perror("could not create control thread\n");
                        close(sock[flow_index]);
                        return;
                    }
                    if(pthread_create(&timer_thread, NULL , TimerThread, (void*)info) < 0)
                    {
                        perror("could not create timer thread\n");
                        close(sock[flow_index]);
                        return;
                    }

                } else {
                    DBGPRINT(0,0, "Flow index is not 0, so not starting control or timer thread\n");
                }
                
            DBGPRINT(0,0,"Server is Connected to the client...\n");
            flow_index++;
        }
    }
    pthread_join(data_thread, NULL);
}

void* TimerThread(void* information)
{
    DBGPRINT(0,0,"Timer thread started!\n");
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
void* CntThread(void* information)
{
/*    struct sched_param param;
    param.__sched_priority=sched_get_priority_max(SCHED_RR);
    int policy=SCHED_RR;
    int s = pthread_setschedparam(pthread_self(), policy, &param);
    if (s!=0)
    {
        DBGPRINT(0,0,"Cannot set priority (%d) for the Main: %s\n",param.__sched_priority,strerror(errno));
    }

    s = pthread_getschedparam(pthread_self(),&policy,&param);
    if (s!=0)
    {
        DBGPRINT(0,0,"Cannot get priority for the Data thread: %s\n",strerror(errno));
    }
    */
   DBGPRINT(0,0, "Control thread started!\n");
	int ret1;
    double min_rtt_=0.0;
    double pacing_rate=0.0;
    double lost_bytes=0.0;
    double lost_rate=0.0;
    double srtt_ms=0.0;
    double snd_ssthresh=0.0;
    double packets_out=0.0;
    double retrans_out=0.0;
    double max_packets_out=0.0;

	int reuse = 1;
    int pre_id=9230;
    int pre_id_tmp=0;
    int msg_id=657;
    bool got_alpha=false;
    bool slow_start_passed=0;
    for(int i=0;i<FLOW_NUM;i++)
    {
        if (setsockopt(sock_for_cnt[i], IPPROTO_TCP, TCP_NODELAY, &reuse, sizeof(reuse)) < 0)
        {
            DBGMARK(0,0,"ERROR: set TCP_NODELAY option %s\n",strerror(errno));
            return((void *)0);
        }
        //Enable orca on this socket:
        //TCP_ORCA_ENABLE
        int enable_orca=2;
        if (setsockopt(sock_for_cnt[i], IPPROTO_TCP, TCP_ORCA_ENABLE, &enable_orca, sizeof(enable_orca)) < 0) 
        {
            DBGERROR("CHECK KERNEL VERSION (0514+) ;CANNOT ENABLE ORCA %s\n",strerror(errno));
            return ((void* )0);
        } 
    }
    char message[1000];
    char *num;
    char*alpha;
    char*save_ptr;
    int got_no_zero=0;
    uint64_t t0,t1;
    t0=timestamp();
    //Time to start the Logic
    struct tcp_orca_info tcp_info_pre;
    tcp_info_pre.init();
    int get_info_error_counter=0;
    int actor_is_dead_counter=0;
    int tmp_step=0;
    while(send_traffic)  
	{
       for(int i=0;i<flow_index;i++)
       {
           got_no_zero=0;
           usleep(report_period*1000);
           while(!got_no_zero && send_traffic)
           {
                ret1= get_orca_info(sock_for_cnt[i],&orca_info);
                if(ret1<0)
                {
                    DBGMARK(0,0,"setsockopt: for index:%d flow_index:%d TCP_C2TCP ... %s (ret1:%d)\n",i,flow_index,strerror(errno),ret1);
                    return((void *)0);
                }
                if(orca_info.avg_urtt>0)
                {
                    t1=timestamp();
                    
                    double time_delta=(double)(t1-t0)/1000000.0;
                    double delay=(double)orca_info.avg_urtt/1000.0;
                    min_rtt_=(double)(orca_info.min_rtt/1000.0);
                    lost_bytes=(double)(orca_info.lost_bytes);
                    pacing_rate=(double)(orca_info.pacing_rate);
                    lost_rate=lost_bytes/time_delta;   //Rate in MBps
                    srtt_ms=(double)((orca_info.srtt_us>>3)/1000.0);
                    snd_ssthresh=(double)(orca_info.snd_ssthresh);
                    packets_out=(double)(orca_info.packets_out);
                    retrans_out=(double)(orca_info.retrans_out);
                    max_packets_out=(double)(orca_info.max_packets_out);

                    report_period=20;
                    if (!slow_start_passed)
                        //Just for the first Time
                        slow_start_passed=(orca_info.snd_ssthresh<orca_info.cwnd)?1:0;

                    if(!slow_start_passed)
                    {
                        //got_no_zero=1;
                        tcp_info_pre=orca_info;
                        t0=timestamp();

                        target_ratio=1.1*orca_info.cwnd; // NOTE(ADNEY): why are they inflating this by 1.1 ??
                        ret1 = setsockopt(sock_for_cnt[i], IPPROTO_TCP,TCP_CWND, &target_ratio,sizeof(target_ratio));
                        if(ret1<0)
                        {
                           DBGPRINT(0,0,"setsockopt: for index:%d flow_index:%d ... %s (ret1:%d)\n",i,          flow_index,strerror(errno),ret1);
                           return((void *)0);
                        }
                        continue; // NOTE(ADNEY): if in slow start - then don't write message, and inflate cwnd by 1.1 times
                    }
                    sprintf(message,"%d %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f %.7f",
                            msg_id,delay,(double)orca_info.thr,(double)orca_info.cnt,(double)time_delta,
                            (double)target,(double)orca_info.cwnd, pacing_rate,lost_rate,srtt_ms,snd_ssthresh,packets_out
                            ,retrans_out,max_packets_out,(double)orca_info.mss,min_rtt_);
                    memcpy(shared_memory,message,sizeof(message));
                    if ((duration_steps!=0))
                    {
                        step_it++;
                        if(step_it>duration_steps)
                            send_traffic=false;
                    }
                    
                    msg_id=(msg_id+1)%1000;
                    //DBGPRINT(DBGSERVER,0,"%s\n",message);
                    got_no_zero=1;
                    tcp_info_pre=orca_info;
                    t0=timestamp();
                    get_info_error_counter=0;
                }
                else
                {
                    get_info_error_counter++;
                    if(get_info_error_counter>30000)
                    {
                        DBGMARK(0,0,"No valid state for 1 min. We (server of Actor %d) are going down down down ...\n",actor_id);
                        send_traffic=false;
                    }
                    usleep(report_period*100);
                }
           }
        got_alpha=false;
        int error_cnt=0;
        int error2_cnt=0;
        while(!got_alpha && send_traffic)
        { 
           //Get alpha from RL-Module
           num=strtok_r(shared_memory_rl," ",&save_ptr);
           alpha=strtok_r(NULL," ",&save_ptr);
           if(num!=NULL && alpha!=NULL)
           {
               pre_id_tmp=atoi(num);
               target_ratio=atoi(alpha);
               if(pre_id!=pre_id_tmp /*&& target_ratio!=OK_SIGNAL*/)
               {
                  got_alpha=true; 
                  pre_id=pre_id_tmp; 
                  target_ratio=atoi(alpha)*orca_info.cwnd/100;
                  
                  if (target_ratio<MIN_CWND)
                      target_ratio=MIN_CWND;

                  ret1 = setsockopt(sock_for_cnt[i], IPPROTO_TCP,TCP_CWND, &target_ratio, sizeof(target_ratio));
                  if(ret1<0)
                  {
                      DBGPRINT(0,0,"setsockopt: for index:%d flow_index:%d ... %s (ret1:%d)\n",i,flow_index,strerror(errno),ret1);
                      return((void *)0);
                  }
                  error_cnt=0;
               }
               else{
                   if (error_cnt>1000)
                   {
                       DBGPRINT(DBGSERVER,0,"still no new value id:%d prev_id:%d\n",pre_id_tmp,pre_id);
                       error_cnt=0;
                   }
                   error_cnt++;
                   usleep(1000);
               }
               error2_cnt=0;
           }
           else{
                if (error2_cnt==50)
                {
                    DBGPRINT(0,0,"got null values: (downlink:%s delay:%d qs:%d) Actor: %d iteration:%d\n",downlink,delay_ms,qsize,actor_id,step_it);
                    //FIXME:
                    //A Hack for now! Let's send a new state to get new action in case we have missed previous action. Why it happens?!
                    if((1+tmp_step)==(step_it))
                    {
                        actor_is_dead_counter++;
                        tmp_step=step_it;
                        if(actor_is_dead_counter>120)
                        {
                            DBGMARK(0,0,"No valid action for 1 min. We (server of actor %d) are going down down down ...\n",actor_id);
                            send_traffic=false;
                        }
                    }
                    else
                    {
                        actor_is_dead_counter=0;
                        tmp_step=step_it;
                    }
                    got_alpha=true; 
                    error2_cnt=0;
                }
                else{ 
                    error2_cnt++;
                    usleep(10000);
                }
           }
        }
     
       }
    }
    shmdt(shared_memory);
    shmctl(shmid, IPC_RMID, NULL);
    shmdt(shared_memory_rl);
    shmctl(shmid_rl, IPC_RMID, NULL);
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
    DBGPRINT(0,0,"Data Thread Started!\n");
	cFlow* flow = (cFlow*)info;
	int sock_local = flow->flowinfo.sock;
	char* src_ip;
	char write_message[BUFSIZ+1];
	char read_message[1024]={0};
	int len =1;
	char *savePtr;
	char* dst_addr;
	u64 loop;
	u64  remaining_size;

	while ((len = recv(sock_local, read_message, BUFSIZ+1, 0)) > 0) {
        //len = recv(sock_local, read_message, BUFSIZ+1, 0);
        DBGPRINT(0,0,"\nInside recv while loop on server\n");
        if(len<=0)
        {
            DBGMARK(DBGSERVER,1,"recv failed! \n");
            close(sock_local);
            return 0;
        }
        DBGMARK(0,0,"\n --- BEGIN REQUEST ----\n%s\n----- END REQUEST -----\n",read_message);
        // parse request
        HTTPRequestLine* request_line = parse_request(read_message, len);
        // write response
        if (strcmp(request_line->method, "GET") == 0) {
            DBGMARK(0,0, "requesting for resource: %s\n",request_line->resource);
            char* ext = parse_resource_extension(request_line->resource);
            char content_type[100], content_path[100];
            const char* ORCAPEN_SERVER_ROOT_PATH = "/newhome/Orca/orca_pensieve/pensieve/video_server";
            sprintf(content_path, "%s%s", ORCAPEN_SERVER_ROOT_PATH, request_line->resource);
            char status[] = "OK";
            char reply_code = 200;

            if (strcmp(ext, "html") == 0) {
                strcpy(content_type, "text/html");
            } else if (strcmp(ext, "m4s") == 0) {
                strcpy(content_type, "video/iso.segment");
            } else if (strcmp(ext, "js") == 0) {
                strcpy(content_type, "text/javascript");
            } else {
                strcpy(content_type, "application/octet-stream");
            }
            
            int sent = send_response(sock_local, init_HTTPResponse(request_line->http_version,
                reply_code, status, content_type, content_path));

        } else {
            char status[] = "Not Implemented";
            int status_code = 501;
            int sent = send_response(sock_local, init_HTTPResponse(request_line->http_version,
                status_code, status, NULL, NULL));
            DBGMARK(0,0, "unimplemented logic for method: %s\n", request_line->method);
        }
    }
    send_traffic = false;
    DBGMARK(0,0, "Recv While ended, with recv returning value: %d\n", len);
    DBGMARK(0,0,"socket is closed - ending data_thread\n");
	return((void *)0);
}
