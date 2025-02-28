from together import Together
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf

model = "meta-llama/Llama-Vision-Free"
# Initialize the Together client
client = Together(api_key="bad2be78c3522849f0b0ea463b7fd4f337daccc7b04d036cb6eb89ab146e0b92")

def get_response(prompt, system_prompt=None):
    """Get a text response from the LLM."""
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

def tensor_to_base64(tensor, tensor_type="numpy", format="JPEG"):
    """
    Convert an RGB tensor to a base64 encoded string.
    
    Args:
        tensor: RGB tensor (numpy array, PyTorch tensor, or TensorFlow tensor)
        tensor_type: Type of tensor ("numpy", "pytorch", or "tensorflow")
        format: Image format to use for encoding ("JPEG", "PNG", etc.)
        
    Returns:
        Base64 encoded string of the image
    """
    # Convert tensor to numpy array based on its type
    if tensor_type == "pytorch":
        # Handle PyTorch tensor
        if tensor.requires_grad:
            tensor = tensor.detach()
        if tensor.device.type != 'cpu':
            tensor = tensor.cpu()
        # Convert from [C, H, W] to [H, W, C] if needed
        if tensor.dim() == 3 and tensor.shape[0] in [1, 3, 4]:
            tensor = tensor.permute(1, 2, 0)
        img_array = tensor.numpy()
    
    elif tensor_type == "tensorflow":
        # Handle TensorFlow tensor
        img_array = tensor.numpy() if hasattr(tensor, 'numpy') else tf.make_ndarray(tensor)
    
    elif tensor_type == "numpy":
        # Already a numpy array
        img_array = tensor
    
    else:
        raise ValueError(f"Unsupported tensor_type: {tensor_type}. Use 'numpy', 'pytorch', or 'tensorflow'.")
    
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

# Example usage with your analyze_image function
def analyze_tensor_image(tensor, prompt, system_prompt=None, tensor_type="numpy"):
    """
    Analyze an image from a tensor using the Together.ai API.
    
    Args:
        tensor: RGB tensor (numpy array, PyTorch tensor, or TensorFlow tensor)
        prompt: Text prompt describing what to analyze in the image
        system_prompt: Optional system prompt to guide the model's behavior
        tensor_type: Type of tensor ("numpy", "pytorch", or "tensorflow")
        
    Returns:
        The model's analysis of the image
    """
    # Convert tensor to base64
    base64_image = tensor_to_base64(tensor, tensor_type=tensor_type)
    
    # Prepare messages with image content
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Create content list with text and image
    content = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }
    ]
    
    messages.append({"role": "user", "content": content})
    
    # Use a vision-capable model
    response = client.chat.completions.create(
        model=model,  # Use a vision model
        messages=messages,
    )
    
    return response.choices[0].message.content

system_prompt = "You are a pirate, ARR"

print("--------------------------------")

print(get_response("Yo?", system_prompt))

print("--------------------------------")

print(get_response("What is the capital of France?", system_prompt))

print("--------------------------------")

print(get_response("", system_prompt))