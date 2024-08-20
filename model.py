import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

class Model(keras.Sequential):
    def __init__(self, input_shape, output_shape):
        super().__init__()
        
        #Apply 32 different filters on the 2D pixel image, with Rectified Linear Unit as an activation function
        self.add(layers.Conv2D(16, (3, 3), activation='relu', input_shape=input_shape))
        
        #Pool the maximum value out of each 2x2 square
        self.add(layers.MaxPooling2D((2, 2)))
        
        self.add(layers.Conv2D(32, (3, 3), activation='relu'))
        self.add(layers.MaxPooling2D((2, 2)))
        
        self.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.add(layers.MaxPooling2D((2, 2)))
        
        #Flatten the neurons from 3D to 1D
        self.add(layers.Flatten())
        #A dense layer of 64 neurons, fully (densely) connected with the last layer
        self.add(layers.Dense(64, activation='relu'))
        
        #Add dropout to prevent overfitting
        self.add(layers.Dropout(0.5))
        self.add(layers.Dense(output_shape))
    
    
    
    
        