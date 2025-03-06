from pocketflow import Node
import json  # For shared memory (using a file for simplicity)

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

class UserInputNode(Node):
    def prep(self, shared):
        last_inputs = load_shared_memory()
        shared['last_inputs'] = last_inputs
        return None

    def exec(self, prep_res, shared): # Added 'shared' argument here
        print("\nPlease provide the required information.") # Subsequent guidance
        print("Enter 'q' to quit at any time.")
        last_inputs = shared['last_inputs']

        # Check for validation errors from previous ValidationNode run
        validation_errors = shared.get('validation_errors')
        if validation_errors:
            print("\nValidation Errors:")
            for input_type, result in validation_errors.items():
                if not result['is_valid']:
                    error_message = result.get('error', 'Unknown error')
                    print(f"- Invalid {input_type}: {error_message}")
            shared.pop('validation_errors', None)  # Clear errors after displaying

        default_exchange = last_inputs.get('exchange') if last_inputs else None # Set to None if no last_inputs
        default_asset_pair = last_inputs.get('asset_pair') if last_inputs else None # Set to None if no last_inputs
        default_timeframe = last_inputs.get('timeframe') if last_inputs else None # Set to None if no last_inputs

        exchange, asset_pair, timeframe = None, None, None # Initialize outside loops

        while not exchange: # Loop until a valid exchange is entered
            exchange_prompt = "Exchange"
            if default_exchange: # Suggest default only if default_exchange is not None
                exchange_prompt = f"{exchange_prompt} (default: {default_exchange})"
            exchange_input = input(f"{exchange_prompt}: ").strip()
            if exchange_input.lower() == 'q': return 'quit'
            if exchange_input: # If input is not empty, use it
                exchange = exchange_input
            elif default_exchange: # If input is empty but default exists, use default
                exchange = default_exchange
            else: # If input is empty and no default, prompt again
                print("Exchange cannot be empty. Please enter an exchange or 'q' to quit.")
                continue # Go to the next iteration of the loop

        while not asset_pair: # Loop until a valid asset_pair is entered
            asset_pair_prompt = "Asset Pair"
            if default_asset_pair: # Suggest default only if default_asset_pair is not None
                asset_pair_prompt = f"{asset_pair_prompt} (default: {default_asset_pair})"
            asset_pair_input = input(f"{asset_pair_prompt}: ").strip()
            if asset_pair_input.lower() == 'q': return 'quit'
            if asset_pair_input: # If input is not empty, use it
                asset_pair = asset_pair_input
            elif default_asset_pair: # If input is empty but default exists, use default
                asset_pair = default_asset_pair
            else: # If input is empty and no default, prompt again
                print("Asset Pair cannot be empty. Please enter an asset pair or 'q' to quit.")
                continue # Go to the next iteration of the loop

        while not timeframe: # Loop until a valid timeframe is entered
            timeframe_prompt = "Timeframe"
            if default_timeframe: # Suggest default only if default_timeframe is not None
                timeframe_prompt = f"{timeframe_prompt} (default: {default_timeframe})"
            timeframe_input = input(f"{timeframe_prompt}: ").strip()
            if timeframe_input.lower() == 'q': return 'quit'
            if timeframe_input: # If input is not empty, use it
                timeframe = timeframe_input
            elif default_timeframe: # If input is empty but default exists, use default
                timeframe = default_timeframe
            else: # If input is empty and no default, prompt again
                print("Timeframe cannot be empty. Please enter a timeframe or 'q' to quit.")
                continue # Go to the next iteration of the loop


        return {'exchange': exchange, 'asset_pair': asset_pair, 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['user_input'] = exec_res
        return 'validate'
