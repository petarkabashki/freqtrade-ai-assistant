from pocketflow import Node
from utils.call_llm import call_llm
import yaml

class ValidationNode(Node): # Class name is already ValidationNode, this is correct
    def prep(self, shared):
        collected_values = shared.get('collected', {})
        last_user_input = shared.get('last_user_input', '')
        validation_prompt = f"""
        User is providing information to download trading data.
        The user may provide all information at once, or field by field, incrementally.
        Validate and extract structured information from the user input, considering the already collected information and hints provided.

        Last User Input: '{last_user_input}'

        Collected values from previous steps (YAML format, may be empty):
        ```yaml
        {yaml.dump(collected_values)}
        ```

        Required information:
        - Exchange: The cryptocurrency exchange to download data from. Must be one of: 'binance', 'ftx', 'kucoin', or 'coinbase'.
        - Asset Pair: The trading pair for which to download data. Must be in 'BASE/QUOTE' format, e.g., 'BTC/USDT'. Default QUOTE is 'USDT' if not provided.
        - Timeframe: The candlestick timeframe. Must be one of: '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y'.

        Instructions:
        - Analyze the Last User Input in combination with the Collected values to determine if the user provided or corrected any of the Required information fields (Exchange, Asset Pair, Timeframe).
        - For each field, if new information is provided in the Last User Input, update the Collected values.
        - Validate ALL THREE fields (Exchange, Asset Pair, Timeframe) based on the Constraints.
        - If any field is invalid or missing, identify ALL invalid/missing fields.
        - Respond with a YAML object containing:
            - "exchange": The VALIDATED exchange if valid and provided, otherwise null. Retain previously collected valid value if user is not providing new exchange info in this turn.
            - "asset_pair": The VALIDATED asset pair if valid and provided, otherwise null. Retain previously collected valid value if user is not providing new asset_pair info in this turn.
            - "timeframe": The VALIDATED timeframe if valid and provided, otherwise null. Retain previously collected valid value if user is not providing new timeframe info in this turn.
            - "errors": A list of error messages, one for each invalid or missing field. If all fields are valid, this should be an empty list.
            - "invalid_fields": A list of names of fields that are invalid or missing. If all fields are valid, this should be an empty list.
            - "user_error_message": A user-friendly, concise message summarizing all validation errors. Should be empty if no errors.
            - "re_entry_prompt": A short, clear prompt asking the user to re-enter ONLY the invalid or missing fields. Should be empty if no errors. Be very brief and directly tell the user what to do next, e.g., "Re-enter missing exchange and timeframe".

        Example YAML Responses:

        # Example 1: All inputs are valid or already collected
        ```yaml
        exchange: binance
        asset_pair: BTC/USDT
        timeframe: 1d
        errors: []
        invalid_fields: []
        user_error_message: ""
        re_entry_prompt: ""
        ```

        # Example 2: Some inputs are invalid or missing
        ```yaml
        exchange: null # or previously collected valid exchange if still valid
        asset_pair: ADA/USD  # even if previous valid asset_pair was collected, re-validate it
        timeframe: null # or previously collected valid timeframe if still valid
        errors:
        - Invalid exchange provided. Must be one of 'binance', 'ftx', 'kucoin', 'coinbase'.
        - Invalid timeframe provided. Must be one of '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y'.
        invalid_fields:
        - exchange
        - timeframe
        user_error_message: "Please provide a valid exchange (binance, kucoin) and timeframe (e.g., 1d, 1w)."
        re_entry_prompt: "Re-enter exchange and timeframe"
        ```

        # Example 3: User provides valid exchange, but asset_pair and timeframe are still needed from previous turns
        ```yaml
        exchange: kucoin # now valid and updated
        asset_pair: BTC/USDT # previously collected and still valid
        timeframe: 1w # previously collected and still valid
        errors: []
        invalid_fields: []
        user_error_message: ""
        re_entry_prompt: ""
        ```

        Output in YAML:
        """
        shared['validation_prompt'] = validation_prompt
        return {'prompt': validation_prompt}

    def exec(self, prep_res, shared):
        llm_response = call_llm(prep_res['prompt'])

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

        # Update collected values incrementally
        collected_values = shared.get('collected', {})
        if exchange: collected_values['exchange'] = exchange
        if asset_pair: collected_values['asset_pair'] = asset_pair
        if timeframe: collected_values['timeframe'] = timeframe
        shared['collected'] = collected_values


        if errors:
            shared['errors'] = {
                "user_error_message": user_error_message,
                "re_entry_prompt": re_entry_prompt,
                "invalid_fields_list": invalid_fields
            }
            return "reinput"
        else:
            shared['previous_errors'] = {}
            return "confirmation"

    def post(self, shared, prep_res, exec_res):
        return exec_res
