from together import Together
from dotenv import load_dotenv
from .looper_constants import reasoner_model, executor_model, syntaxer_model
from .utils import tensor_to_base64, display_image_from_base64, combine_images_side_by_side
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
import base64

load_dotenv()

client = Together()

class LooperMethods:
    def __init__(self, prompt_base):
        self.prompt_base = prompt_base
        self.syntaxer_ratio = [0, 0]
        self.fresh_memory_image = None
        self.fresh_memory_reasoning = None


    def _add_reasoning_visuals(self, past_image, current_image):
        content = []
        # Add descriptive text about the images
        if past_image is not None:
            # Combine past and current images side by side using the utility function
            combined_image_base64 = combine_images_side_by_side(past_image, current_image)
            
            if combined_image_base64:
                content.append({"type": "text", "text": f"### Past state of the game (before your last reasoning) and current state of the game are combined in the image below. The past state is on the left, and the current state is on the right.\n"})

                # Add combined image
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{combined_image_base64}"
                    }
                })

            else:
                # Fallback to just showing current image
                content.append({"type": "text", "text": f"### Current state of the game: \n"})
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{current_image}"
                    }
                })

        else:
            content.append({"type": "text", "text": f"### Current state of the game: \n"})
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{current_image}"
                }
            })
        
        return content
    
    def reason(self, remaining_actions, current_image, past_image=None, past_reasoning=None, tensor_type="tensorflow"):
        """
        Analyze an image from a tensor using the Together.ai API.
        
        Args:
            image: RGB tensor (numpy array, PyTorch tensor, or TensorFlow tensor)
            tensor_type: Type of tensor ("numpy", "pytorch", or "tensorflow")
            
        Returns:
            The model's analysis of the image
        """
        if past_image is None:
            past_image = self.fresh_memory_image
        if past_reasoning is None:
            past_reasoning = self.fresh_memory_reasoning

        # Get prompt from self.prompt_base
        current_prompt = self.prompt_base.get_reasoner_prompt(past_answer=past_reasoning, remaining_actions=remaining_actions)
            
        # Prepare messages with image content
        messages = []
        
        # Create content list with text and image
        content = []
        
        # Add system prompt to the user query if provided
        content.append({"type": "text", "text": f"### System Prompt\n{current_prompt}"})

        # Convert current image to base64
        current_image = tensor_to_base64(current_image, tensor_type=tensor_type)
        
        content.extend(self._add_reasoning_visuals(past_image, current_image))

        content.append({"type": "text", "text": "### Your Response: \n"})
        
        messages.append({"role": "user", "content": content})
        
        response = client.chat.completions.create(
            model=reasoner_model,
            messages=messages,
        )
        
        print("--------------------------------")
        print("REASONING RESPONSE: \n", response.choices[0].message.content)
        print("--------------------------------")

        self.fresh_memory_image = current_image
        self.fresh_memory_reasoning = response.choices[0].message.content

        return response.choices[0].message.content

    def executor(self, reasoning_answer):
        content = []
        messages = []

        # Get prompt from self.prompt_base
        current_prompt = self.prompt_base.get_executor_prompt()

        content.append({"type": "text", "text": f"### System Prompt\n{current_prompt}"})
        content.append({"type": "text", "text": f"### Your reasoning: \n{reasoning_answer}"})
        content.append({"type": "text", "text": f"### Your list of the next 5 commands: \n"})
        messages.append({"role": "user", "content": content})

        response = client.chat.completions.create(
            model=executor_model,
            messages=messages,
        )
        response_str = response.choices[0].message.content

        print("--------------------------------")
        print("EXECUTOR RESPONSE: \n", response_str)
        print("--------------------------------")
        return response_str

    def syntaxer(self, input, grammar_function):
        grammar_result, parsed_string = grammar_function(input)
        error_count = 0

        while grammar_result != 0:
            error_count += 1
            if error_count > 2:
                return None

            error_message = parsed_string
            print("SYNTAXER ERROR: \n", input, "\n", error_message)
            print("--------------------------------")
            self.syntaxer_ratio[1] += 1
            response_str = self._call_syntaxer(input=input, error_message=error_message)

            input = response_str
            grammar_result, parsed_string = grammar_function(response_str)

        self.syntaxer_ratio[0] += 1
        print("SYNTAXER SUCCESS: \n", parsed_string)
        print("SYNTAXER RATIO: (success, error): \n", self.syntaxer_ratio)
        print("--------------------------------")
        return parsed_string

    def _call_syntaxer(self, input, error_message):
        content = []
        messages = []
        
        # Get prompt from self.prompt_base
        current_prompt = self.prompt_base.get_syntaxer_prompt()
        
        content.append({"type": "text", "text": f"### System Prompt\n{current_prompt}"})
        messages.append({"role": "user", "content": content})

        content = []
        content.append({"type": "text", "text": f"### Your output: \n{input}"})
        messages.append({"role": "assistant", "content": content})

        content = []
        content.append({"type": "text", "text": f"### Your error message: \n{error_message}"})
        messages.append({"role": "user", "content": content})

        content = []
        content.append({"type": "text", "text": f"### Your corrected output (again, adhering to the grammar outlined in the introduction): \n"})
        messages.append({"role": "user", "content": content})

        response = client.chat.completions.create(
            model=syntaxer_model,
            messages=messages,
        )
        response_str = response.choices[0].message.content

        return response_str 