from pocketflow import Flow, Node
import subprocess

class CollectExchangeNode(Node):
    def prep(self, shared):
        # Initialize default values from shared memory, or empty strings if not present
        default_exchange = shared.get('exchange', '')
        default_pair = shared.get('pair', '')
        default_timeframe = shared.get('timeframe', '')
        # Defensive return: Ensure prep always returns a dict
        prep_dict = {
            'default_exchange': default_exchange,
            'default_pair': default_pair,
            'default_timeframe': default_timeframe,
        }
        print(f"CollectExchangeNode.prep CALLED. Returning: {prep_dict}") # DEBUG
        return prep_dict

    def exec(self, prep_res):
        print(f"CollectExchangeNode.exec CALLED. prep_res is: {prep_res}") # DEBUG

        # Forcefully ensure prep_res is a dictionary, even if it's None
        if prep_res is None:
            prep_res = {}
        elif not isinstance(prep_res, dict):
            prep_res = {}

        # Debug: Print keys after ensuring it's a dict
        print(f"DEBUG: prep_res is a dict with keys: {prep_res.keys()}") # DEBUG: print keys

        # VERY EXPLICIT CHECK RIGHT BEFORE ACCESS - EVEN MORE AGGRESSIVE
        if prep_res is None:
            raise ValueError("CRITICAL ERROR: prep_res is STILL None right before accessing it! Flow logic error?")
        if not isinstance(prep_res, dict):
            raise ValueError(f"CRITICAL ERROR: prep_res is STILL not a dict right before accessing it! Type: {type(prep_res)}")


        # No defensive check needed, rely on .get with default
        default_exchange = prep_res.get('default_exchange', '') # Use .get with default

        exchange = input(f"***ARE WE RUNNING THE RIGHT VERSION?*** Enter exchange (binance, ftx, kucoin, coinbase) or 'q' to quit (default: {default_exchange}): ").lower() # DISTINCTIVE PROMPT
        if exchange == 'q':
            return {'action': 'quit'}
        if not exchange: # User pressed Enter, use default
            exchange = default_exchange
        return {'action': 'validate_exchange', 'exchange': exchange}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'quit':
            return 'quit'
        shared['exchange'] = exec_res.get('exchange')
        return 'collect_pair'

class ValidateExchangeNode(Node): # <<<--- DEFINITION FOR ValidateExchangeNode IS ADDED HERE
    def exec(self, prep_res):
        exchange = prep_res['exchange']
        valid_exchanges = ('binance', 'ftx', 'kucoin', 'coinbase')

        if not exchange or exchange not in valid_exchanges:
            return {'action': 'invalid_exchange', 'message': f"Invalid exchange. Choose from: {', '.join(valid_exchanges)}"}

        return {'action': 'collect_pair', 'exchange': exchange}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'invalid_exchange':
            print(f"Input Error: {exec_res.get('message')}")
            return 'retry_exchange'
        return 'collect_pair'

class CollectPairNode(Node): # <<<--- DEFINITION FOR CollectPairNode IS ADDED HERE
    def prep(self, shared):
        default_pair = shared.get('pair', '')
        return {
            'default_pair': default_pair,
        }

    def exec(self, prep_res):
        default_pair = prep_res.get('default_pair', '') # Use .get with default
        pair = input(f"Enter pair (e.g., BTC/USDT) (default: {default_pair}): ").upper()
        if not pair: # User pressed Enter, use default
            pair = default_pair
        return {'action': 'validate_pair', 'pair': pair}

    def post(self, shared, prep_res, exec_res):
        shared['pair'] = exec_res.get('pair')
        return 'collect_timeframe'

