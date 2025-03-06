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
        validation_errors = shared.get('validation_errors', {}) # Get validation errors, default to empty dict

        input_data = {} # Dictionary to store the input data

        # Function to get input for a field, considering validation errors and defaults
        def get_input_for_field(field_name, default_value=None, is_valid=True):
            if is_valid and default_value:
                print(f"{field_name} is valid from previous input.")
                return default_value # Reuse valid input, don't ask again

            while True:
                if not is_valid: # Only show prompt if the field is invalid
                    prompt_text = f"{field_name} (re-enter)"
                else:
                    prompt_text = f"{field_name}"

                if default_value and is_valid: # Suggest default only if default_value is not None and field is valid from last input or initial input
                    prompt_text = f"{prompt_text} (default: {default_value})"
                elif default_value and not is_valid: # Still suggest default if available even if re-entering
                     prompt_text = f"{prompt_text} (default available: {default_value})"

                user_input = input(f"{prompt_text}: ").strip()
                if user_input.lower() == 'q': return 'quit'
                if user_input: # If input is not empty, use it
                    return user_input
                elif default_value and is_valid: # If input is empty but default exists and field was valid, use default
                    return default_value
                elif not is_valid: # If re-entering invalid field and input is empty, re-prompt
                    print(f"{field_name} cannot be empty. Please re-enter or 'q' to quit.")
                    continue
                elif not default_value and is_valid: # if initial input and no default available and empty input, re-prompt
                    print(f"{field_name} cannot be empty. Please enter or 'q' to quit.")
                    continue
                else: # Should not reach here, but for safety, re-prompt
                    print(f"{field_name} cannot be empty. Please re-enter or 'q' to quit.")
                    continue


        # Display Validation Errors from previous ValidationNode run
        if validation_errors:
            print("\nValidation Errors:")
            for input_type, result in validation_errors.items():
                if not result['is_valid']:
                    error_message = result.get('error', 'Unknown error')
                    print(f"- Invalid {input_type}: {error_message}")
            print("Please correct these issues.\n")


        # Get Exchange - Conditionally prompt based on validation errors
        is_exchange_valid = validation_errors.get('exchange', {}).get('is_valid', True) # Assume valid if no validation error for exchange
        default_exchange = last_inputs.get('exchange') if last_inputs else None
        input_data['exchange'] = get_input_for_field("Exchange", default_exchange, is_exchange_valid)
        if input_data['exchange'] == 'quit': return 'quit'


        # Get Asset Pair - Conditionally prompt based on validation errors
        is_asset_pair_valid = validation_errors.get('asset_pair', {}).get('is_valid', True) # Assume valid if no validation error for asset_pair
        default_asset_pair = last_inputs.get('asset_pair') if last_inputs else None
        input_data['asset_pair'] = get_input_for_field("Asset Pair", default_asset_pair, is_asset_pair_valid)
        if input_data['asset_pair'] == 'quit': return 'quit'


        # Get Timeframe - Conditionally prompt based on validation errors
        is_timeframe_valid = validation_errors.get('timeframe', {}).get('is_valid', True) # Assume valid if no validation error for timeframe
        default_timeframe = last_inputs.get('timeframe') if last_inputs else None
        input_data['timeframe'] = get_input_for_field("Timeframe", default_timeframe, is_timeframe_valid)
        if input_data['timeframe'] == 'quit': return 'quit'


        shared.pop('validation_errors', None) # Clear errors after input again, regardless of quit or continue

        return input_data

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['user_input'] = exec_res
        return 'validate'
