import subprocess
from utils.call_llm import call_llm
import yaml # Use yaml instead of json for llm output AI!

def main():
    previous_errors = [] # Initialize to store previous errors

    while True:
        # 1. Unified Input Prompt

        # Display previous errors if any
        if previous_errors:
            print("Validation Errors from previous input:")
            for error in previous_errors:
                print(f"- {error}")
            print("Please re-enter all fields.")

        user_input = input("Enter exchange, asset pair, and timeframe (or 'q' to quit): ")

        if user_input.lower() in ["q", "quit"]:
            print("Thank you for using the Freqtrade Download Assistant!")
            break

        # 2. Input Validation via LLM
        validation_prompt = f"""
        Validate the following user input, provided as a single string: '{user_input}'.

        The input string contains three fields, separated by commas. The fields are:
        - Exchange: Must be one of 'binance', 'ftx', 'kucoin', or 'coinbase'.
        - Asset Pair: Must follow the 'BASE/QUOTE' format (default to 'USDT' if the quote is missing and convert the base to its standardized short form if needed).
        - Timeframe: Must be one of '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y' (conversion applied as required).

        Respond with a YAML object containing the following keys:
        - "exchange": The validated exchange, or null if invalid.
        - "asset_pair": The validated asset pair, or null if invalid.
        - "timeframe": The validated timeframe, or null if invalid.
        - "errors": An array of error messages, one for each invalid field.  If all fields are valid, this should be an empty array.

        Example Valid Response:
        ```yaml
        exchange: binance
        asset_pair: BTC/USDT
        timeframe: 1d
        errors: []
        ```

        Example Invalid Response:
        ```yaml
        exchange: null
        asset_pair: null
        timeframe: null
        errors:
        - Invalid exchange
        - Invalid asset pair
        - Invalid timeframe
        ```
        """

        llm_response = call_llm(validation_prompt)

        try:
            validation_result = yaml.safe_load(llm_response) # Use yaml.safe_load instead of json.loads
            exchange = validation_result.get("exchange")
            asset_pair = validation_result.get("asset_pair")
            timeframe = validation_result.get("timeframe")
            errors = validation_result.get("errors", [])
        except yaml.YAMLError as e: # Catch YAML decode errors
            print(f"Error: Could not decode LLM response as YAML. Please try again. Error details: {e}")
            previous_errors = ["Could not decode LLM response as YAML. Please try again."] # Store decode error
            continue

        if errors:
            print("Validation Errors:")
            for error in errors:
                print(f"- {error}")
            previous_errors = errors # Store errors for next prompt
            continue
        else:
            previous_errors = [] # Clear errors if validation is successful

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
