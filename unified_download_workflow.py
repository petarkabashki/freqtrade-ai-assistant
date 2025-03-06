import subprocess
from utils.call_llm import call_llm

def main():
    while True:
        # 1. Unified Input Prompt
        user_input = input("Enter exchange, asset pair, and timeframe (or 'q' to quit): ")

        if user_input.lower() in ["q", "quit"]:
            print("Thank you for using the Freqtrade Download Assistant!")
            break

# This prompt needs to as only for the invalid fields. AI!
        # 2. Input Validation via LLM
        validation_prompt = f"""
        Validate the following user input, provided as a single string: '{user_input}'.

        The input string contains three fields, separated by commas. The fields are:
        - Exchange: Must be one of 'binance', 'ftx', 'kucoin', or 'coinbase'.
        - Asset Pair: Must follow the 'BASE/QUOTE' format (default to 'USDT' if the quote is missing and convert the base to its standardized short form if needed).
        - Timeframe: Must be one of '1d', '3d', '1w', '2w', '1M', '3M', '6M', or '1y' (conversion applied as required).

        Respond with a JSON object containing the following keys:
        - "exchange": The validated exchange, or null if invalid.
        - "asset_pair": The validated asset pair, or null if invalid.
        - "timeframe": The validated timeframe, or null if invalid.
        - "errors": An array of error messages, one for each invalid field.  If all fields are valid, this should be an empty array.

        Example Valid Response:
        ```json
        {{
            "exchange": "binance",
            "asset_pair": "BTC/USDT",
            "timeframe": "1d",
            "errors": []
        }}
        ```

        Example Invalid Response:
        ```json
        {{
            "exchange": null,
            "asset_pair": null,
            "timeframe": null,
            "errors": ["Invalid exchange", "Invalid asset pair", "Invalid timeframe"]
        }}
        ```
        """

        llm_response = call_llm(validation_prompt)

        try:
            import json
            validation_result = json.loads(llm_response)
            exchange = validation_result.get("exchange")
            asset_pair = validation_result.get("asset_pair")
            timeframe = validation_result.get("timeframe")
            errors = validation_result.get("errors", [])
        except json.JSONDecodeError:
            print("Error: Could not decode LLM response. Please try again.")
            continue

        if errors:
            print("Validation Errors:")
            for error in errors:
                print(f"- {error}")
            continue

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
