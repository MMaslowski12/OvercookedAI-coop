import numpy as np
from random import random
import tensorflow as tf
from Buffer import Buffer
from model import initialize_model
import logging
import time
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
    def __init__(self, learning, save_file = None, initialize=False, player_number=None):          
        if(initialize):
            self.model = initialize_model(player_number)
        
        else:
            self.model = tf.keras.models.load_model(save_file)
            
        self.learning = learning
        self.eps_ticks = 0
        
        if learning:
            self.optimizer = tf.keras.optimizers.Adam()
            self.buffer = Buffer(tfrecord_file="data"+str(player_number)+".tfrecord")
            
            # Enable mixed precision training
            policy = tf.keras.mixed_precision.Policy('mixed_float16')
            tf.keras.mixed_precision.set_global_policy(policy)
            
            self.save_file = save_file 
            self.gamma = 0.95 ** (10/60) #Action rate is 10, FPS is 60. 95% of the value after 1 second.
        
    
    def get_eps(self):
        assert(self.learning)
        k = -np.log((0.2 - 0.1) / 0.9) / 200000 #k is such that eps = 0.2 after 200000 ticks
        eps = 0.1 + 0.9 * np.exp(-k * self.eps_ticks)
        self.eps_ticks += 1
        
        return eps
    
    def get_qs(self, state, random_exploration = False):
        if random_exploration:
            is_random = random() < self.get_eps()
            if is_random:
                randomized_q_values = np.random.rand(5)
                return randomized_q_values
            
        q_values = self.model.predict(state)
        q_values = q_values[0] #Get rid of the batch_size dimension: goes from (1, 5) to (5,) 
          
        return q_values
    
    def add_experience_to_memory(self, visual_state, numerical_state, action_idx, future_state, reward):  
        action_idx = np.array([action_idx])
        
        y_target = np.float32([reward + np.max(self.model(future_state)) * self.gamma]) #[] so that its not just a scalar
        self.buffer.add_experience_to_memory(visual_state, numerical_state, action_idx, y_target)
        
        self.former_visual_state = None
        self.former_numerical_state = None
        self.former_action_idx = None        
   
    def loss(self, qs, action, y_target):
        #gather the qs of actions that were taken by the bot
        q_values_of_actions = tf.gather(qs, action, batch_dims=1, axis=1)
        # logging.debug(f"q_values of actions: {q_values_of_actions[10]}")
                
        square_losses = tf.square(y_target - q_values_of_actions)
        # logging.debug(f"losses: {square_losses}")
        loss = tf.reduce_mean(square_losses)
        return loss
    
    def train_on_moves(self, epochs = 3):
        print("Training on moves")
        losses = []
        time_per_dataset = 0
        for _ in range (epochs):
            start_time_epoch = time.time()
            dataset = self.buffer.create_dataset()
            end_time_epoch = time.time()
            time_per_dataset += end_time_epoch - start_time_epoch
            
            losses_in_epoch = []
            for batch in dataset:    
                visual_state = batch["visual_state"]
                numerical_state = batch["numerical_state"]
                action_idx_batch = batch["action_idx"]
                y_target_batch = batch["y_target"] 
                # logging.debug(f"visual_state shape: {visual_state.shape}")
                # logging.debug(f"numerical_state shape: {numerical_state.shape}")
                # logging.debug(f"action_idx_batch shape: {action_idx_batch.shape}")
                # logging.debug(f"y_target_batch shape: {y_target_batch.shape}")
                   
                with tf.GradientTape() as tape:
                    q_preds = self.model([visual_state, numerical_state])
                    loss_value = self.loss(q_preds, action_idx_batch, y_target_batch)
                    # logging.debug(f"random q_predicts: {q_preds}")
                    # logging.debug(f"random action_idx: {action_idx_batch}")
                    # logging.debug(f"random y_targets: {y_target_batch}")
                    # logging.debug(f"loss_value: {loss_value}")                    

                # Calculate gradients and apply
                gradients = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
                losses_in_epoch.append(loss_value)
                
                q_preds_test = self.model([visual_state, numerical_state])
                loss_value_test = self.loss(q_preds_test, action_idx_batch, y_target_batch)
                
            losses.append(sum(losses_in_epoch)/len(losses_in_epoch))
        
        save_file = self.save_file if self.save_file != None else "Misha.keras"
        self.model.save(save_file)
        self.buffer.reset()

                
        return losses, time_per_dataset
    
    