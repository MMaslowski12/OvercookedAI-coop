import os

reasoner_model = "meta-llama/Llama-Vision-Free"
executor_model = "meta-llama/Llama-Vision-Free"
syntaxer_model = "meta-llama/Llama-Vision-Free"
# Initialize the Together client with API key from environment variable
api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise ValueError("TOGETHER_API_KEY environment variable not set. Please set it in your .env file.")

