import subprocess
import sys
try:
    subprocess.check_call([sys.executable, "pip", "install", "--upgrade", "tensorflow"])
    print("TensorFlow has been successfully updated.")
    
except subprocess.CalledProcessError as e:
    print(f"An error occurred while updating TensorFlow: {e}")
    
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Concatenate, Lambda, BatchNormalization, ReLU
from tensorflow.keras.models import Model
import tensorflow as tf

print(tf.__version__)


if __name__ == "__main__":
    image_input = Input(shape=(434, 576, 3))
    image_resized = Lambda(lambda image: tf.image.resize(image, (108, 144)), output_shape = (108, 144, 3))(image_input) 

    #This defins the network through which the visual input (the screenshot of the board) will go through before joining other input\\
    x = Conv2D(8, (3, 3), activation='relu')(image_resized)
    x = MaxPooling2D(3, 3)(x)
    x = Conv2D(16, (3, 3), activation='relu')(x)
    x = MaxPooling2D((3, 3))(x)
    x = Conv2D(32, (3, 3), activation='relu')(x)
    x = MaxPooling2D((3, 3))(x)
    x = Flatten()(x)

    x = Dense(128, activation='relu')(x)
    x = Dense(64, activation='relu')(x)
    additional_input = Input(shape=(24,)) 
    combined = Concatenate()([x, additional_input])
    x = Dense(32, activation='relu')(combined)
    output = Dense(10, activation='linear')(x)
    model = Model(inputs=[image_input, additional_input], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

    model.summary()
    model.save("Misha.keras")
