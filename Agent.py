import numpy as np
from random import random
import tensorflow as tf

from model import initialize_model

class Agent:
    def __init__(self, learning, save_file = None):
        if (save_file == None):
            self.model = initialize_model()
            #initialize using model or sth
            
        else:
            self.model = tf.keras.models.load_model("Misha.keras", safe_mode=False)
            #Save the model
            
        self.eps_tick = 0
        self.learning = learning
        if learning:
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
            self.optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-4)
            self.state_buffer = []
            self.action_idxs_buffer = []
            self.y_target_buffer = []

    def get_eps(self):
        self.eps_tick += 1
        return 0.1 + 0.9 * np.exp(- 1e-5/2 * self.eps_tick)
    
    
    def get_qs(self, state, eps_exploration = False):
        if eps_exploration:
            is_random = random() < self.get_eps()
            if is_random:
                randomized_q_values = np.random.rand(10)
                return randomized_q_values
            
        q_values = self.model.predict(state)
        q_values = q_values[0] #Get rid of the batch_size dimension: goes from (1, 10) to (10,) 
                    
        return q_values
    
    def add_actions_to_memory(self, state, action_idxs):
        action_idxs[1] += 5 #To account for the fact that indices for second's move are at [5: 10] of Misha's output
        
        self.state_buffer.extend(state) # no [ because input already has a batch dimension
        self.action_idxs_buffer.extend([action_idxs]) #[ because action_idxs is just a list of two idxs    
    
    def add_consequences_to_memory(self, future_state, reward, gamma = 0.9984): #Gamma is set so that events in 30 seconds are worth 10% less.        
        y_target = reward + np.max(self.model(future_state)) * gamma
        self.y_target_buffer.extend([y_target]) #[ because y_target is just an integer
   
    def prepare_buffers(self):
        assert(len(self.state_buffer) == len(self.action_idxs_buffer))
        assert(len(self.state_buffer) == len(self.y_target_buffer))
        
        state_buffer = np.array(self.Buffer.vis_state_buffer)
        action_idxs_buffer = np.array(self.Buffer.action_idxs_buffer)
        y_target_buffer = np.array(self.Buffer.y_target_buffer)
        dataset = tf.data.Dataset.from_tensor_slices((state_buffer, action_idxs_buffer, y_target_buffer))
        return dataset
    
    def reset_buffers(self):
        self.state_buffer = []
        self.action_idxs_buffer = []
        self.y_target_buffer = []
   
    def train_on_moves(self, epochs = 3, batch_size = 64):
        dataset = self.prepare_buffers()
        
        def loss(qs, actions, y_target):
            #gather the qs of actions that were taken by the bot
            q_values_of_actions = tf.gather(qs, actions, batch_dims=1, axis=1)

            #Average the q_values across the two actions (average of the Q-value)
            #Like this and not losses separately because there is no point for q-value of either to predict the entire q-value - they are inherently entangled, so the loss should be entangled, too
            avg_q_values = tf.reduce_mean(q_values_of_actions, axis = 1, keepdims=True)
            
            loss = tf.reduce_mean(tf.square(y_target - avg_q_values))
            return loss

        losses = []
        
        for _ in range (epochs):
            dataset = dataset.shuffle(buffer_size=len(self.state_buffer)).batch(batch_size).prefetch(tf.data.experimental.AUTOTUNE)
            losses_in_epoch = []
            for state, action_idxs_batch, y_target_batch in dataset:
                with tf.GradientTape() as tape:
                    q_preds = self.model(state)
                    loss_value = loss(q_preds, action_idxs_batch, y_target_batch)

                # Calculate gradients and apply
                gradients = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
                losses_in_epoch.append(loss_value)
                
            losses.append(losses_in_epoch)
                        
        self.reset_buffers()
        
        save_file = self.save_file if self.save_file != None else "Misha.keras"
        self.model.save(save_file)
                
        return losses
    
    