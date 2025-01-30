import tensorflow as tf
import os

class Buffer():
    def __init__(self, tfrecord_file='data.tfrecord', buffer_size = 100000, batch_size=64, visual_state_dims=(108, 144, 3), numerical_state_dims = 28, action_idxs_dims=2, y_target_dims=1):#64, 1e5
        self.tfrecord_file = tfrecord_file
        self.tfrecord_writer = tf.io.TFRecordWriter(tfrecord_file)  # Initialize TFRecord writer
        self.reset()
        
        self.buffer_size = buffer_size 
        self.batch_size = batch_size
        
        self.visual_state_dims = visual_state_dims 
        self.numerical_state_dims = numerical_state_dims
        self.action_idxs_dims = action_idxs_dims
        self.y_target_dims = y_target_dims
        
        
    def _serialize_example(self, visual_state, numerical_state, action_idxs, y_target):
        print("/\n"*2)
        print(visual_state.shape)
        print(self.visual_state_dims)
        print(numerical_state.shape)
        print(self.numerical_state_dims)
        print(action_idxs.shape)
        print(self.action_idxs_dims)
        print(y_target.shape)
        print(self.y_target_dims)
        print("/\n"*2)
        assert(visual_state.shape == self.visual_state_dims)
        assert(numerical_state.shape == (self.numerical_state_dims,))
        assert(action_idxs.shape == (self.action_idxs_dims, ))
        assert(y_target.shape == (self.y_target_dims, ))
        feature = {
            'visual_state': tf.train.Feature(float_list=tf.train.FloatList(value=visual_state.flatten())),
            'numerical_state': tf.train.Feature(float_list=tf.train.FloatList(value=numerical_state)),
            'action_idxs': tf.train.Feature(int64_list=tf.train.Int64List(value=action_idxs)),
            'y_target': tf.train.Feature(float_list=tf.train.FloatList(value=y_target)),
        }
        
        example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
        return example_proto.SerializeToString()
    
    def add_experience_to_memory(self, visual_state, numerical_state, action_idxs, y_target):
        serialized_example = self._serialize_example(visual_state, numerical_state, action_idxs, y_target)
        self.tfrecord_writer.write(serialized_example)
        
    
    def _parse_example(self, example):
        visual_state_len = 1
        for dim in self.visual_state_dims: visual_state_len *= dim 
        
        feature_description = {
            'visual_state': tf.io.FixedLenFeature(visual_state_len, tf.float32),
            'numerical_state': tf.io.FixedLenFeature(self.numerical_state_dims, tf.float32),
            'action_idxs': tf.io.FixedLenFeature(self.action_idxs_dims, tf.int64),
            'y_target': tf.io.FixedLenFeature(self.y_target_dims, tf.float32),
        }
        parsed_example = tf.io.parse_single_example(example, feature_description)
        
        parsed_example['visual_state'] = tf.reshape(parsed_example['visual_state'], self.visual_state_dims)
        return parsed_example 
    
    def create_dataset(self):
        self.close_writer()
        #Get the dataset 
        dataset = tf.data.TFRecordDataset('data.tfrecord')
        
        #for each example, do _parse_example
        dataset = dataset.map(self._parse_example, num_parallel_calls=tf.data.AUTOTUNE)
        
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
