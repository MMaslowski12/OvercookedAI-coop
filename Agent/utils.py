import tensorflow as tf
import numpy as np
from PIL import Image
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf
import ast

def keys2list(keys, controls):
    return [keys[control] for control in controls.values()]

def draw_image_from_tensor(tensor):
    """
    Draw an image from an RGB TensorFlow tensor.
    
    Args:
        tensor: RGB TensorFlow tensor
    """
    # Convert TensorFlow tensor to numpy array
    img_array = tensor.numpy() if hasattr(tensor, 'numpy') else tf.make_ndarray(tensor)
    
    # Ensure values are in the correct range for images
    if img_array.dtype == np.float32 or img_array.dtype == np.float64:
        if img_array.max() <= 1.0:
            img_array = (img_array * 255).astype(np.uint8)
        else:
            img_array = img_array.astype(np.uint8)
    
    # Create PIL Image
    img = Image.fromarray(img_array)
    
    # Display the image
    img.show()

def parse_commands(commands):
    try:
        result = ast.literal_eval(commands)
        return 0, result  # 0 indicates success
    
    except (ValueError, TypeError) as e:
        return 1, str(e)  # 1 indicates an error, return the error message as a string

def tensor_to_base64(tensor, tensor_type="numpy", format="PNG"):
    """
    Convert an RGB tensor to a base64 encoded string.
    
    Args:
        tensor: RGB tensor (numpy array, PyTorch tensor, or TensorFlow tensor)
        tensor_type: Type of tensor ("numpy", "pytorch", or "tensorflow")
        format: Image format to use for encoding ("PNG", "JPEG", etc.)
        
    Returns:
        Base64 encoded string of the image
    """
    # Convert TensorFlow tensor to numpy array if needed
    if isinstance(tensor, tf.Tensor):
        img_array = tensor.numpy()
    else:
        img_array = tensor
    
    # Ensure values are in the correct range for images
    if img_array.dtype == np.float32 or img_array.dtype == np.float64:
        if img_array.max() <= 1.0:
            img_array = (img_array * 255).astype(np.uint8)
        else:
            img_array = img_array.astype(np.uint8)
    
    # Create PIL Image
    img = Image.fromarray(img_array)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str

def display_image_from_base64(base64_str):
    """
    Display an image from a base64 encoded string.
    
    Args:
        base64_str: Base64 encoded string of the image
    """
    # Decode the base64 string
    image_data = base64.b64decode(base64_str)
    
    # Convert the binary data to a PIL Image
    image = Image.open(BytesIO(image_data))
    
    # Display the image
    image.show()