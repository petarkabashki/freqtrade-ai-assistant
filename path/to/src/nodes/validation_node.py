from pocketflow import Node
from utils.call_llm import call_llm
import yaml # For structured prompt output

class ValidationNode(Node):
    def prep(self, shared):
        # --- Retrieve data from shared store ---
        # this should be passed according to the pocketflow guidelines. AI!
        if 'field_to_validate' not in shared:
            print("Error: 'field_to_validate' key missing in shared data.")
            return 'missing_field_to_validate' # Indicate missing field
        if 'field_value' not in shared:
            print("Error: 'field_value' key missing in shared data.")
            return 'missing_field_value' # Indicate missing field

        self.field_name = shared['field_to_validate']
        self.field_value = shared['field_value']
        self.validation_prompt_path = self.params.get('validation_prompt_path')

        return self.field_value

    def exec(self, prep_res, shared):
        if prep_res in ['missing_field_to_validate', 'missing_field_value']:
            return prep_res # Return error indicator to post

        # --- Load validation prompt from file ---
        try:
            with open(self.validation_prompt_path, 'r') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            error_message = f"Validation prompt file not found: {self.validation_prompt_path}"
            print(f"Error: {error_message}")
            shared['validation_error_message'] = error_message # Store error in shared for user feedback
            return 'validate_failure' # Indicate validation failure

        # --- Construct prompt and call LLM ---
        prompt = prompt_template.format(field_value=prep_res) # Use prep_res which is field_value
        llm_response_text = call_llm(prompt)

        try:
            llm_response = yaml.safe_load(llm_response_text)
        except yaml.YAMLError as e:
            error_message = f"LLM response YAML parsing error: {e}"
            print(f"Error: {error_message}\nResponse text: {llm_response_text}") # Include response text for debugging
            shared['validation_error_message'] = error_message # Store error in shared for user feedback
            return 'validate_failure' # Indicate validation failure


        # --- Validate LLM response structure ---
        if not isinstance(llm_response, dict) or 'is_valid' not in llm_response or 'reason' not in llm_response:
            error_message = f"LLM response structure invalid. Expected 'is_valid' and 'reason' keys. Response: {llm_response}"
            print(f"Error: {error_message}")
            shared['validation_error_message'] = error_message # Store error in shared for user feedback
            return 'validate_failure' # Indicate validation failure

        if llm_response['is_valid']:
            return 'validate_success' # Validation success
        else:
            shared['validation_error_message'] = llm_response['reason'] # Store validation reason for user feedback
            return 'validate_failure' # Validation failure

    def post(self, shared, prep_res, exec_res):
        if exec_res in ['missing_field_to_validate', 'missing_field_value', 'validate_success', 'validate_failure']:
            return exec_res # Pass action status directly
        return 'default' # Default action if none of the above
