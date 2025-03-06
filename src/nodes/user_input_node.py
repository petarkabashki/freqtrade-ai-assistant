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
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m"         # ANSI escape code to reset color

    def prep(self, shared):
        last_inputs = load_shared_memory()
        shared['last_inputs'] = last_inputs
        return None

    def exec(self, prep_res, shared): # Added 'shared' argument here
        print("\nPlease provide the required information.") # Subsequent guidance
        print("Enter 'q' to quit at any time.")
        last_inputs = shared['last_inputs']

        input_data = {} # Dictionary to store the input data
        fields = ['exchange', 'asset_pair', 'timeframe'] # Define order of fields
        validation_error_message = None # Initialize error message

        for field_name in fields:
            while True:
                if validation_error_message: # Display error message if validation failed
                    print(f"\n{UserInputNode.ORANGE_COLOR_CODE}Validation Error:{UserInputNode.RESET_COLOR_CODE} {validation_error_message}")
                    validation_error_message = None # Clear error message after displaying

                default_value = last_inputs.get(field_name) if last_inputs else None
                prompt_text = f"{field_name}"
                if default_value:
                    prompt_text = f"{prompt_text} (default: {default_value})"

                user_input = input(f"{prompt_text}: ").strip()
                if user_input.lower() == 'q': return 'quit'
                if not user_input and default_value:
                    input_data[field_name] = default_value
                    break # Input is valid as default is used, move to next field
                elif not user_input:
                    print(f"{field_name} cannot be empty. Please enter or 'q' to quit.")
                    continue # Re-prompt for the same field
                else:
                    shared['field_to_validate'] = field_name # Prepare shared data for validation node
                    shared['field_value'] = user_input
                    # --- Removed dynamic flow construction ---
                    # validation_action = self >> self.params['validation_node']
                    # validation_result_action = validation_action.run(shared)

                    validation_node = self.params['validation_node'] # Get ValidationNode from params
                    validation_result = validation_node.run(shared) # Call ValidationNode.run directly

                    if validation_result == 'validate_success': # Check against the action string returned by ValidationNode.post
                        input_data[field_name] = user_input
                        break # Input is valid, move to next field
                    elif validation_result == 'validate_failure': # Check against the action string returned by ValidationNode.post
                        validation_error_message = shared.get('validation_error_message') # Get specific error message
                        continue # Re-prompt for the same field


        return input_data

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['user_input'] = exec_res
        return 'validate'
