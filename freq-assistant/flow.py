import sys
import os

# Add the directory containing 'pocketflow' to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from pocketflow import Flow

# ... rest of your flow.py code ...
