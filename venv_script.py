import subprocess
import sys
import os

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
    if not os.path.exists(venv_name):
        subprocess.check_call([sys.executable, "-m", "venv", venv_name])
        print("Venv created")
    venv_python = os.path.join(venv_name, "bin", "python")
    return venv_python
    
def get_requirements(venv_name="venv", requirements_file="requirements.txt"):
    #Virtual environment - set it up as venv_python to activate commands with it later
    venv_python = os.path.join(venv_name, "bin", "python")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_file])

def setup_venv(venv_python):
    subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
    packages = [
        "setuptools",
        "numpy",
        "tensorflow",
        "pygame",
        "matplotlib",
        "jupyter",
        "notebook",
        "memory_profiler",
        "importlib",
    ]

    def install(package):
        """Install a package using pip."""
        subprocess.check_call([venv_python, "-m", "pip", "install", package])

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
    

if __name__ == "__main__":
    # List of packages to install
    venv_python = activate_venv(venv_name="testvenv")
    setup_venv(venv_python)
