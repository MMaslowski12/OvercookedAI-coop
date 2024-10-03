import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

Misha = load_model('Misha.h5')
memory_buffer = np.array([])    

def add_memory(state, final_state, action_idxs, reward, gamma = 0.9):
    #Add a data about a state and a reward that occured during playing of the game
    
    y_target = reward + final_state * gamma
    
    action_idxs[1] += 5 #To account for the fact that indices for second's move are at [5: 10] of Misha's output
    
    #Add: state, indices of actions, a reward to the memory buffer
    memory_buffer = memory_buffer.vstack(np.array(state, action_idxs, y_target))
    print(len(memory_buffer))
    
# def save_memory_buffer():
#     np.save('memory_buffer.npy', memory_buffer)
    
def train_Misha(batch_size = 32):
    #Get the memory buffer
    #Shuffle it, get the batches
    #Train it on every batch
    # memory_buffer = np.load('memory_buffer.npy')
    optimizer = tf.keras.optimizers.Adam()
    
    def loss(qs, actions, y_target):
        q_preds = tf.gather_nd(qs, tf.stack([tf.range(tf.shape(actions)[0])[:, tf.newaxis], actions], axis=-1))
        
        loss = tf.reduce_mean(tf.square(y_target - q_preds))
        return loss
    
    global memory_buffer
    np.random.shuffle(memory_buffer)
    batches = np.array_split(memory_buffer, len(memory_buffer) // batch_size)
    
    for batch in batches:        
        with tf.GradientTape() as tape:
            states = batch[:, 0]
            action_idxs = batch[:, 1]
            y_target = batch[:, 2]
            
            y_pred = Misha(states)  # Forward pass: compute model predictions
            loss = loss(y_pred, action_idxs, y_target)  # Compute loss

        gradients = tape.gradient(loss, Misha.trainable_variables)

        optimizer.apply_gradients(zip(gradients, Misha.trainable_variables))
        
    memory_buffer = np.array([])
    Misha.save('Misha.h5')



    
    
    
    
    


    