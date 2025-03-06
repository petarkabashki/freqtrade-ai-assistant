from pocketflow import Node
from utils.call_llm import call_llm # Direct import from utils
import json

class ValidationNode(Node):
    def prep(self, shared):
        # --- Retrieve data from shared store ---
        self.field_name = shared['field_to_validate']
        self.field_value = shared['field_value']
        return {'field_name': self.field_name, 'field_value': self.field_value}

    def exec(self, prep_res, shared):
        field_name = prep_res['field_name']
        field_value = prep_res['field_value']

        def constraints_for_field(field_name):
            if field_name == 'exchange':
                return "Must be one of: binance, ftx, kucoin, or coinbase."
            elif field_name == 'asset_pair':
                return "Must be in BASE/QUOTE format (e.g., BTC/USDT). If the quote currency is missing, default to USDT. Standardize the base and quote currency to their short forms if necessary."
            elif field_name == 'timeframe':
                return "Must be one of: 1d, 3d, 1w, 2w, 1M, 3M, 6M, or 1y. Convert to the standard format if necessary (e.g., '1 month' to '1M')."
            return "No specific constraints defined for this field."

        # --- LLM Validation ---
        validation_prompt = f"""
        You are a system for validating user inputs for downloading cryptocurrency data.
        Validate the user input for the field: '{field_name}'.
        Input Value: {field_value}

        Constraints:
        For '{field_name}', the constraints are:
        {constraints_for_field(field_name)}

        Response Format:
        Return a JSON object that strictly adheres to this format:
        ```json
        {{
          "field_name": "{field_name}", // MUST be exactly the field_name being validated
          "is_valid": true/false,
          "error": "error message if invalid" // Only include if is_valid is false
        }}
        ```

        Example of valid response for exchange 'binance':
        ```json
        {{
          "field_name": "exchange",
          "is_valid": true
        }}
        ```

        Example of invalid response for exchange 'invalid_exchange':
        ```json
        {{
          "field_name": "exchange",
          "is_valid": false,
          "error": "Invalid exchange: invalid_exchange. Must be one of binance, ftx, kucoin, or coinbase."
        }}
        ```

        Begin!
        """
        validation_prompt_with_constraints = validation_prompt.format( # use .format instead of .replace
            constraints_for_field(field_name)
        )

        validation_response = call_llm(validation_prompt_with_constraints) # Assuming call_llm is defined
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
