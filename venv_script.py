import subprocess
import sys
import os
import platform

def run_command(command, description=""):
    """Helper function to run a command and handle errors."""
    result = subprocess.run(
        command,
        capture_output=True,  # Capture stdout and stderr
        text=True,            # Output as text (string)
        check=False           # Don't automatically raise exceptions
    )
    if result.returncode == 0:
        print(f"{description} succeeded.")
    else:
        print(f"{description} failed with return code: {result.returncode}")
        print(f"Standard Output:\n{result.stdout}")
        print(f"Standard Error:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command)

def install_requirements(requirements_file="requirements.txt"):
    """
    Installs dependencies from a requirements.txt file.
    """
    try:
        print(f"Installing dependencies from '{requirements_file}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Dependencies installed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies. Error: {e}")
        
def freeze():
    subprocess.check_call(f"{sys.executable} -m pip freeze > requirements.txt", shell=True)

def activate_venv(venv_name="venv"):
    print(sys.executable)
    if not os.path.exists(venv_name):
        run_command([sys.executable, "-c", "print('Hello, World!')"])
        run_command([sys.executable, "-m", "pip", "install", "virtualenv"])
        print("installed venv")
        run_command([sys.executable, "-m", "venv", venv_name])
        print("Venv created")
        
    # Determine the correct path based on the operating system
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_name, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_name, "bin", "python")
        
    subprocess.check_call([venv_python, "-c", "print('Hello, World!')"])
    
    # Print activation instructions
    print_activation_instructions(venv_name)
    
    return venv_python

def print_activation_instructions(venv_name="venv"):
    """Print instructions for activating the virtual environment."""
    print("\n=== HOW TO ACTIVATE THE VIRTUAL ENVIRONMENT ===")
    
    if platform.system() == "Windows":
        print(f"Run: {venv_name}\\Scripts\\activate")
    else:
        print(f"Run: source {venv_name}/bin/activate")
    
    print("\nAfter activation, your command prompt should show the environment name.")
    print("When you're done, type 'deactivate' to exit the virtual environment.")
    print("================================================\n")
    
def get_requirements(venv_name="venv", requirements_file="requirements.txt"):
    #Virtual environment - set it up as venv_python to activate commands with it later
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_name, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_name, "bin", "python")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_file])

def setup_venv(venv_python):
    # subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
    packages = [
        "setuptools",
        "numpy",
        "tensorflow",
        "keras",
        "pygame",
        "matplotlib",
        "jupyter",
        "notebook",
        "tqdm",
        "ipykernel",
    ]

    
    def install(package):
        """Install a package using pip."""
        subprocess.check_call([venv_python, "-m", "pip", "install", "-q", package])

    # Install all packages
    for package in packages:
        try:
            print(f"Installing {package}...")
            install(package)
            print(f"Successfully installed {package}!")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}. Error: {e}")

    print("All packages installed (or attempted).")
    freeze()
    
    subprocess.check_call([venv_python, "-m", "ipykernel" ,"install", "--user", "--name=venv"])
    print("Installed the kernel")
    
if __name__ == "__main__":
    # List of packages to install
    venv_python = activate_venv()
    setup_venv(venv_python)
    print_activation_instructions()  # Print instructions again at the end
