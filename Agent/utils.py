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

def combine_images_side_by_side(image1_base64, image2_base64):
    """
    Combine two base64 encoded images side by side and return the result as a base64 string.
    
    Args:
        image1_base64: Base64 encoded string of the first image
        image2_base64: Base64 encoded string of the second image
        
    Returns:
        Base64 encoded string of the combined image
    """
    try:
        # Decode base64 images
        img1 = Image.open(BytesIO(base64.b64decode(image1_base64)))
        img2 = Image.open(BytesIO(base64.b64decode(image2_base64)))
        
        # Create a new image with both images side by side
        # Add 2 pixels for the separator line
        total_width = img1.width + img2.width + 2
        max_height = max(img1.height, img2.height)
        combined_img = Image.new('RGB', (total_width, max_height))
        
        # Paste images
        combined_img.paste(img1, (0, 0))
        
        # Draw a vertical separator line (2 pixels wide)
        for y in range(max_height):
            for x in range(2):
                combined_img.putpixel((img1.width + x, y), (255, 255, 255))  # White line
        
        # Paste second image after the separator line
        combined_img.paste(img2, (img1.width + 2, 0))
        
        # Convert combined image to base64
        buffered = BytesIO()
        combined_img.save(buffered, format="PNG")
        combined_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        display_image_from_base64(combined_image_base64)
        return combined_image_base64
    except Exception as e:
        print(f"Error combining images: {e}")
        return None