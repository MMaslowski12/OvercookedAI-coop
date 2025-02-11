import numpy as np
from random import random
import tensorflow as tf
from tqdm import tqdm
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
        self.eps_ticks = 10**5
        
        self.experience_state_batch = []
        self.experience_rewards_batch = []
        self.experience_action_batch = []
        self.experience_future_state_batch = []
        self.experience_future_mask_batch = []
        self.loss_distribution = []
        
        
        if learning:
            self.optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
            self.buffer = Buffer()
            
            # Enable mixed precision training
            policy = tf.keras.mixed_precision.Policy('mixed_float16')
            tf.keras.mixed_precision.set_global_policy(policy)
            
            self.save_file = save_file 
            self.gamma = 0.95 ** (10/60) #Action rate is 10, FPS is 60. 95% of the value after 1 second.
        
    
    def get_eps(self):
        assert(self.learning)
        k = -np.log((0.2 - 0.1) / 0.9) / 500000 #k is such that eps = 0.2 after 500000 ticks
        eps = 0.1 + 0.9 * np.exp(-k * self.eps_ticks)
        self.eps_ticks += 1
        
        return eps
    
    def get_qs_and_idxs(self, state=None, mask=None, batch_size=1, random_exploration = False):
        assert len(state) == batch_size, f"Expected first dimension of states to be {batch_size}, but got {state.shape}"
        
        if random_exploration:
            is_random = random() < self.get_eps()
            if is_random:
                randomized_q_values = tf.random.uniform((batch_size, 5))
                q_values_idxs = tf.argmax(randomized_q_values, axis=1)
                return randomized_q_values, q_values_idxs
        
        # Convert list of [visual_state, numerical_state] pairs into batched tensors
        visual_states = tf.stack([s[0] for s in state])
        numerical_states = tf.stack([s[1] for s in state])
        
        # Create list of inputs expected by model
        model_inputs = [visual_states, numerical_states]
        q_values = self.model(model_inputs)
        q_values_masked = q_values * mask
        
        q_values_idxs = tf.argmax(q_values_masked, axis=1)
        
        return q_values_masked, q_values_idxs
    
    def add_experience_to_batch(self, state, rewards, action, future_state, future_mask):  
        self.experience_state_batch.append(state)
        self.experience_rewards_batch.append(rewards)
        self.experience_action_batch.append(action)
        self.experience_future_state_batch.append(future_state)
        self.experience_future_mask_batch.append(future_mask)
        #Accumulate the states
    
    def _reset_experiences(self):
        self.experience_state_batch = []
        self.experience_rewards_batch = []
        self.experience_action_batch = []
        self.experience_future_state_batch = []
        self.experience_future_mask_batch = []
        
    def add_batch_to_memory(self):
        future_qs = self.get_qs_and_idxs(self.experience_future_state_batch, self.experience_future_mask_batch, batch_size=len(self.experience_future_state_batch))[0]
        max_future_qs = tf.reduce_max(future_qs, axis=1)
        y_target = np.array(self.experience_rewards_batch) + self.gamma * max_future_qs
        
        self.buffer.add_batch_to_memory(self.experience_state_batch, self.experience_action_batch, y_target)
        self._reset_experiences()
   
    def loss(self, qs, action, y_target):
        #gather the qs of actions that were taken by the bot
        q_values_of_actions = tf.gather(qs, action, batch_dims=1, axis=1)
        # logging.debug(f"q_values of actions: {q_values_of_actions[10]}")
                
        square_losses = tf.square(y_target - q_values_of_actions)
        # logging.debug(f"losses: {square_losses[0]}")
        loss = tf.reduce_mean(square_losses)
        # Store loss value in array for later saving
        if not hasattr(self, 'training_losses'):
            self.training_losses = []
        self.loss_distribution.append(float(loss))
        
        return loss
    
    def train_on_moves(self, epochs = 3):
        losses = []
        time_per_dataset = 0
        for epoch in range (epochs):
            tf.print(f"Epoch #{epoch}")
            dataset = self.buffer.create_dataset()
            
            losses_in_epoch = []
            # for batch in tqdm(dataset, desc=f"Epoch {epoch+1}/{epochs}", colour='green'): 
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
                    # Use tf operations to get sample values
                    # Print sample values for debugging
                    # tf.print("\nSample values from batch:")
                    # tf.print("Q predictions (first row):", q_preds[0])
                    # tf.print("Action index (first element):", action_idx_batch[0])
                    # tf.print("Y target (first element):", y_target_batch[0])

                # Calculate gradients and apply
                gradients = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
                losses_in_epoch.append(loss_value)
                
            losses.append(sum(losses_in_epoch)/len(losses_in_epoch))
        
        save_file = self.save_file if self.save_file != None else "Misha.keras"
        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Save loss distribution to file
        loss_dist_path = os.path.join('logs', 'loss_distribution.npy')
        np.save(loss_dist_path, np.array(self.loss_distribution))
        self.loss_distribution = []
        self.model.save(save_file)
        self.buffer.reset()
        
        eps = self.get_eps()
                
        return losses, time_per_dataset, eps
    
    