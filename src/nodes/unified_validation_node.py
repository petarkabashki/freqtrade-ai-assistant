from pocketflow import Node
from utils.call_llm import call_llm
import yaml

class UnifiedValidationNode(Node):
    def prep(self, shared):
        collected_values = shared.get('collected', {})
        last_user_input = shared.get('last_user_input', {})
        validation_prompt = f"""
        Validate the following user inputs, considering the hints provided:
        - Last User Input: '{collected_values}' (This is the user's raw input)
        Collected values from previous steps:
        - Exchange: '{collected_values.get("exchange", "")}' 
        - Asset Pair: '{collected_values.get("asset_pair", "")}' 
        - Timeframe: '{collected_values.get("timeframe", "")}'

        Constraints:
        - Exchange must be one of 'binance', 'ftx', 'kucoin', or 'coinbase'.
        - Asset Pair must follow the 'BASE/QUOTE' format (default to 'USDT' if the quote is missing and convert the base to its standardized short form if needed).
        - Timeframe must be one of '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y' (conversion applied as required).

        Based on the validation, respond with a YAML object containing the following keys:
        - "exchange": The validated exchange, or null if invalid.
        - "asset_pair": The validated asset pair, or null if invalid.
        - "timeframe": The validated timeframe, or null if invalid.
        - "errors": An array of error messages, one for each invalid field.
        - "invalid_fields": List the names of the fields that are invalid.
        - "user_error_message": A user-friendly, concise message summarizing all validation errors, suitable for displaying to the user. 
        - "re_entry_prompt": A short, clear prompt asking the user to re-enter ONLY the invalid fields. Use the hints to remind the user of the expected input format. This prompt should be very brief and directly tell the user what to do next.

        Example Valid Response:
        ```yaml
        exchange: binance
        asset_pair: BTC/USDT
        timeframe: 1d
        errors: []
        invalid_fields: []
        user_error_message: ""
        re_entry_prompt: ""
        ```

        Example Invalid Response:
        ```yaml
        exchange: null
        asset_pair: ADA/USDT
        timeframe: null
        errors:
        - Invalid exchange
        - Invalid timeframe
        invalid_fields:
        - exchange
        - timeframe
        user_error_message: "There were errors in your input. Please correct the exchange (e.g., binance, kucoin) and timeframe (e.g., 1d, 1w)."
        re_entry_prompt: "Re-enter exchange, timeframe (e.g., binance, 1d)"
        ```
        """
        shared['validation_prompt'] = validation_prompt
        return {'prompt': validation_prompt}

    def exec(self, prep_res, shared):
        llm_response = call_llm(prep_res['prompt'])
        # this should collect and validate the input fields incrementally AI!

        try:
            validation_result = yaml.safe_load(llm_response)
            exchange = validation_result.get("exchange")
            asset_pair = validation_result.get("asset_pair")
            timeframe = validation_result.get("timeframe")
            errors = validation_result.get("errors", [])
            invalid_fields = validation_result.get("invalid_fields", [])
            user_error_message = validation_result.get("user_error_message", "")
            re_entry_prompt = validation_result.get("re_entry_prompt", "")
        except yaml.YAMLError as e:
            print(f"Error: Could not decode LLM response as YAML. Please try again. Error details: {e}")
            shared['previous_errors'] = {"llm_response": "Could not decode LLM response as YAML. Please try again."}
            return "reinput"

        if errors:
            shared['previous_errors'] = {
                "user_error_message": user_error_message,
                "re_entry_prompt": re_entry_prompt,
                "invalid_fields_list": invalid_fields
            }
            return "reinput"
        else:
            shared['previous_errors'] = {}
            shared['collected'] = { # AI: changed to 'collected'
                "exchange": exchange,
                "asset_pair": asset_pair,
                "timeframe": timeframe
            }
            return "confirmation"

    def post(self, shared, prep_res, exec_res):
        return {}
