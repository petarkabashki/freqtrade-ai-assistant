import sys
import os

# Print current sys.path for debugging
print("Current sys.path:")
for path in sys.path:
    print(path)
print("-" * 20)

# Add the project root and lib directory to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.path.join(PROJECT_ROOT, "lib")  # Construct path to lib directory
sys.path.insert(0, LIB_PATH) # Add lib path to sys.path


# Print sys.path after modification for debugging
print("Modified sys.path:")
for path in sys.path:
    print(path)
print("-" * 20)


try:
    from pocketflow import Flow
    print("pocketflow module imported successfully!") # Debug message
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}") # Print specific error
    raise # Re-raise the exception to see the traceback

# ... rest of your flow.py code ...
