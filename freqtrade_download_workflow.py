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
from src.nodes.exchange_input_node import ExchangeInputNode
from src.nodes.asset_pair_input_node import AssetPairInputNode # Import AssetPairInputNode
from src.nodes.timeframe_input_node import TimeframeInputNode # Import TimeframeInputNode
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
validation_node = ValidationNode() # Define validation_node **FIRST**
exchange_input_node = ExchangeInputNode()
asset_pair_input_node = AssetPairInputNode() # Instantiate AssetPairInputNode
timeframe_input_node = TimeframeInputNode() # Instantiate TimeframeInputNode
confirmation_node = ConfirmationNode()
download_execution_node = DownloadExecutionNode()
summary_node = SummaryNode()
exit_node = ExitNode()

# --- Dynamically set validation node in Input Nodes ---
exchange_input_node.params['validation_node'] = validation_node # Set param **AFTER** validation_node is defined and **BEFORE** Flow creation!
asset_pair_input_node.params['validation_node'] = validation_node # Set param for AssetPairInputNode
timeframe_input_node.params['validation_node'] = validation_node # Set param for TimeframeInputNode

# --- Flow Definition ---
download_flow = Flow(start=exchange_input_node) # Start with exchange input node
download_flow.params = {} # Initialize flow params


# --- Flow Definition ---
exchange_input_node - 'quit' >> exit_node
exchange_input_node - 'validate_exchange' >> asset_pair_input_node # Go to asset_pair input after exchange
asset_pair_input_node - 'quit' >> exit_node
asset_pair_input_node - 'validate_asset_pair' >> timeframe_input_node # Go to timeframe input after asset_pair
timeframe_input_node - 'quit' >> exit_node
timeframe_input_node - 'validate_timeframe' >> confirmation_node # Go to confirmation after timeframe
confirmation_node - 'download' >> download_execution_node
confirmation_node - 'input' >> exchange_input_node # Go back to exchange input if not confirmed
download_execution_node - 'summarize' >> summary_node
summary_node - 'input' >> exchange_input_node # Loop back to exchange input for next download


def main():
    print("\nWelcome to the Freqtrade Download Assistant!") # Initial greeting
    print("Please provide the required information to download data.\n") # Initial guidance

    shared_data = {} # Initialize shared data
    flow_result = download_flow.run(shared_data) # or download_flow.run_async(shared_data) if using async nodes
    # print("Flow Result:", flow_result)  # If needed to capture final action/result

if __name__ == '__main__':
    main()
