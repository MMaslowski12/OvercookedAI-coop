import numpy as np
import tensorflow as tf
import keras
import time
print(tf.__version__)
Misha = tf.keras.models.load_model("Misha.keras", safe_mode=False)



vis_state_buffer = []  # Visual state
num_state_buffer = []        # Numerical state
action_idxs_buffer = []              # Action indices
y_target_buffer = []            # Target values

optimizer = tf.keras.optimizers.Adam(learning_rate =0.0001)

def add_memory(vis_state, num_state, final_vis_state, final_num_state, action_idxs, reward, gamma = 0.9):
    #Add a data about a state and a reward that occured during playing of the game
    global vis_state_buffer
    global num_state_buffer
    global action_idxs_buffer
    global y_target_buffer
    
    y_target = reward + np.max(Misha((final_vis_state, final_num_state))) * gamma
    
    action_idxs[1] += 5 #To account for the fact that indices for second's move are at [5: 10] of Misha's output
    
    #Add: state, indices of actions, a reward to the memory buffer
    vis_state_buffer.extend(vis_state) # no [ because input already has a batch dimension
    num_state_buffer.extend(num_state) # no [ because input already has a batch dimension
    action_idxs_buffer.extend([action_idxs]) #[ because action_idxs is just a list of two idxs
    y_target_buffer.extend([y_target]) #[ because y_target is just an integer

# def save_memory_buffer():
#     np.save('memory_buffer.npy', memory_buffer)
    
def train_Misha(batch_size = 64, epochs = 3):
    #Get the memory buffer
    #Shuffle it, get the batches
    #Train it on every batch
    # memory_buffer = np.load('memory_buffer.npy')
    global optimizer
    global vis_state_buffer
    global num_state_buffer
    global action_idxs_buffer
    global y_target_buffer
    
    vis_state_buffer = np.array([vis_state_buffer])
    num_state_buffer = np.array([num_state_buffer])
    action_idxs_buffer = np.array([action_idxs_buffer])
    y_target_buffer = np.array([y_target_buffer])
    print("SIZES:")
    for buffer in [vis_state_buffer, num_state_buffer, action_idxs_buffer, y_target_buffer]:
        print(buffer.size, ", size: ", buffer.ndim)
    
    def loss(qs, actions, y_target):
        #Get the q-values of index actions as tensors
        #mean them
        
        #gather the qs of actions that were taken by the bot
        q_values_of_actions = tf.gather(qs, actions, batch_dims=1, axis=1)
        q_values_of_actions = tf.cast(q_values_of_actions, dtype=tf.float32)
        loss1 = tf.reduce_mean(tf.square(y_target - q_values_of_actions[:, 0:1]))
        loss2 = tf.reduce_mean(tf.square(y_target - q_values_of_actions[:, 1:2]))
        return (loss1+loss2)/2
    
    losses = np.array([])
    
    
    for _ in range (epochs):
        dataset = tf.data.Dataset.from_tensor_slices((vis_state_buffer, num_state_buffer, action_idxs_buffer, y_target_buffer))
        dataset = dataset.shuffle(buffer_size=len(vis_state_buffer)).batch(batch_size).prefetch(tf.data.experimental.AUTOTUNE)
        losses_in_epoch = np.array([]) 
        for vis_batch, num_batch, action_idxs_batch, y_target_batch in dataset:
            with tf.GradientTape() as tape:
                q_preds = Misha((vis_batch, num_batch))
                loss_value = loss(q_preds, action_idxs_batch, y_target_batch)

            # Calculate gradients and apply
            gradients = tape.gradient(loss_value, Misha.trainable_variables)
            optimizer.apply_gradients(zip(gradients, Misha.trainable_variables))
            losses_in_epoch = np.append(losses_in_epoch, loss_value)
            
        # losses = np.append(losses, losses_in_epoch)
            
    vis_state_buffer = []
    num_state_buffer = []
    action_idxs_buffer = []
    y_target_buffer = []
    start_saving = time.time()
    Misha.save("Misha.keras")
    saving_time = time.time() - start_saving
    print("Time saving: ", saving_time - start_saving)
    return (losses, saving_time)



    
    
    
    
    


    