import numpy as np
from random import random
import tensorflow as tf
from Buffer import Buffer
from model import initialize_model
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
import os

def setup_logging():
    # Configure application logging with green color
    app_handler = logging.StreamHandler()
    app_handler.setFormatter(logging.Formatter(
        '\033[92m%(asctime)s - %(levelname)s - %(message)s\033[0m'
    ))
    app_logger = logging.getLogger('app')
    app_logger.addHandler(app_handler)
    app_logger.setLevel(logging.DEBUG)

    # Custom filter for GPU-related messages
    class GPUMessageFilter(logging.Filter):
        def filter(self, record):
            return any(keyword in record.getMessage().upper() for keyword in 
                    ['GPU', 'DEVICE:GPU', 'XLA_GPU', 'CUDNN'])

    # Configure TensorFlow logging with blue color and GPU filter
    tf_handler = logging.StreamHandler()
    tf_handler.setFormatter(logging.Formatter(
        '\033[94m[TensorFlow] %(message)s\033[0m'
    ))
    tf_handler.addFilter(GPUMessageFilter())  # Add GPU filter to handler

    tf.get_logger().handlers.clear()  # Remove existing handlers
    tf.get_logger().addHandler(tf_handler)
    tf.get_logger().setLevel(logging.INFO)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  # Show INFO and above
    
setup_logging()

class Agent:
    def __init__(self, learning, save_file = None, initialize=False):          
        if(initialize):
            self.model = initialize_model()
        
        else:
            self.model = tf.keras.models.load_model(save_file)
            
        self.eps_tick = 0
        self.learning = learning
        
        if learning:
            self.optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
            self.buffer = Buffer()
            self.save_file = save_file 
                
    def set_gamma(self, value): #Gamma is set so that events in 30 seconds are worth 10% less.   
        self.gamma = value
        
    def get_eps(self):
        self.eps_tick += 1
        return 0.1 + 0.9 * np.exp(-1e-6 * self.eps_tick) #CHANGE THIS LATER ON 
    
    
    def get_qs(self, state, random_exploration = False):
        if random_exploration:
            is_random = random() < self.get_eps()
            if is_random:
                randomized_q_values = np.random.rand(10)
                return randomized_q_values
            
        q_values = self.model.predict(state)
        q_values = q_values[0] #Get rid of the batch_size dimension: goes from (1, 10) to (10,) 
          
        return q_values
        
    
    def remember_actions(self, state, action_idxs):
        action_idxs[1] += 5 #To account for the fact that indices for second's move are at [5: 10] of Misha's output
        self.former_visual_state = np.array(state[0][0])
        self.former_numerical_state = np.array(state[1][0])
        self.former_action_idxs = np.array(action_idxs)
    
    def add_experience_to_memory(self, future_state, reward):  
        gamma = self.gamma    
        visual_state = self.former_visual_state
        numerical_state = self.former_numerical_state
        action_idxs = self.former_action_idxs
        
        y_target = np.float32([reward + np.max(self.model(future_state)) * gamma]) #[] so that its not just a scalar
        self.buffer.add_experience_to_memory(visual_state, numerical_state, action_idxs, y_target)
        
        self.former_visual_state = None
        self.former_numerical_state = None
        self.former_action_idxs = None        
   
    def loss(self, qs, actions, y_target):
        #gather the qs of actions that were taken by the bot
        q_values_of_actions = tf.gather(qs, actions, batch_dims=1, axis=1)
        # logging.debug(f"q_values of actions: {q_values_of_actions[10]}")

        #Average the q_values across the two actions (average of the Q-value)
        #Like this and not losses separately because there is no point for q-value of either to predict the entire q-value - they are inherently entangled, so the loss should be entangled, too
        avg_q_values = tf.reduce_mean(q_values_of_actions, axis = 1, keepdims=True)
        # logging.debug(f"average q_values: {avg_q_values[10]}")
        
        square_losses = tf.square(y_target - avg_q_values)
        # logging.debug(f"losses: {square_losses[10]}")
        loss = tf.reduce_mean(square_losses)
        return loss
    
    def train_on_moves(self, epochs = 3):
        losses = []
        for _ in range (epochs):
            dataset = self.buffer.create_dataset()
            losses_in_epoch = []
            for batch in dataset:    
                visual_state = batch["visual_state"]
                numerical_state = batch["numerical_state"]
                action_idxs_batch = batch["action_idxs"]
                y_target_batch = batch["y_target"] 
                logging.debug(f"visual_state shape: {visual_state.shape}")
                logging.debug(f"numerical_state shape: {numerical_state.shape}")
                logging.debug(f"action_idxs_batch shape: {action_idxs_batch.shape}")
                logging.debug(f"y_target_batch shape: {y_target_batch.shape}")
                   
                with tf.GradientTape() as tape:
                    q_preds = self.model([visual_state, numerical_state])
                    loss_value = self.loss(q_preds, action_idxs_batch, y_target_batch)
                    # logging.debug(f"random q_predicts: {q_preds[10]}")
                    # logging.debug(f"random action_idxs: {action_idxs_batch[10]}")
                    # logging.debug(f"random y_targets: {y_target_batch[10]}")                    

                # Calculate gradients and apply
                gradients = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
                losses_in_epoch.append(loss_value)
                
                q_preds_test = self.model([visual_state, numerical_state])
                loss_value_test = self.loss(q_preds_test, action_idxs_batch, y_target_batch)
                print("/\n"*2)
                print("new loss in a test delta: ", loss_value_test - loss_value, (loss_value_test - loss_value)/loss_value)
                print("/\n"*2)
                
            losses.append(sum(losses_in_epoch)/len(losses_in_epoch))
        
        save_file = self.save_file if self.save_file != None else "Misha.keras"
        self.model.save(save_file)
        self.buffer.reset()
                
        return losses
    
    