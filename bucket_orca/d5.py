'''
MIT License
Copyright (c) Chen-Yu Yen - Soheil Abbasloo 2020

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
'''

from utils import logger, get_my_logger, Params, get_data_file
from common import DIRNAME
import threading
import logging
logging.basicConfig(filename=f"/newhome/Orca/{DIRNAME}/logs/d5.log", level=logging.DEBUG)
LOG = logging.getLogger(__name__)
action_logger = get_my_logger("action_logger", f"/newhome/Orca/{DIRNAME}/logs/actions.log", log_fmt="%(message)s")
ood_logger = None
import tensorflow as tf
import sys
from agent import Agent
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import argparse
import gym
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import time
import random
import datetime
import sysv_ipc
import signal
import pickle
from envwrapper import Env_Wrapper, TCP_Env_Wrapper, GYM_Env_Wrapper

import scipy as sp

#action_file = get_data_file("/newhome/Orca/orca_pensieve/data/actions.data")


softmax_logger = None

def create_input_op_shape(obs, tensor):
    input_shape = [x or -1 for x in tensor.shape.as_list()]
    return np.reshape(obs, input_shape)


def action_after_ood_decision(action, action_range, max_trained_softmax_value):
    # expecting a list of 2 values 
    # [0] - actual action
    # [1] - action confidence - this is the softmax prob
    THRESHOLD = 0.1
    DEFAULT_ACTION = 0
    OOD_MARKER = 2
    backup_action = action
    action = action[0]
    #ood_logger.debug(f"action supplied: {action}, type: {type(action)}")
    a_dim = int(action.size)
    #ood_logger.debug(f"action_range supplied: {action_range}, recieved action_dim: {a_dim}")
    actual_actions = np.linspace(action_range[0], action_range[1], a_dim).tolist()
    #ood_logger.debug(f"actual actions: {actual_actions}")
    # do softmax here
    # compare softmax value with max_softmax to 
    # ONGOING: MAYBE: some mapping between softmax value to[0,1]
    #softmax_values = tf.nn.softmax(action)

    #ood_logger.debug(f"action supplied: {action}, type: {type(action)}")
    softmax_values = sp.special.softmax(action)
    #ood_logger.debug(f"softmax values: {softmax_values}")
    action_max_sftmx_value = np.max(softmax_values)
    action_softmax_argmax = np.argmax(softmax_values)
    #ood_logger.debug(f"max softmax from values: {action_max_sftmx_value} stored at index: {action_softmax_argmax}")
    softmax_logger.debug(action_max_sftmx_value)
    #ood_logger.debug(f"actual_actions has max index of {len(actual_actions)-1}")
    actual_action = actual_actions[action_softmax_argmax]
    action_confidence = action_max_sftmx_value
    
    # confidence_diff = max_trained_softmax_value - action_confidence
    # if confidence_diff > 0:
    #     ratio = confidence_diff / max_trained_softmax_value
    #     if ratio < THRESHOLD:
    #         actual_action = DEFAULT_ACTION
    #         action_confidence = OOD_MARKER
    # else:
    #     ood_logger.debug(f"^ACTION CONFIDENCE HIGHER THAN MAX OF TRAINED SET^")
    #ood_logger.debug(f"{actual_action}, {action_confidence}")
    #return [actual_action]
    action_confidence = 1
    ood_logger.debug(f"{backup_action[0][0]}, {action_confidence}")
    return [backup_action[0][0]]
    

