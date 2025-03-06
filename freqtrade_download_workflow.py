import sys
import json  # For shared memory (using a file for simplicity)
from pocketflow import Node, Flow
# Assuming call_llm, call_llm_async, and search_web are defined in utils.call_llm (or similar)
from utils.call_llm import call_llm
# from utils.search_web import search_web

# --- Shared Memory (using a JSON file for simplicity) ---
SHARED_MEMORY_FILE = "shared_memory.json"

def load_shared_memory():
    try:
        with open(SHARED_MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_shared_memory(data):
    with open(SHARED_MEMORY_FILE, "w") as f:
        json.dump(data, f)

# --- Nodes ---

class UserInputNode(Node):
    def prep(self, shared):
        last_inputs = load_shared_memory()
        shared['last_inputs'] = last_inputs
        return None

    def exec(self, prep_res, shared): # Added 'shared' argument here
        print("\nEnter 'q' to quit at any time.")
        last_inputs = shared['last_inputs']

        default_exchange = last_inputs.get('exchange') if last_inputs else None # Set to None if no last_inputs
        default_asset_pair = last_inputs.get('asset_pair') if last_inputs else None # Set to None if no last_inputs
        default_timeframe = last_inputs.get('timeframe') if last_inputs else None # Set to None if no last_inputs

        while True:
            exchange_prompt = "Exchange"
            if default_exchange: # Suggest default only if default_exchange is not None
                exchange_prompt = f"{exchange_prompt} (default: {default_exchange})"
            exchange = input(f"{exchange_prompt}: ").strip()
            if not exchange and default_exchange: # Use default only if user input is empty and default_exchange is not None
                exchange = default_exchange
            elif not exchange:
                exchange = 'binance' # Hardcoded default if no last_inputs and no user input
            if exchange.lower() == 'q': return 'quit'

            asset_pair_prompt = "Asset Pair"
            if default_asset_pair: # Suggest default only if default_asset_pair is not None
                asset_pair_prompt = f"{asset_pair_prompt} (default: {default_asset_pair})"
            asset_pair = input(f"{asset_pair_prompt}: ").strip()
            if not asset_pair and default_asset_pair: # Use default only if user input is empty and default_asset_pair is not None
                asset_pair = default_asset_pair
            elif not asset_pair:
                asset_pair = 'BTC/USDT' # Hardcoded default if no last_inputs and no user input
            if asset_pair.lower() == 'q': return 'quit'

            timeframe_prompt = "Timeframe"
            if default_timeframe: # Suggest default only if default_timeframe is not None
                timeframe_prompt = f"{timeframe_prompt} (default: {default_timeframe})"
            timeframe = input(f"{timeframe_prompt}: ").strip()
            if not timeframe and default_timeframe: # Use default only if user input is empty and default_timeframe is not None
                timeframe = default_timeframe
            elif not timeframe:
                timeframe = '1d' # Hardcoded default if no last_inputs and no user input
            if timeframe.lower() == 'q': return 'quit'

            return {'exchange': exchange, 'asset_pair': asset_pair, 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['user_input'] = exec_res
        return 'validate'


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


class ConfirmationNode(Node):
    def prep(self, shared):
        validated_input = shared['validated_input']
        return validated_input

    def exec(self, prep_res, shared):
        exchange = prep_res['exchange']
        asset_pair = prep_res['asset_pair']
        timeframe = prep_res['timeframe']

        confirmation_message = f"\nConfirm download for:\nExchange: {exchange}\nAsset Pair: {asset_pair}\nTimeframe: {timeframe}\nDownload? (y/n): "
        confirm = input(confirmation_message).strip().lower()
        return confirm

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'y':
            return 'download'
        else:
            print("Download cancelled. Re-entering input.\n")
            return 'input'

class DownloadExecutionNode(Node):
    def prep(self, shared):
        validated_input = shared['validated_input']
        return validated_input

    def exec(self, prep_res, shared):
        exchange = prep_res['exchange']
        asset_pair = prep_res['asset_pair']
        timeframe = prep_res['timeframe']

        command = f"freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {asset_pair}"
        print(f"\nExecuting command: {command}\n")

        import subprocess
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_message = stdout.decode() + "\n" + stderr.decode()

        return {'command': command, 'output_message': output_message}


    def post(self, shared, prep_res, exec_res):
        shared['command_output'] = exec_res
        return 'summarize'

class SummaryNode(Node):
    def prep(self, shared):
        command_output = shared['command_output']
        return command_output

    def exec(self, prep_res, shared):
        output_message = prep_res['output_message']
        command = prep_res['command']

        # --- LLM Summary ---
        summary_prompt = f"""
        Please summarize the output of the following terminal command.
        Command: `{command}`
        Output:
        ```
        {output_message}
        ```
        Focus on the outcome (success/failure, any errors) and provide a concise summary.
        """
        summary = call_llm(summary_prompt) # Assuming call_llm is defined

        return {'summary_message': summary}


    def post(self, shared, prep_res, exec_res):
        print("\n--- Download Summary ---")
        print(exec_res['summary_message'])
        print("---\n")

        # Save last valid inputs to shared memory
        validated_input = shared['validated_input']
        save_shared_memory(validated_input)

        return 'input' # Loop back to input for next download


class ExitNode(Node):
    def exec(self, prep_res, shared):
        print("\nThank you for using the Freqtrade Download Assistant!")
        return None # No output

    def post(self, shared, prep_res, exec_res):
        return None # End of flow


# --- Flow Definition ---

input_node = UserInputNode()
validation_node = ValidationNode()
confirmation_node = ConfirmationNode()
download_execution_node = DownloadExecutionNode()
summary_node = SummaryNode()
exit_node = ExitNode()

input_node - 'validate' >> validation_node
input_node - 'quit' >> exit_node
validation_node - 'validate' >> confirmation_node # Corrected transition action to 'validate'
validation_node - 'input' >> input_node
confirmation_node - 'download' >> download_execution_node
confirmation_node - 'input' >> input_node
download_execution_node - 'summarize' >> summary_node
summary_node - 'input' >> input_node


download_flow = Flow(start=input_node)

def main():
    shared_data = {} # Initialize shared data
    flow_result = download_flow.run(shared_data) # or download_flow.run_async(shared_data) if using async nodes
    # print("Flow Result:", flow_result) # If needed to capture final action/result

if __name__ == '__main__':
    main()
