import sys
import os # Import the os module
# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) # Add script directory to path

import json  # For shared memory (using a file for simplicity)
from pocketflow import Node, Flow
# Assuming call_llm, call_llm_async, and search_web are defined in utils.call_llm (or similar)
# from utils.call_llm import call_llm # moved to nodes
# from utils.search_web import search_web

# --- Node Imports ---
from src.nodes.user_input_node import UserInputNode
from src.nodes.validation_node import ValidationNode
from src.nodes.confirmation_node import ConfirmationNode
from src.nodes.download_execution_node import DownloadExecutionNode
from src.nodes.summary_node import SummaryNode
from src.nodes.exit_node import ExitNode

# --- Shared Memory (using a JSON file for simplicity) ---
SHARED_MEMORY_FILE = "shared_memory.json"

def load_shared_memory():
    try:
        with open(SHARED_MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_shared_memory(data):
    with open(SHARED_MEMORY_FILE, "w") as f:
        json.dump(data, f)

# --- Node Definitions ---
input_node = UserInputNode()
validation_node = ValidationNode() # Define validation_node BEFORE using it
confirmation_node = ConfirmationNode()
download_execution_node = DownloadExecutionNode()
summary_node = SummaryNode()
exit_node = ExitNode()

# --- Dynamically set validation node in UserInputNode ---
input_node.params['validation_node'] = validation_node # Set param **BEFORE** Flow creation!


# --- Flow Definition ---
download_flow = Flow(start=input_node) # Create the Flow **AFTER** setting params
download_flow.params = {} # Initialize flow params


# --- Flow Definition ---
input_node - 'validate' >> confirmation_node # Input node now transitions to confirmation after collecting all inputs
input_node - 'quit' >> exit_node
validation_node - 'validate_success' >> confirmation_node # These transitions are no longer used in the main flow
validation_node - 'validate_failure' >> input_node # These transitions are no longer used in the main flow
confirmation_node - 'download' >> download_execution_node
confirmation_node - 'input' >> input_node
download_execution_node - 'summarize' >> summary_node
summary_node - 'input' >> input_node


def main():
    print("\nWelcome to the Freqtrade Download Assistant!") # Initial greeting
    print("Please provide the required information to download data.\n") # Initial guidance

    shared_data = {} # Initialize shared data
    flow_result = download_flow.run(shared_data) # or download_flow.run_async(shared_data) if using async nodes
    # print("Flow Result:", flow_result)  # If needed to capture final action/result

if __name__ == '__main__':
    main()
