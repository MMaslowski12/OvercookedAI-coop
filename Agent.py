import numpy as np
from random import random
import tensorflow as tf
from Buffer import Buffer

from model import initialize_model
import tracemalloc
tracemalloc.start()

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
            self.optimizer = tf.keras.optimizers.Adam()
            self.buffer = Buffer()
            self.save_file = save_file

    def get_eps(self):
        self.eps_tick += 1
        return 0.1 + 0.9 * np.exp(- 1e-5/2 * self.eps_tick)
    
    
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
    
    def add_experience_to_memory(self, future_state, reward, gamma = 0.9984): #Gamma is set so that events in 30 seconds are worth 10% less.        
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

        #Average the q_values across the two actions (average of the Q-value)
        #Like this and not losses separately because there is no point for q-value of either to predict the entire q-value - they are inherently entangled, so the loss should be entangled, too
        avg_q_values = tf.reduce_mean(q_values_of_actions, axis = 1, keepdims=True)
        loss = tf.reduce_mean(tf.square(y_target - avg_q_values))
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
                with tf.GradientTape() as tape:
                    q_preds = self.model([visual_state, numerical_state])
                    loss_value = self.loss(q_preds, action_idxs_batch, y_target_batch)

                # Calculate gradients and apply
                gradients = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
                losses_in_epoch.append(loss_value)
                
            losses.append(sum(losses_in_epoch)/len(losses_in_epoch))
        
        save_file = self.save_file if self.save_file != None else "Misha.keras"
        self.model.save(save_file)
        self.buffer.reset()
                
        return losses
    
    