import subprocess
from utils.call_llm import call_llm
import yaml # Use yaml instead of json for llm output AI!

def main():
    previous_errors = {} # Store previous errors as a dictionary, field -> error message
    validated_input_values = {} # Store last validated input values

    while True:
        # 1. Unified Input Prompt - Modified to be dynamic

        prompt_parts = []
        if previous_errors:
            print("Validation Errors from previous input:")
            for field, error in previous_errors.items():
                print(f"- {field}: {error}")
            print("Please re-enter the invalid fields.")

        fields_to_prompt = ["exchange", "asset pair", "timeframe"] # Default to all fields
        if previous_errors:
            fields_to_prompt = list(previous_errors.keys()) # Only prompt for fields with errors

        input_str_parts = []
        for field in fields_to_prompt:
            default_value_text = ""
            if field == "exchange":
                field_display_name = "exchange"
                default_value = validated_input_values.get("exchange", "")
            elif field == "asset pair":
                field_display_name = "asset pair"
                default_value = validated_input_values.get("asset_pair", "")
            elif field == "timeframe":
                field_display_name = "timeframe"
                default_value = validated_input_values.get("timeframe", "")

            if default_value:
                default_value_text = f" (last valid: '{default_value}')"
            prompt_parts.append(f"{field_display_name}{default_value_text}")

        prompt_text = ", ".join(prompt_parts) + " (or 'q' to quit): "
        user_input_str = input(prompt_text)


        if user_input_str.lower() in ["q", "quit"]:
            print("Thank you for using the Freqtrade Download Assistant!")
            break

        user_input_values = {}
        input_parts = user_input_str.split(',')
        for i, field in enumerate(fields_to_prompt):
            if i < len(input_parts):
                user_input_values[field] = input_parts[i].strip()
            else:
                user_input_values[field] = "" # Handle missing input if user just presses enter

        # Merge new user input with previously validated values for fields not being re-prompted
        current_input_to_validate = validated_input_values.copy()
        current_input_to_validate.update(user_input_values)


        # 2. Input Validation via LLM
        validation_prompt = f"""
        Validate the following user inputs:
        - Exchange: '{current_input_to_validate.get("exchange", "")}'
        - Asset Pair: '{current_input_to_validate.get("asset_pair", "")}'
        - Timeframe: '{current_input_to_validate.get("timeframe", "")}'

        Constraints:
        - Exchange must be one of 'binance', 'ftx', 'kucoin', or 'coinbase'.
        - Asset Pair must follow the 'BASE/QUOTE' format (default to 'USDT' if the quote is missing and convert the base to its standardized short form if needed).
        - Timeframe must be one of '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y' (conversion applied as required).

        Respond with a YAML object containing the following keys:
        - "exchange": The validated exchange, or null if invalid.
        - "asset_pair": The validated asset pair, or null if invalid.
        - "timeframe": The validated timeframe, or null if invalid.
        - "errors": An array of error messages, one for each invalid field.
        - "invalid_fields": List the names of the fields that are invalid.

        Example Valid Response:
        ```yaml
        exchange: binance
        asset_pair: BTC/USDT
        timeframe: 1d
        errors: []
        invalid_fields: []
        ```

        Example Invalid Response:
        ```yaml
        exchange: binance
        asset_pair: ADA/USDT
        timeframe: null
        errors:
        - Invalid timeframe
        invalid_fields:
        - timeframe
        ```
        """

        llm_response = call_llm(validation_prompt)

        try:
            validation_result = yaml.safe_load(llm_response) # Use yaml.safe_load instead of json.loads
            exchange = validation_result.get("exchange")
            asset_pair = validation_result.get("asset_pair")
            timeframe = validation_result.get("timeframe")
            errors = validation_result.get("errors", [])
            invalid_fields = validation_result.get("invalid_fields", [])
        except yaml.YAMLError as e: # Catch YAML decode errors
            print(f"Error: Could not decode LLM response as YAML. Please try again. Error details: {e}")
            previous_errors = {"llm_response": "Could not decode LLM response as YAML. Please try again."} # Store decode error
            continue

        if errors:
            print("Validation Errors:")
            current_errors = {}
            for i in range(len(errors)):
                field_name = invalid_fields[i] if i < len(invalid_fields) else f"field_{i+1}" # Fallback field name
                error_message = errors[i]
                print(f"- {field_name}: {error_message}")
                current_errors[field_name] = error_message # Store errors with field names
            previous_errors = current_errors # Store errors for next prompt
            continue
        else:
            previous_errors = {} # Clear errors if validation is successful
            validated_input_values = { # Store validated values
                "exchange": exchange,
                "asset_pair": asset_pair,
                "timeframe": timeframe
            }

        # 3. Download Confirmation
        print("\nConfirmation:")
        print(f"Exchange: {exchange}")
        print(f"Asset Pair: {asset_pair}")
        print(f"Timeframe: {timeframe}")

        confirmation = input("Confirm download? (y/n): ")
        if confirmation.lower() != "y":
            print("Download cancelled.  Returning to input prompt.")
            continue

        # 4. Download Execution
        command = f"freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {asset_pair}"
        print(f"Executing command: {command}")
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print("Download completed successfully!")
                print(stdout.decode())
            else:
                print("Download failed.")
                print(stderr.decode())
        except Exception as e:
            print(f"An error occurred during download: {e}")

if __name__ == "__main__":
    main()
