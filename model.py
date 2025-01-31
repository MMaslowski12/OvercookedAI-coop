from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Concatenate, BatchNormalization
from tensorflow.keras.models import Model
import tensorflow as tf
print(tf.__version__)

def initialize_model(player_number):
    image_input = Input(shape=(108, 144, 3))
    #This defins the network through which the visual input (the screenshot of the board) will go through before joining other input\\
    x = Conv2D(32, (3, 3), activation='relu')(image_input)
    x = BatchNormalization()(x)
    x = MaxPooling2D(3, 3)(x)
    x = Conv2D(32, (3, 3), activation='relu')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D(3, 3)(x)
    x = Conv2D(64, (3, 3), activation='relu')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D(3, 3)(x)
    # x = Conv2D(64, (3, 3), activation='relu')(x)
    # x = BatchNormalization()(x)
    # x = MaxPooling2D(3, 3)(x)
    x = Flatten()(x)

    x = Dense(256, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dense(128, activation='relu')(x)
    x = BatchNormalization()(x)
    additional_input = Input(shape=(28,)) 
    combined = Concatenate()([x, additional_input])
    x = Dense(64, activation='relu')(combined)
    x = BatchNormalization()(x)
    x = Dense(64, activation='relu')(x)
    x = BatchNormalization()(x)
    output = Dense(5, activation='linear')(x)
    model = Model(inputs=[image_input, additional_input], outputs=output)

    model.summary()
    model.save('Misha'+str(player_number)+'.keras')
    
    return model
   

# initialize_model(1)
# initialize_model(2)