def evaluate_TCP(env, agent, epoch, summary_writer, params, s0_rec_buffer, eval_step_counter):


    score_list = []

    eval_times = 1
    eval_length = params.dict['max_eps_steps']
    start_time = time.time()
    for _ in range(eval_times):

        step_counter = 0
        ep_r = 0.0

        if not params.dict['use_TCP']:
            s0 = env.reset()

        if params.dict['recurrent']:
            a = agent.get_action(s0_rec_buffer, False)
        else:
            a = agent.get_action(s0, False)
        a = a[0][0]
        LOG.debug(f"evaluate_TCP: got action: {a}")
        
        # do ood stuff here - or write function to do ood stuff

        env.write_action(a)

        while True:

            eval_step_counter += 1
            step_counter += 1

            s1, r, terminal, error_code = env.step(a, eval_=True)

            if error_code == True:
                s1_rec_buffer = np.concatenate( (s0_rec_buffer[params.dict['state_dim']:], s1) )

                if params.dict['recurrent']:
                    a1 = agent.get_action(s1_rec_buffer, False)
                else:
                    a1 = agent.get_action(s1, False)

                a1 = a1[0][0]
                #actual_action = action_after_ood_decision(a1, agent.action_range, agent.max_trained_softmax_value)
                #LOG.debug(f"evaluate_TCP: got action: {a1}")
                env.write_action(a1)
                #env.write_action(actual_action[0])

            else:
                print("Invalid state received...\n")
                env.write_action(a)
                #env.write_action(actual_action[0])
                continue

            ep_r = ep_r+r


            if (step_counter+1) % params.dict['tb_interval'] == 0:

                summary = tf.summary.Summary()
                summary.value.add(tag='Eval/Step/0-Actions', simple_value=env.map_action(a))
                #summary.value.add(tag='Eval/Step/0-Actions', simple_value=env.map_action(old_actual_action))
                summary.value.add(tag='Eval/Step/2-Reward', simple_value=r)
            summary_writer.add_summary(summary, eval_step_counter)

            s0 = s1
            a = a1
            #old_actual_action = actual_action[0]
            if params.dict['recurrent']:
                s0_rec_buffer = s1_rec_buffer


            if step_counter == eval_length or terminal:
                score_list.append(ep_r)
                break

    summary = tf.summary.Summary()
    summary.value.add(tag='Eval/Return', simple_value=np.mean(score_list))
    summary_writer.add_summary(summary, epoch)

    return eval_step_counter



class learner_killer():

    def __init__(self, buffer):

        self.replay_buf = buffer
        print("learner register sigterm")
        signal.signal(signal.SIGTERM, self.handler_term)
        print("test length:", self.replay_buf.length_buf)
    def handler_term(self, signum, frame):
        if not config.eval:
            with open(os.path.join(params.dict['train_dir'], "replay_memory.pkl"), "wb") as fp:
                pickle.dump(self.replay_buf, fp, protocol=pickle.HIGHEST_PROTOCOL)
                print("test length:", self.replay_buf.length_buf)
                print("--------------------------Learner: Saving rp memory--------------------------")
        print("-----------------------Learner's killed---------------------")
        sys.exit(0)


