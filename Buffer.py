import tensorflow as tf
import os
import numpy as np
import time

class Buffer():
    def __init__(self, tfrecord_file, buffer_size = 50000, batch_size=64, visual_state_dims=(72, 96, 3), numerical_state_dims = 28, action_idx_dims=1, y_target_dims=1):#64, 1e5
        # self.tfrecord_file = tfrecord_file
        # self.tfrecord_writer = tf.io.TFRecordWriter(tfrecord_file)  # Initialize TFRecord writer
        # self.reset()
        
        self.buffer_size = buffer_size 
        self.batch_size = batch_size
        
        self.visual_state_dims = visual_state_dims 
        self.numerical_state_dims = numerical_state_dims
        self.action_idx_dims = action_idx_dims
        self.y_target_dims = y_target_dims
        
        # Initialize tensors with zeros for each component
        self.visual_states = np.zeros([buffer_size, *visual_state_dims], dtype=np.float32)
        self.numerical_states = np.zeros([buffer_size, numerical_state_dims], dtype=np.float32)
        self.action_idxs = np.zeros([buffer_size, action_idx_dims], dtype=np.int64)
        self.y_targets = np.zeros([buffer_size, y_target_dims], dtype=np.float32)
        
        self.current_index = 0
        
        self.print_memory_sizes()
        
    def print_memory_sizes(self):
        # Calculate memory size for each tensor
        visual_memory = self.visual_states.nbytes / (1024 * 1024)  # Convert to MB
        numerical_memory = self.numerical_states.nbytes / (1024 * 1024)
        action_memory = self.action_idxs.nbytes / (1024 * 1024)
        target_memory = self.y_targets.nbytes / (1024 * 1024)
        total_memory = visual_memory + numerical_memory + action_memory + target_memory
        
        print(f"Memory usage:")
        print(f"Visual states: {visual_memory:.2f} MB")
        print(f"Numerical states: {numerical_memory:.2f} MB") 
        print(f"Action indices: {action_memory:.2f} MB")
        print(f"Target values: {target_memory:.2f} MB")
        print(f"Total memory: {total_memory:.2f} MB")
        
    '''
    TOTAL OVERWRITE:
    JUST STORE ALL THE STUFF IN THE LISTS
    CREATE_DATASET IS JUST SLIGHTLY MODIFIED
    
    
    '''   
    
    # def _serialize_example(self, visual_state, numerical_state, action_idx, y_target):
    #     # print("/\n"*2)
    #     # print(visual_state.shape)
    #     # print(self.visual_state_dims)
    #     # print(numerical_state.shape)
    #     # print(self.numerical_state_dims)
    #     # print(action_idx.shape)
    #     # print(self.action_idx_dims)
    #     # print(y_target.shape)
    #     # print(self.y_target_dims)
    #     # print("/\n"*2)
    #     assert(visual_state.shape == self.visual_state_dims)
    #     assert(numerical_state.shape == (self.numerical_state_dims,))
    #     assert(action_idx.shape == (self.action_idx_dims, ))
    #     assert(y_target.shape == (self.y_target_dims, ))
    #     feature = {
    #         'visual_state': tf.train.Feature(float_list=tf.train.FloatList(value=visual_state.flatten())),
    #         'numerical_state': tf.train.Feature(float_list=tf.train.FloatList(value=numerical_state)),
    #         'action_idx': tf.train.Feature(int64_list=tf.train.Int64List(value=action_idx)),
    #         'y_target': tf.train.Feature(float_list=tf.train.FloatList(value=y_target)),
    #     }
        
    #     example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    #     return example_proto.SerializeToString()
    
    def add_experience_to_memory(self, visual_state, numerical_state, action_idx, y_target):
        self.visual_states[self.current_index] = visual_state
        self.numerical_states[self.current_index] = numerical_state  
        self.action_idxs[self.current_index] = action_idx
        self.y_targets[self.current_index] = y_target
        
        self.current_index = (self.current_index + 1) % self.buffer_size
        
        
        # serialized_example = self._serialize_example(visual_state, numerical_state, action_idx, y_target)
        # self.tfrecord_writer.write(serialized_example)
        
    
    # def _parse_example(self, example):
    #     visual_state_len = 1
    #     for dim in self.visual_state_dims: visual_state_len *= dim 
        
    #     feature_description = {
    #         'visual_state': tf.io.FixedLenFeature(visual_state_len, tf.float32),
    #         'numerical_state': tf.io.FixedLenFeature(self.numerical_state_dims, tf.float32),
    #         'action_idx': tf.io.FixedLenFeature(self.action_idx_dims, tf.int64),
    #         'y_target': tf.io.FixedLenFeature(self.y_target_dims, tf.float32),
    #     }
    #     parsed_example = tf.io.parse_single_example(example, feature_description)
        
    #     parsed_example['visual_state'] = tf.reshape(parsed_example['visual_state'], self.visual_state_dims)
    #     return parsed_example 
    
    def create_dataset(self):
        self.close_writer()
        #Get the dataset 
        # Convert numpy arrays to tensors
        visual_states_tensor = tf.convert_to_tensor(self.visual_states, dtype=tf.float32)
        numerical_states_tensor = tf.convert_to_tensor(self.numerical_states, dtype=tf.float32)
        action_idxs_tensor = tf.convert_to_tensor(self.action_idxs, dtype=tf.int64)
        y_targets_tensor = tf.convert_to_tensor(self.y_targets, dtype=tf.float32)
        
        dataset = tf.data.Dataset.from_tensor_slices((
            visual_states_tensor,
            numerical_states_tensor, 
            action_idxs_tensor,
            y_targets_tensor
        ))
        
        #for each example, do _parse_example
        # dataset = dataset.map(self._parse_example, num_parallel_calls=tf.data.AUTOTUNE)
        
        #Shuffle the dataset
        dataset = dataset.shuffle(buffer_size=self.buffer_size)
        
        #Batch it
        dataset = dataset.batch(self.batch_size)
        
        #prefetch it
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
        
    def reset(self):
        self.tfrecord_writer.close()

        os.remove(self.tfrecord_file) #Reset the buffer

        self.tfrecord_writer = tf.io.TFRecordWriter(self.tfrecord_file)
        
    def close_writer(self):
        self.tfrecord_writer.close()
