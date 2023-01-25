import tensorflow as tf
import numpy as np
import sys

sdim = 7
rec_dim = 1
RECURRENT = True
adim = 1
h1_shape = 256
h2_shape = 256

config = {
    'state_dim': sdim,
    'action_dim': adim,
    'rec_dim': rec_dim,
    'job_name': 'actor',
    'task'    : 0,
    'action_bins': 10
}

class Actor():

    def __init__(self, s_dim, a_dim,h1_shape,h2_shape, action_scale=1.0, name='actor'):
        self.s_dim = s_dim
        if RECURRENT:
            self.s_dim = s_dim * rec_dim
        print(f"Actor: s_dim = {self.s_dim}")
        self.a_dim = a_dim
        self.name = name
        self.action_scale = action_scale
        self.h1_shape = h1_shape
        self.h2_shape = h2_shape
        self.num_action_bins = config['action_bins']
        

    def train_var(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    def build(self, s, is_training):

        with tf.variable_scope(self.name, reuse=tf.AUTO_REUSE):

            h1 = tf.layers.dense(s, units=self.h1_shape, name='fc1')
            h1 = tf.layers.batch_normalization(h1, training=is_training, scale=False)
            h1 = tf.nn.leaky_relu(h1)

            h2 = tf.layers.dense(h1, units=self.h2_shape,  name='fc2')
            h2 = tf.layers.batch_normalization(h2, training=is_training, scale=False)
            h2 = tf.nn.leaky_relu(h2)

            # output = tf.layers.dense(h2, units=self.a_dim, activation=tf.nn.tanh)
            # output = tf.Print(output, [output], "debug: tanh output = ", name='tanhPrint', summarize=5)
            
            # output needs to be one value - want it to be max of softmax, of 5 bins
            # -1, -0.5, 0, 0.5, 1
            num_action_bins = self.num_action_bins
            h3 = tf.layers.dense(h2, units=num_action_bins, name='fc3', activation=tf.nn.softmax)
            argmax = tf.argmax(h3, dimension=1)
            action_bins = tf.constant(np.linspace(-1, 1, num_action_bins).tolist(), name="action_bins")
            #action_bins = tf.constant([-1, -0.5, 0, 0.5, 1])
            # onehot_argmax = tf.one_hot(argmax, depth=5)
            output = tf.gather(action_bins, argmax)
            output = tf.Print(output, [h3, argmax, action_bins, output], "debug:output = ", name='printOutput', summarize=num_action_bins)
            # #scale_output = tf.multiply(output, self.action_scale)
            scale_output = output
        return scale_output
    
def create_input_op_shape(obs, tensor):
    input_shape = [x or -1 for x in tensor.shape.as_list()]
    print(f"create_input_state: input_shape = {input_shape}")
    return np.reshape(obs, input_shape)
    
class Agent():
    def __init__(self, s_dim=sdim, a_dim=adim, action_scale=1.0, h1_shape=h1_shape, h2_shape=h2_shape, action_range=(-1.0,1.0)):
        self.s_dim = s_dim
        self.a_dim = a_dim
        self.h1_shape = h1_shape
        self.h2_shape = h2_shape
        self.action_range = action_range
        self.s0 = tf.placeholder(tf.float32, shape=[None, self.s_dim], name='s0')
        self.is_training = tf.placeholder(tf.bool, name='Actor_is_training')
        print(f"Agent: s_dim = {self.s_dim}")
        self.actor = Actor(self.s_dim, self.a_dim, action_scale=action_scale,h1_shape=self.h1_shape,h2_shape=self.h2_shape)
        
        
        self.actor_out = self.actor.build(self.s0, self.is_training)
        
    def assign_sess(self, sess):
        self.sess = sess
        print("Agent sess assigned")
        
    def get_action(self, s, use_noise=True):
        print(f"get_action: state provided: {s}")
        fd = {self.s0: create_input_op_shape(s, self.s0), self.is_training:False}
        print(f"get_action: fd = {fd}")
        action = self.sess.run([self.actor_out], feed_dict=fd)
        if use_noise:
            noise = np.random.randn(1)#self.actor_noise(action[0])
            action += noise
            action = np.clip(action, self.action_range[0], self.action_range[1])
        return action
    
def hello():
    print(f"hello i am {__name__}")
    
def get_state(s_dim=sdim, random=False):
    if random:
        return np.random.rand(s_dim)
    else:
        return np.zeros(s_dim)
    
def run():
    print("BEGIN")
    print(f"sdim = {sdim}")
    local_job_device = '/job:%s/task:%d' % (config['job_name'], config['task'])
    agent = Agent()
    s_dim = sdim * rec_dim if RECURRENT else sdim
    s0 = get_state(sdim, True)
    s0_rec_buffer = np.zeros([s_dim])
    s1_rec_buffer = np.zeros([s_dim])
    s0_rec_buffer[-1*sdim:] = s0
    evaluation = True
    init_op = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init_op)
        agent.assign_sess(sess)
        if RECURRENT:
            a = agent.get_action(s0_rec_buffer, not evaluation)
        else:
            a = agent.get_action(s0, not evaluation)
        print(f"Raw Action: {a}")
        print(f"Action[0]: {a[0]}")
        a = a[0][0]
        print(f"Got Action: {a}")
        # s = get_state(agent.s_dim, random=True)
        # print(f"Got State: {s}\n with len: {len(s)}")
        # s_rec_buffer = np.concatenate()
    
    
    