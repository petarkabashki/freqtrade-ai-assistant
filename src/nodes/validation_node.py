from pocketflow import Node
from ...utils.call_llm import call_llm # More explicit relative import: from ...utils
import json

class ValidationNode(Node):
    def prep(self, shared):
        user_input = shared['user_input']
        return user_input

    def exec(self, prep_res, shared):
        exchange = prep_res['exchange']
        asset_pair = prep_res['asset_pair']
        timeframe = prep_res['timeframe']

        # --- LLM Validation ---
        validation_prompt = f"""
        You are a system for validating user inputs for downloading cryptocurrency data.
        Validate the following user inputs to ensure they are valid for downloading data from Freqtrade.
        Inputs:
        Exchange: {exchange}
        Asset Pair: {asset_pair}
        Timeframe: {timeframe}

        Constraints:
        - **Exchange**: Must be one of: binance, ftx, kucoin, or coinbase.
        - **Asset Pair**: Must be in BASE/QUOTE format (e.g., BTC/USDT). If the quote currency is missing, default to USDT. Standardize the base and quote currency to their short forms if necessary.
        - **Timeframe**: Must be one of: 1d, 3d, 1w, 2w, 1M, 3M, 6M, or 1y. Convert to the standard format if necessary (e.g., '1 month' to '1M').

        Response Format:
        Return a JSON object that strictly adheres to this format:
        {{
          "is_valid": true/false,
          "validation_results": {{
            "exchange": {{ "is_valid": true/false, "error": "error message if invalid" }},
            "asset_pair": {{ "is_valid": true/false, "error": "error message if invalid" }},
            "timeframe": {{ "is_valid": true/false, "error": "error message if invalid" }}
          }},
          "validated_input": {{ "exchange": "...", "asset_pair": "...", "timeframe": "..." }} // Only include if is_valid is true
        }}

        Example of valid response:
        ```json
        {{
          "is_valid": true,
          "validation_results": {{
            "exchange": {{ "is_valid": true }},
            "asset_pair": {{ "is_valid": true }},
            "timeframe": {{ "is_valid": true }}
          }},
          "validated_input": {{ "exchange": "binance", "asset_pair": "BTC/USDT", "timeframe": "1d" }}
        }}
        ```

        Example of invalid response:
        ```json
        {{
          "is_valid": false,
          "validation_results": {{
            "exchange": {{ "is_valid": false, "error": "Invalid exchange: kraken. Must be one of binance, ftx, kucoin, or coinbase." }},
            "asset_pair": {{ "is_valid": true }},
            "timeframe": {{ "is_valid": false, "error": "Invalid timeframe: 2d. Must be one of 1d, 3d, 1w, 2w, 1M, 3M, 6M, or 1y." }}
          }}
        }}
        ```

        Begin!
        """
        validation_response = call_llm(validation_prompt) # Assuming call_llm is defined
        validation_result = {} # Initialize as empty dict to handle potential errors
        try:
            validation_result = json.loads(validation_response)
            return validation_result
        except json.JSONDecodeError:
            return {'is_valid': False, 'validation_results': {}, 'error': "LLM validation response was not valid JSON."}


    def post(self, shared, prep_res, exec_res):
        if exec_res['is_valid']:
             shared['validated_input'] = exec_res['validated_input']
             return 'validate' # Corrected action string here
        else:
            print("\nValidation Failed:")
            validation_results = exec_res['validation_results']
            if not validation_results: # defensive check in case LLM response is malformed re: validation_results
                print("- No detailed validation results received from LLM.")
            else:
                for input_type, result in validation_results.items():
                    if not result['is_valid']:
                        error_message = result.get('error', 'Unknown error') # Get error message or default
                        print(f"- Invalid {input_type}: {error_message}")
                    elif result['is_valid']:
                        print(f"- {input_type} is valid.") # Inform user about valid inputs as well

            print("Please re-enter your details.\n")
            return 'input'
