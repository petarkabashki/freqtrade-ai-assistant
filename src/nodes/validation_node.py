from pocketflow import Node
from utils.call_llm import call_llm # Direct import from utils
import json
import os

class ValidationNode(Node):
    def prep(self, shared):
        # --- Retrieve data from shared store ---
        self.field_name = shared['field_to_validate']
        self.field_value = shared['field_value']
        return {'field_name': self.field_name, 'field_value': self.field_value}

    def exec(self, prep_res, shared):
        field_name = prep_res['field_name']
        field_value = prep_res['field_value']

        prompt_file = f"src/nodes/validation_prompt_{field_name}.txt"
        if not os.path.exists(prompt_file):
            return {'field_name': field_name, 'is_valid': False, 'error': f"Prompt file not found: {prompt_file}"}

        with open(prompt_file, 'r') as f:
            validation_prompt_template = f.read()

        validation_prompt = validation_prompt_template.format(field_value=field_value)

        validation_response = call_llm(validation_prompt) # Assuming call_llm is defined
        validation_result = {} # Initialize as empty dict to handle potential errors
        try:
            validation_result = json.loads(validation_response)
            return validation_result
        except json.JSONDecodeError:
            return {'field_name': field_name, 'is_valid': False, 'error': "LLM validation response was not valid JSON."}


    def post(self, shared, prep_res, exec_res):
        field_name = prep_res['field_name']
        if exec_res['is_valid']:
            # --- Put validation result into shared store ---
            shared['validation_result'] = exec_res # Store the entire validation result in shared
            return 'validate_success' # Action is still needed for flow control if used in a flow
        else:
            # --- Put validation result and error message into shared store ---
            shared['validation_result'] = exec_res # Store the entire validation result in shared
            shared['validation_error_message'] = f"Invalid {field_name}: {exec_res.get('error', 'Unknown error')}" # Store specific error message
            return 'validate_failure' # Action is still needed for flow control if used in a flow
