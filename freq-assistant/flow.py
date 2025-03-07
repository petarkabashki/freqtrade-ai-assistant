import sys
import os

# Add the project root and lib directory to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.path.join(PROJECT_ROOT, "lib")  # Construct path to lib directory
sys.path.insert(0, LIB_PATH) # Add lib path to sys.path


from pocketflow import Flow

# ... rest of your flow.py code ...
