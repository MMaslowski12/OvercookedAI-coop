# Together.ai API Integration

This project uses the Together.ai API for LLM and vision-language model inference.

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your Together.ai API key:
   ```
   TOGETHER_API_KEY=your_api_key_here
   ```

   **Note:** The `.env` file is included in `.gitignore` to prevent your API key from being pushed to GitHub.

3. Alternatively, you can set the environment variable directly in your shell:
   ```
   # For Linux/macOS
   export TOGETHER_API_KEY=your_api_key_here
   
   # For Windows (Command Prompt)
   set TOGETHER_API_KEY=your_api_key_here
   
   # For Windows (PowerShell)
   $env:TOGETHER_API_KEY = "your_api_key_here"
   ```

## Usage

The `llm.py` file contains functions for interacting with the Together.ai API:

- `get_response()`: Get a text response from the LLM
- `analyze_tensor_image()`: Analyze an image using the vision-language model

See the function documentation for more details on usage. 