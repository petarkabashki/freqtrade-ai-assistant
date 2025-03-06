from pocketflow import Node
from utils.call_llm import call_llm # Import call_llm here
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
        - Exchange must be one of: binance, ftx, kucoin, or coinbase.
        - Asset Pair must be in BASE/QUOTE format (e.g., BTC/USDT). If the quote currency is missing, default to USDT.
        - Timeframe must be one of: 1d, 3d, 1w, 2w, 1M, 3M, 6M, or 1y.

        Response Format:
        Return a JSON object that strictly adheres to this format:
        {{
          "is_valid": true/false,
          "validated_input": {{ "exchange": "...", "asset_pair": "...", "timeframe": "..." }},
          "errors": ["error message 1", "error message 2", ...] // Only include if is_valid is false
        }}

        Example of valid response:
        ```json
        {{
          "is_valid": true,
          "validated_input": {{ "exchange": "binance", "asset_pair": "BTC/USDT", "timeframe": "1d" }}
        }}
        ```

        Example of invalid response:
        ```json
        {{
          "is_valid": false,
          "errors": ["Invalid exchange: kraken. Must be one of binance, ftx, kucoin, or coinbase."]
        }}
        ```

        Begin!
        """
        validation_response = call_llm(validation_prompt) # Assuming call_llm is defined
        try:
            validation_result = json.loads(validation_response)
            return validation_result
        except json.JSONDecodeError:
            return {'is_valid': False, 'errors': ["LLM validation response was not valid JSON."]}


    def post(self, shared, prep_res, exec_res):
        if exec_res['is_valid']:
            shared['validated_input'] = exec_res['validated_input']
            return 'validate' # Corrected action string here
        else:
            print("\nValidation Failed:")
            for error in exec_res['errors']:
                print(f"- {error}")
            print("Please re-enter your details.\n")
            return 'input'
