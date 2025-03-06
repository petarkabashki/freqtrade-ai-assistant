from pocketflow import Node
import json

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

class ExchangeInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m"         # ANSI escape code to reset color

    def prep(self, shared):
        last_inputs = load_shared_memory()
        shared['last_inputs'] = last_inputs
        return None

    def _get_user_input(self, last_inputs, validation_error_message=None):
        field_name = 'exchange'
        if validation_error_message:
            print(f"\n{ExchangeInputNode.ORANGE_COLOR_CODE}Validation Error:{ExchangeInputNode.RESET_COLOR_CODE} {validation_error_message}")

        default_value = last_inputs.get(field_name) if last_inputs else None
        prompt_text = f"{field_name}"
        if default_value:
            prompt_text = f"{prompt_text} (default: {default_value})"
        return input(f"{prompt_text}: ").strip()

    def _validate_input(self, user_input, shared):
        field_name = 'exchange'
        if not user_input:
            default_value = shared['last_inputs'].get(field_name) if shared['last_inputs'] else None
            if default_value:
                return 'validate_success', default_value # Input is valid as default is used
            else:
                return 'empty_input', None # Indicate empty input, no default

        shared['field_to_validate'] = field_name # Prepare shared data for validation node
        shared['field_value'] = user_input
        # Why this nonsense ? AI!
        validation_node = self.params['validation_node'] # Get ValidationNode from params
        validation_result = validation_node.run(shared) # Call ValidationNode.run directly

        if validation_result == 'validate_success':
            return 'validate_success', user_input # Input is valid
        elif validation_result == 'validate_failure':
            return 'validate_failure', shared.get('validation_error_message') # Validation failed
        return 'unknown', None # Should not reach here, but handle unknown case


    def exec(self, prep_res, shared):
        print("\nPlease provide the exchange.")
        print("Enter 'q' to quit at any time.")
        last_inputs = shared['last_inputs']

        validation_error_message = None
        while True:
            user_input = self._get_user_input(last_inputs, validation_error_message)
            if user_input.lower() == 'q':
                return 'quit'

            validation_status, validation_response = self._validate_input(user_input, shared)

            if validation_status == 'validate_success':
                return validation_response # Input is valid
            elif validation_status == 'validate_failure':
                validation_error_message = validation_response # Set validation error message for next loop
                continue # Re-prompt for the same field
            elif validation_status == 'empty_input':
                print(f"Exchange cannot be empty. Please enter or 'q' to quit.")
                validation_error_message = None # Clear any previous error
                continue # Re-prompt for the same field
            else: # 'unknown' or any other unexpected status
                print(f"An unexpected validation status occurred: {validation_status}. Please try again.") # General error message
                validation_error_message = None # Clear any previous error
                continue # Re-prompt for the same field


    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['exchange_input'] = exec_res # Store validated input in shared memory
        return 'validate_exchange'