def main():

    tf.get_logger().setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--load', action='store_true', default=False, help='default is  %(default)s')
    parser.add_argument('--eval', action='store_true', default=False, help='default is  %(default)s')
    parser.add_argument('--tb_interval', type=int, default=1)
    parser.add_argument('--train_dir', type=str, default=None)
    parser.add_argument('--mem_r', type=int, default = 123456)
    parser.add_argument('--mem_w', type=int, default = 12345)
    parser.add_argument('--base_path',type=str, required=True)
    parser.add_argument('--job_name', type=str, choices=['learner', 'actor'], required=True, help='Job name: either {\'learner\', actor}')
    parser.add_argument('--task', type=int, required=True, help='Task id')


    ## parameters from parser
    global config
    global params
    config = parser.parse_args()

    logfilename=f"{config.job_name}{config.task}"
    logging.basicConfig(filename=f'/newhome/Orca/{DIRNAME}/logs/{logfilename}-d5_py.log', level=logging.DEBUG)
    global LOG
    global ood_logger
    
    ood_logger = get_my_logger(f"ood_logger-{config.task}", f"/newhome/Orca/{DIRNAME}/logs/ood-{config.task}.log", log_fmt="%(message)s")
    ## parameters from file
    params = Params(os.path.join(config.base_path,'params.json'))

    global softmax_logger
    softmax_logger = get_my_logger(f"softmax_logger_{config.job_name}-{config.task}", f"/newhome/Orca/{DIRNAME}/logs/softmax_values_{config.job_name}-{config.task}.log", log_fmt="%(message)s")

    if params.dict['single_actor_eval']:
        local_job_device = ''
        shared_job_device = ''
        def is_actor_fn(i): return True
        global_variable_device = '/cpu'
        is_learner = False
        server = tf.train.Server.create_local_server()
        filters = []
    else:

        local_job_device = '/job:%s/task:%d' % (config.job_name, config.task)
        shared_job_device = '/job:learner/task:0'

        is_learner = config.job_name == 'learner'

        global_variable_device = shared_job_device + '/cpu'


        def is_actor_fn(i): return config.job_name == 'actor' and i == config.task


        if params.dict['remote']:
            cluster = tf.train.ClusterSpec({
                'actor': params.dict['actor_ip'][:params.dict['num_actors']],
                'learner': [params.dict['learner_ip']]
            })
        else:
            cluster = tf.train.ClusterSpec({
                    'actor': ['localhost:%d' % (8001 + i) for i in range(params.dict['num_actors'])],
                    'learner': ['localhost:8000']
                })


        server = tf.train.Server(cluster, job_name=config.job_name,
                                task_index=config.task)
        filters = [shared_job_device, local_job_device]



    if params.dict['use_TCP']:
        env_str = "TCP"
        env_peek = TCP_Env_Wrapper(env_str, params,use_normalizer=params.dict['use_normalizer'])

    else:
        env_str = 'YourEnvironment'
        env_peek =  Env_Wrapper(env_str)



    s_dim, a_dim = env_peek.get_dims_info()
    action_scale, action_range = env_peek.get_action_info()

    if not params.dict['use_TCP']:
        params.dict['state_dim'] = s_dim
    if params.dict['recurrent']:
        s_dim = s_dim * params.dict['rec_dim']


    if params.dict['use_hard_target'] == True:
        params.dict['tau'] = 1.0


    with tf.Graph().as_default(),\
        tf.device(local_job_device + '/cpu'):

        tf.set_random_seed(1234)
        random.seed(1234)
        np.random.seed(1234)

        actor_op = []
        now = datetime.datetime.now()
        tfeventdir = os.path.join( config.base_path, params.dict['logdir'], config.job_name+str(config.task) )
        params.dict['train_dir'] = tfeventdir

        if not os.path.exists(tfeventdir):
            os.makedirs(tfeventdir)
        summary_writer = tf.summary.FileWriterCache.get(tfeventdir)
        LOG.debug(f"tfeventdir/summary location: {tfeventdir}")

        with tf.device(shared_job_device):

            agent = Agent(s_dim, a_dim, actual_a_dim=params.dict['actual_action_dim'], batch_size=params.dict['batch_size'], summary=summary_writer,h1_shape=params.dict['h1_shape'],
                        h2_shape=params.dict['h2_shape'],stddev=params.dict['stddev'],mem_size=params.dict['memsize'],gamma=params.dict['gamma'],
                        lr_c=params.dict['lr_c'],lr_a=params.dict['lr_a'],tau=params.dict['tau'],PER=params.dict['PER'],CDQ=params.dict['CDQ'],
                        LOSS_TYPE=params.dict['LOSS_TYPE'],noise_type=params.dict['noise_type'],noise_exp=params.dict['noise_exp'], max_softmax_val=params.dict['max_trained_softmax_value'])

            dtypes = [tf.float32, tf.float32, tf.float32, tf.float32, tf.float32]
            shapes = [[s_dim], [a_dim], [1], [s_dim], [1]]
            queue = tf.FIFOQueue(10000, dtypes, shapes, shared_name="rp_buf")


        if is_learner:
            with tf.device(params.dict['device']):
                agent.build_learn()

                agent.create_tf_summary()

            if config.load is True and config.eval==False:
                if os.path.isfile(os.path.join(params.dict['train_dir'], "replay_memory.pkl")):
                    with open(os.path.join(params.dict['train_dir'], "replay_memory.pkl"), 'rb') as fp:
                        replay_memory = pickle.load(fp)

            _killsignal = learner_killer(agent.rp_buffer)


        for i in range(params.dict['num_actors']):
                if is_actor_fn(i):
                    if params.dict['use_TCP']:
                        shrmem_r = sysv_ipc.SharedMemory(config.mem_r)
                        shrmem_w = sysv_ipc.SharedMemory(config.mem_w)
                        env = TCP_Env_Wrapper(env_str, params, config=config, for_init_only=False, shrmem_r=shrmem_r, shrmem_w=shrmem_w,use_normalizer=params.dict['use_normalizer'])
                    else:
                        env = GYM_Env_Wrapper(env_str, params)

                    a_s0 = tf.placeholder(tf.float32, shape=[s_dim], name='a_s0')
                    a_action = tf.placeholder(tf.float32, shape=[a_dim], name='a_action')
                    a_reward = tf.placeholder(tf.float32, shape=[1], name='a_reward')
                    a_s1 = tf.placeholder(tf.float32, shape=[s_dim], name='a_s1')
                    a_terminal = tf.placeholder(tf.float32, shape=[1], name='a_terminal')
                    a_buf = [a_s0, a_action, a_reward, a_s1, a_terminal]


                    with tf.device(shared_job_device):
                        actor_op.append(queue.enqueue(a_buf))

        if is_learner:
            Dequeue_Length = params.dict['dequeue_length']
            dequeue = queue.dequeue_many(Dequeue_Length)

        queuesize_op = queue.size()

        if params.dict['ckptdir'] is not None:
            params.dict['ckptdir'] = os.path.join( config.base_path, params.dict['ckptdir'])
            print("## checkpoint dir:", params.dict['ckptdir'])
            isckpt = os.path.isfile(os.path.join(params.dict['ckptdir'], 'checkpoint') )
            print("## checkpoint exists?:", isckpt)
            if isckpt== False:
                print("\n# # # # # # Warning ! ! ! No checkpoint is loaded, use random model! ! ! # # # # # #\n")
        else:
            params.dict['ckptdir'] = tfeventdir

        tfconfig = tf.ConfigProto(allow_soft_placement=True)
        # saving hooks


        if params.dict['single_actor_eval']:
            mon_sess = tf.train.SingularMonitoredSession(
                checkpoint_dir=params.dict['ckptdir'])
        else:
            scaffold = tf.train.Scaffold(saver=tf.train.Saver(keep_checkpoint_every_n_hours=0.5))
            LOG.debug(f"creating mon_sess")
            mon_sess = tf.train.MonitoredTrainingSession(master=server.target,
                    save_checkpoint_secs=15,
                    save_summaries_secs=None,
                    save_summaries_steps=None,
                    is_chief=is_learner,
                    checkpoint_dir=params.dict['ckptdir'],
                    scaffold=scaffold,
                    config=tfconfig,
                    hooks=None)
            LOG.debug("created mon_sess - assigning to agent")
        agent.assign_sess(mon_sess)
        LOG.debug("assigned mon_sess to agent")

        if is_learner:
            print("I am the learner and i am ready")
            if config.eval is True:
                print("=========================Learner is up===================")
                while not mon_sess.should_stop():
                    time.sleep(1)
                    continue

            if config.load is False:
                agent.init_target()

            counter = 0
            start = time.time()

            LOG.debug("starting learner dequeue thread")
            dequeue_thread = threading.Thread(target=learner_dequeue_thread, args=(agent,params, mon_sess, dequeue, queuesize_op, Dequeue_Length),daemon=True)
            first_time=True

            while not mon_sess.should_stop():

                if first_time == True:
                    dequeue_thread.start()
                    first_time=False

                up_del_tmp=params.dict['update_delay']/1000.0
                time.sleep(up_del_tmp)
                LOG.debug(f"counter: {counter}")
                if agent.rp_buffer.ptr>200 or agent.rp_buffer.full :
                    LOG.debug("running learner train step")
                    agent.train_step()
                    if params.dict['use_hard_target'] == False:
                        agent.target_update()

                        if counter %params.dict['hard_target'] == 0 :
                            current_opt_step = agent.sess.run(agent.global_step)
                            logger.info("Optimize step:{}".format(current_opt_step))
                            logger.info("rp_buffer ptr:{}".format(agent.rp_buffer.ptr))

                    else:
                        if counter %params.dict['hard_target'] == 0 :

                            agent.target_update()
                            current_opt_step = agent.sess.run(agent.global_step)
                            logger.info("Optimize step:{}".format(current_opt_step))
                            logger.info("rp_buffer ptr:{}".format(agent.rp_buffer.ptr))

                counter += 1
                


        else:
                start = time.time()
                step_counter = np.int64(0)
                eval_step_counter = np.int64(0)
                s0 = env.reset()
                s0_rec_buffer = np.zeros([s_dim])
                s1_rec_buffer = np.zeros([s_dim])
                s0_rec_buffer[-1*params.dict['state_dim']:] = s0


                if params.dict['recurrent']:
                    a = agent.get_action(s0_rec_buffer,not config.eval)
                else:
                    a = agent.get_action(s0, not config.eval)
                a = a[0][0]
                #actual_action = action_after_ood_decision(a, agent.action_range, agent.max_trained_softmax_value)
                LOG.debug(f"actor: got action: {a}")
                #env.write_action(actual_action[0])
                env.write_action(a)
                epoch = 0
                ep_r = 0.0
                start = time.time()
                while True:
                    start = time.time()
                    epoch += 1

                    step_counter += 1
                    s1, r, terminal, error_code = env.step(a,eval_=config.eval)
                    # LOG action and new state TODO(ADNEY)
                    #state_action_logger.info(f"epoch: {epoch}\naction: {a}\ngave state: {s1}\nwhere samples/cwnd is at index 3")

                    if error_code == True:
                        s1_rec_buffer = np.concatenate( (s0_rec_buffer[params.dict['state_dim']:], s1) )

                        if params.dict['recurrent']:
                            a1 = agent.get_action(s1_rec_buffer, not config.eval)
                        else:
                            a1 = agent.get_action(s1,not config.eval)

                        a1 = a1[0][0]
                        #actual_action = action_after_ood_decision(a1, agent.action_range, agent.max_trained_softmax_value)
                        LOG.debug(f"actor: got action: {a1}")
                        #action_logger.debug(a1)
                        #action_file.write(f"{a1}\n")

                        env.write_action(a1)
                        #env.write_action(actual_action[0])

                    else:
                        print("TaskID:"+str(config.task)+"Invalid state received...\n")
                        #env.write_action(actual_action[0])
                        env.write_action(a)
                        continue

                    if params.dict['recurrent']:
                        fd = {a_s0:s0_rec_buffer, a_action:create_input_op_shape(a, a_action), a_reward:np.array([r]), a_s1:s1_rec_buffer, a_terminal:np.array([terminal], np.float)}
                    else:
                        fd = {a_s0:s0, a_action:create_input_op_shape(a, a_action), a_reward:np.array([r]), a_s1:s1, a_terminal:np.array([terminal], np.float)}

                    if not config.eval:
                        mon_sess.run(actor_op, feed_dict=fd)

                    s0 = s1
                    a = a1
                    if params.dict['recurrent']:
                        s0_rec_buffer = s1_rec_buffer

                    if not params.dict['use_TCP'] and (terminal):
                        if agent.actor_noise != None:
                            agent.actor_noise.reset()

                    if (epoch% params.dict['eval_frequency'] == 0):
                        eval_step_counter = evaluate_TCP(env, agent, epoch, summary_writer, params, s0_rec_buffer, eval_step_counter)


                print("total time:", time.time()-start)

def learner_dequeue_thread(agent,params, mon_sess, dequeue, queuesize_op, Dequeue_Length):
    ct = 0
    while True:
        ct = ct + 1
        data = mon_sess.run(dequeue)
        agent.store_many_experience(data[0], data[1], data[2], data[3], data[4], Dequeue_Length)
        time.sleep(0.01)


def learner_update_thread(agent,params):
    delay=params.dict['update_delay']/1000.0
    ct = 0
    while True:
        agent.train_step()
        agent.target_update()
        time.sleep(delay)


if __name__ == "__main__":
    main()


# /users/`whoami`/venv/bin/python orca_pensieve/d5.py --tb_interval=1 --base_path=orca_pensieve --load --eval --task=0 --job_name=actor --train_dir=orca_pensieve  --mem_r=%d --mem_w=%d