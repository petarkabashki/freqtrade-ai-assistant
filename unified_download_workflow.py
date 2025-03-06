import subprocess
from utils.call_llm import call_llm
import yaml # Use yaml instead of json for llm output AI!

def main():
    print("Welcome to the Freqtrade Download Assistant!") # Welcome message AI!
    previous_errors = {} # Store previous errors as a dictionary, field -> error message
    validated_input_values = {} # Store last validated input values

    while True:
        # 1. Unified Input Prompt - Modified to be dynamic

        prompt_parts = []
        if previous_errors:
            # No longer printing static error messages here
            # The LLM will provide a user-friendly error message
            print(previous_errors.get("user_error_message", "Validation Errors:")) # Fallback message
            prompt_text = previous_errors.get("re_entry_prompt", "Please re-enter the invalid fields.") # Fallback prompt
            print(prompt_text)
        else:
            prompt_text = ", ".join([
                "exchange (e.g., binance, kucoin, coinbase, ftx)", # Exchange hint AI!
                "asset pair (e.g., BTC/USDT, ETH/BTC)", # Asset pair hint AI!
                "timeframe (e.g., 1d, 1w, 1M)" # Timeframe hint AI!
            ]) + " (or 'q' to quit): "


        if not previous_errors: # Only ask for input if not re-prompting due to errors
            user_input_str = input(prompt_text)

            if user_input_str.lower() in ["q", "quit"]:
                print("Thank you for using the Freqtrade Download Assistant!")
                break

            user_input_values = {}
            input_parts = user_input_str.split(',')
            fields_to_prompt = ["exchange", "asset pair", "timeframe"] # Initial fields to prompt
            for i, field in enumerate(fields_to_prompt):
                if i < len(input_parts):
                    user_input_values[field] = input_parts[i].strip()
                else:
                    user_input_values[field] = "" # Handle missing input if user just presses enter

            # Merge new user input with previously validated values for fields not being re-prompted
            current_input_to_validate = validated_input_values.copy()
            current_input_to_validate.update(user_input_values)
        else:
            # Re-prompting for specific fields based on previous errors
            fields_to_prompt = list(previous_errors.get("invalid_fields_list", [])) # Get invalid fields from LLM response
            if not fields_to_prompt:
                fields_to_prompt = ["exchange", "asset pair", "timeframe"] # Fallback to all fields if no invalid_fields_list

            prompt_parts = []
            for field in fields_to_prompt:
                default_value_text = ""
                if field == "exchange":
                    field_display_name = "exchange (e.g., binance, kucoin, coinbase, ftx)" # Exchange hint in re-prompt AI!
                    default_value = validated_input_values.get("exchange", "")
                elif field == "asset_pair":
                    field_display_name = "asset pair (e.g., BTC/USDT, ETH/BTC)" # Asset pair hint in re-prompt AI!
                    default_value = validated_input_values.get("asset_pair", "")
                elif field == "timeframe":
                    field_display_name = "timeframe (e.g., 1d, 1w, 1M)" # Timeframe hint in re-prompt AI!
                    default_value = validated_input_values.get("timeframe", "")

                if default_value:
                    default_value_text = f" (last valid: '{default_value}')"
                prompt_parts.append(f"{field_display_name}{default_value_text}")

            re_prompt_text = ", ".join(prompt_parts) + " (or 'q' to quit): "
            user_input_str = input(re_prompt_text)


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

            # Correctly merge new user input with previously validated values
            # Only update the fields that are being re-prompted
            for field in fields_to_prompt:
                if field in user_input_values:
                    validated_input_values[field] = user_input_values[field]
            current_input_to_validate = validated_input_values # current_input_to_validate now directly points to validated_input_values


        # 2. Input Validation via LLM
        validation_prompt = f"""
        Validate the following user inputs, considering the hints provided:
        - Exchange: '{current_input_to_validate.get("exchange", "")}' (Hint: e.g., binance, kucoin, coinbase, ftx) # Exchange hint in LLM prompt AI!
        - Asset Pair: '{current_input_to_validate.get("asset_pair", "")}' (Hint: e.g., BTC/USDT, ETH/BTC) # Asset pair hint in LLM prompt AI!
        - Timeframe: '{current_input_to_validate.get("timeframe", "")}' (Hint: e.g., 1d, 1w, 1M) # Timeframe hint in LLM prompt AI!

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
        - "user_error_message": A user-friendly, concise message summarizing all validation errors, suitable for displaying to the user. Make use of the provided hints to guide the user. # Hint instruction for error message AI!
        - "re_entry_prompt": A short, clear prompt asking the user to re-enter ONLY the invalid fields. Use the hints to remind the user of the expected input format. # Hint instruction for re-entry prompt AI! This prompt should be very brief and directly tell the user what to do next.

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
        user_error_message: "There were errors in your input. Please correct the exchange (e.g., binance, kucoin) and timeframe (e.g., 1d, 1w)." # Example error message with hints AI!
        re_entry_prompt: "Re-enter exchange, timeframe (e.g., binance, 1d)" # Example re-entry prompt with hints AI!
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
            user_error_message = validation_result.get("user_error_message", "")
            re_entry_prompt = validation_result.get("re_entry_prompt", "")
        except yaml.YAMLError as e: # Catch YAML decode errors
            print(f"Error: Could not decode LLM response as YAML. Please try again. Error details: {e}")
            previous_errors = {"llm_response": "Could not decode LLM response as YAML. Please try again."} # Store decode error
            continue

        if errors:
            current_errors = {}
            for i in range(len(errors)): # Still process errors to store them, but rely on LLM's user_error_message for display
                field_name = invalid_fields[i] if i < len(invalid_fields) else f"field_{i+1}" # Fallback field name
                error_message = errors[i]
                current_errors[field_name] = error_message # Store errors with field names

            previous_errors = { # Store LLM generated messages and invalid fields
                "user_error_message": user_error_message,
                "re_entry_prompt": re_entry_prompt,
                "invalid_fields_list": invalid_fields # Store list of invalid fields to re-prompt
            }
            continue
        else:
            previous_errors = {} # Clear errors if validation is successful
            # validated_input_values is already updated in the re-prompting section
            # No need to update it again here, as it was updated correctly during input processing.
            # Update variables to use validated values for confirmation and download
            exchange = validated_input_values["exchange"]
            asset_pair = validated_input_values["asset_pair"]
            timeframe = validated_input_values["timeframe"]

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
