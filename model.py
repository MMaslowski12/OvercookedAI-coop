from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Concatenate
from tensorflow.keras.models import Model
import tensorflow as tf

image_input = Input(shape=(64, 64, 3))
image_input = tf.image.resize(image_input, [84, 112])

#This defins the network through which the visual input (the screenshot of the board) will go through before joining other input
x = Conv2D(8, (3, 3), activation='relu')(image_input)
x = MaxPooling2D((2, 2))(x)
x = Conv2D(16, (3, 3), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)
x = Flatten()(x)


additional_input = Input(shape=(24,)) 
combined = Concatenate()([x, additional_input])

output = Dense(32, activation='relu')(combined)
output = Dense(10)(output)
model = Model(inputs=[image_input, additional_input], outputs=output)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print(model.summary())
model.save('Misha.h5')