class ValidatePairNode(Node): # <<<--- DEFINITION FOR ValidatePairNode IS ADDED HERE
    def prep(self, shared):
        exchange = shared.get('exchange')
        pair = shared.get('pair')
        return {
            'exchange': exchange,
            'pair': pair,
        }

    def exec(self, prep_res):
        pair = prep_res['pair']

        if not pair: # Check if pair is empty after input
            return {'action': 'invalid_pair', 'message': "Pair cannot be empty."}

        if not pair or '/' not in pair:
            pair = f"{pair}/USDT" # Assume USDT quote if only base is provided
            print(f"Assuming USDT quote, using pair: {pair}") # Inform user about assumption

        base, quote = pair.split('/')
        if not (base and quote): # simple check for base and quote not empty
            return {'action': 'invalid_pair', 'message': "Invalid pair format. Both base and quote are required."} # More specific message

        # TODO: Add logic to try and convert base to short form if needed

        return {'action': 'collect_timeframe', 'exchange': prep_res['exchange'], 'pair': pair}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'invalid_pair':
            print(f"Input Error: {exec_res.get('message')}")
            return 'retry_pair'
        return 'collect_timeframe'

class CollectTimeframeNode(Node): # <<<--- DEFINITION FOR CollectTimeframeNode IS ADDED HERE
    def prep(self, shared):
        default_timeframe = shared.get('timeframe', '')
        return {
            'default_timeframe': default_timeframe,
        }

    def exec(self, prep_res):
        default_timeframe = prep_res.get('default_timeframe', '') # Use .get with default
        timeframe = input(f"Enter timeframe (1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y) (default: {default_timeframe}): ").lower()
        if not timeframe: # User pressed Enter, use default
            timeframe = default_timeframe
        return {'action': 'validate_timeframe', 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        shared['timeframe'] = exec_res.get('timeframe')
        return 'validate_all_inputs'

class ValidateTimeframeNode(Node): # <<<--- DEFINITION FOR ValidateTimeframeNode IS ADDED HERE
    def exec(self, prep_res):
        timeframe = prep_res['timeframe']
        valid_timeframes = ('1d', '3d', '1w', '2w', '1m', '3m', '6m', '1y') # corrected timeframe list

        if not timeframe or timeframe not in valid_timeframes:
            return {'action': 'invalid_timeframe', 'message': f"Invalid timeframe. Choose from: {', '.join(valid_timeframes)}"}

        return {'action': 'execute_download', 'exchange': shared['exchange'], 'pair': shared['pair'], 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'invalid_timeframe':
            print(f"Input Error: {exec_res.get('message')}")
            return 'retry_timeframe'
        return 'execute_download'

class ExecuteDownloadNode(Node): # <<<--- DEFINITION FOR ExecuteDownloadNode IS ADDED HERE
    def prep(self, shared):
        # Retrieve exchange, pair, and timeframe from shared memory
        exchange = shared.get('exchange')
        pair = shared.get('pair')
        timeframe = shared.get('timeframe')
        return {
            'exchange': exchange,
            'pair': pair,
            'timeframe': timeframe,
        }

    def exec(self, prep_res):
        exchange = prep_res['exchange']
        pair = prep_res['pair']
        timeframe = prep_res['timeframe']

        command = [
            "freqtrade", "download-data",
            "--userdir", "./freq-user-data",
            "--data-format-ohlcv", "json",
            "--exchange", exchange,
            "-t", timeframe,
            "--timerange=20200101-", # Fixed timerange as per requirements
            "-p", pair
        ]

        try:
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            return {'action': 'success', 'output': process.stdout}
        except subprocess.CalledProcessError as e:
            return {'action': 'error', 'message': f"Download failed: {e.stderr}"}
        except FileNotFoundError:
            return {'action': 'error', 'message': "Error: freqtrade command not found. Ensure freqtrade is installed and in your PATH."}


    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'success':
            print(f"Download successful!\nOutput:\n{exec_res.get('output')}")
            return 'start_over'
        else:
            print(f"Download Error: {exec_res.get('message')}")
            return 'retry_input'

class QuitNode(Node): # <<<--- DEFINITION FOR QuitNode IS ADDED HERE
    def exec(self, prep_res):
        return "Thank you for using the Freqtrade Download Assistant!"

    def post(self, shared, prep_res, exec_res):
        print(exec_res)
        return None  # End the flow


class ValidateAllInputsNode(Node):  # New ValidateAllInputsNode
    def prep(self, shared):
        exchange = shared.get('exchange')
        pair = shared.get('pair')
        timeframe = shared.get('timeframe')
        return {
            'exchange': exchange,
            'pair': pair,
            'timeframe': timeframe,
        }

    def exec(self, prep_res):
        exchange = prep_res['exchange']
        pair = prep_res['pair']
        timeframe = prep_res['timeframe']

        # --- LLM PROMPT --- (This is a placeholder, refine as needed)
        prompt = f"""
        Validate the following user inputs for a freqtrade download command:
        Exchange: {exchange}
        Pair: {pair}
        Timeframe: {timeframe}

        Valid exchanges are: binance, ftx, kucoin, coinbase.
        Pair should be in format BASE/QUOTE, e.g., BTC/USDT. Assume USDT if quote is missing.
        Valid timeframes are: 1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y.

        Return a YAML structure with:
        - 'validation_status': OK or NOT_OK
        - If NOT_OK, include:
            - 'error_messages': a list of error messages for each invalid field.
            - 'next_action':  'retry_exchange', 'retry_pair', 'retry_timeframe', or 'retry_all' if unclear.
        - If OK, 'next_action': 'execute_download'

        Example for invalid exchange and timeframe:
        ```yaml
        validation_status: NOT_OK
        error_messages:
          - field: exchange
            message: "Invalid exchange. Choose from binance, ftx, kucoin, coinbase."
          - field: timeframe
            message: "Invalid timeframe. Choose from 1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y."
        next_action: retry_exchange
        ```
        """
        llm_response = call_llm(prompt)  # Replace with your actual LLM call utility
        validation_result = yaml.safe_load(llm_response)  # Assuming YAML output from LLM
        return validation_result

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('validation_status') == 'NOT_OK':
            print("Validation errors:")
            for error in exec_res.get('error_messages', []):
                print(f"  - {error['field']}: {error['message']}")
            return exec_res.get('next_action', 'retry_exchange')  # Default retry action
        return 'execute_download'  # Proceed to download if validation OK

validate_all_inputs_node = ValidateAllInputsNode()  # Instantiate ValidateAllInputsNode
collect_pair_node = CollectPairNode()
validate_pair_node = ValidatePairNode()
collect_timeframe_node = CollectTimeframeNode()
execute_download_node = ExecuteDownloadNode()
quit_node = QuitNode()
collect_exchange_node = CollectExchangeNode()  # <<<--- MOVE INSTANTIATION HERE, BEFORE FLOW DEF
validate_exchange_node = ValidateExchangeNode() # Instantiate ValidateExchangeNode - even if not used in flow anymore, for code completeness, can be removed later

collect_exchange_node - "quit" >> quit_node
collect_exchange_node - "validate_exchange" >> collect_pair_node  # Go to collect pair directly

collect_pair_node - "collect_timeframe" >> collect_timeframe_node  # Go to collect timeframe directly

collect_timeframe_node - "validate_all_inputs" >> validate_all_inputs_node  # Go to validate all inputs

validate_all_inputs_node - "execute_download" >> execute_download_node  # Go to execute download if validation OK
validate_all_inputs_node - "retry_exchange" >> collect_exchange_node  # Retry from exchange if exchange invalid
validate_all_inputs_node - "retry_pair" >> collect_pair_node  # Retry pair if pair invalid
validate_all_inputs_node - "retry_timeframe" >> collect_timeframe_node  # Retry timeframe if timeframe invalid

download_flow = Flow(start=collect_exchange_node)


def main():
    shared_data = {}  # Initialize shared data dictionary
    download_flow.run(shared_data)

if __name__ == "__main__":
    main()
