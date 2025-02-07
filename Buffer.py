import tensorflow as tf
import os
import numpy as np
import time
import logging

class Buffer():
    def __init__(self, buffer_size = 65536, batch_size=64, visual_state_dims=(72, 96, 3), numerical_state_dims = 28, action_idx_dims=1, y_target_dims=1):#64, 1e5
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
    
    def reset(self):
        self.visual_states = np.zeros([self.buffer_size, *self.visual_state_dims], dtype=np.float32)
        self.numerical_states = np.zeros([self.buffer_size, self.numerical_state_dims], dtype=np.float32)
        self.action_idxs = np.zeros([self.buffer_size, self.action_idx_dims], dtype=np.int64)
        self.y_targets = np.zeros([self.buffer_size, self.y_target_dims], dtype=np.float32)
        
        self.current_index = 0
    
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
    
    def add_batch_to_memory(self, states, actions, y_targets):
        # Handle batch of 64 experiences
        batch_size = len(states)
        end_index = self.current_index + batch_size
        actions = np.array(actions).reshape(-1, 1)
        y_targets = np.array(y_targets).reshape(-1, 1)
        
        # Handle wrap-around case
        if end_index > self.buffer_size:
            # Split into two parts
            first_part = self.buffer_size - self.current_index
            second_part = batch_size - first_part
            
            # First part goes from current_index to end of buffer
            self.visual_states[self.current_index:] = [s[0] for s in states[:first_part]]
            self.numerical_states[self.current_index:] = [s[1] for s in states[:first_part]]
            self.action_idxs[self.current_index:] = actions[:first_part]
            self.y_targets[self.current_index:] = y_targets[:first_part]
            
            # Second part wraps to start of buffer
            self.visual_states[:second_part] = [s[0] for s in states[first_part:]]
            self.numerical_states[:second_part] = [s[1] for s in states[first_part:]]
            self.action_idxs[:second_part] = actions[first_part:]
            self.y_targets[:second_part] = y_targets[first_part:]
            
            self.current_index = second_part
            
        else:
            # No wrap-around needed
            self.visual_states[self.current_index:end_index] = [s[0] for s in states]
            self.numerical_states[self.current_index:end_index] = [s[1] for s in states]
            self.action_idxs[self.current_index:end_index] = actions
            self.y_targets[self.current_index:end_index] = y_targets
            
            self.current_index = end_index % self.buffer_size
        
        
    
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
        # Use a generator that yields one sample at a time
        def generator():
            # When the buffer isn't fully filled,
            # you might prefer to yield only up to self.current_index.
            # Otherwise, if you consider the whole buffer as your dataset,
            # replace num_samples with self.buffer_size.
            assert(len(self.visual_states) > 0 )
            assert(len(self.visual_states) == len(self.numerical_states) == len(self.action_idxs) == len(self.y_targets))
            num_samples = self.current_index if self.current_index > 0 else self.buffer_size
            for i in range(num_samples):
                yield {
                    "visual_state": self.visual_states[i],
                    "numerical_state": self.numerical_states[i],
                    "action_idx": self.action_idxs[i],
                    "y_target": self.y_targets[i]
                }

        # Define the output signature so TensorFlow knows the shape and dtype for each element.
        output_signature = {
            "visual_state": tf.TensorSpec(shape=self.visual_state_dims, dtype=tf.float32),
            "numerical_state": tf.TensorSpec(shape=(self.numerical_state_dims,), dtype=tf.float32),
            "action_idx": tf.TensorSpec(shape=(self.action_idx_dims,), dtype=tf.int64),
            "y_target": tf.TensorSpec(shape=(self.y_target_dims,), dtype=tf.float32)
        }

        # Build the tf.data.Dataset from the generator.
        dataset = tf.data.Dataset.from_generator(generator, output_signature=output_signature)

        # Shuffle the data (buffering all samples for good mixing)
        dataset = dataset.shuffle(buffer_size=self.buffer_size)

        # Batch the dataset. Entire batches will be evaluated at once.
        dataset = dataset.batch(self.batch_size)

        # Prefetch to overlap the producer (data loading) and consumer (model execution)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        # Log the size of the dataset
        num_samples = self.current_index if self.current_index > 0 else self.buffer_size
        num_batches = num_samples // self.batch_size
        logging.debug(f"Created dataset with {num_samples} samples in {num_batches} batches of size {self.batch_size}")

        return dataset
        
        
