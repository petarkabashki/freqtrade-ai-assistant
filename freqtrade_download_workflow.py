from pocketflow import Flow, Node
import subprocess

class CollectInputNode(Node):
    def prep(self, shared):
        # Initialize default values from shared memory, or empty strings if not present
        default_exchange = shared.get('exchange', '')
        default_pair = shared.get('pair', '')
        default_timeframe = shared.get('timeframe', '')
        return {
            'default_exchange': default_exchange,
            'default_pair': default_pair,
            'default_timeframe': default_timeframe,
        }

    def exec(self, prep_res):
        default_exchange = prep_res['default_exchange']
        default_pair = prep_res['default_pair']
        default_timeframe = prep_res['default_timeframe']

        exchange = input(f"Enter exchange (binance, ftx, kucoin, coinbase) or 'q' to quit (default: {default_exchange}): ").lower()
        if exchange == 'q':
            return {'action': 'quit'}
        if not exchange: # User pressed Enter, use default
            exchange = default_exchange

        pair = input(f"Enter pair (e.g., BTC/USDT) (default: {default_pair}): ").upper()
        if not pair: # User pressed Enter, use default
            pair = default_pair

        timeframe = input(f"Enter timeframe (1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y) (default: {default_timeframe}): ").lower()
        if not timeframe: # User pressed Enter, use default
            timeframe = default_timeframe

        return {'action': 'validate', 'exchange': exchange, 'pair': pair, 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'quit':
            return 'quit'
        shared['exchange'] = exec_res.get('exchange')
        shared['pair'] = exec_res.get('pair')
        shared['timeframe'] = exec_res.get('timeframe')
        return 'validate'

class ValidateInputNode(Node):
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

        valid_exchanges = ('binance', 'ftx', 'kucoin', 'coinbase')
        valid_timeframes = ('1d', '3d', '1w', '2w', '1m', '3m', '6m', '1y') # corrected timeframe list

        if not exchange or exchange not in valid_exchanges: # check if exchange is None or invalid
            return {'action': 'invalid', 'message': f"Invalid exchange. Choose from: {', '.join(valid_exchanges)}"}

        if not pair or '/' not in pair: # check if pair is None or invalid
            return {'action': 'invalid', 'message': "Invalid pair format. Use format like BTC/USDT."}

        base, quote = pair.split('/')
        if not (base and quote): # simple check for base and quote not empty
            return {'action': 'invalid', 'message': "Invalid pair format. Base and quote are required."}


        if not timeframe or timeframe not in valid_timeframes: # check if timeframe is None or invalid
            return {'action': 'invalid', 'message': f"Invalid timeframe. Choose from: {', '.join(valid_timeframes)}"}

        return {'action': 'execute'}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'invalid':
            print(f"Input Error: {exec_res.get('message')}")
            return 'retry_input' # Action to go back to CollectInputNode
        return 'execute_download' # Action to proceed to ExecuteDownloadNode

class ExecuteDownloadNode(Node):
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
            return 'start_over' # Action to go back to CollectInputNode
        else:
            print(f"Download Error: {exec_res.get('message')}")
            return 'retry_input' # Action to go back to CollectInputNode

class QuitNode(Node):
    def exec(self, prep_res):
        return "Thank you for using the Freqtrade Download Assistant!"

    def post(self, shared, prep_res, exec_res):
        print(exec_res)
        return None # End the flow

collect_input_node = CollectInputNode()
validate_input_node = ValidateInputNode()
execute_download_node = ExecuteDownloadNode()
quit_node = QuitNode()

collect_input_node - "validate" >> validate_input_node
collect_input_node - "quit" >> quit_node
validate_input_node - "execute_download" >> execute_download_node
validate_input_node - "retry_input" >> collect_input_node # Loop back on invalid input
execute_download_node - "start_over" >> collect_input_node # Loop back after successful download
execute_download_node - "retry_input" >> collect_input_node # Loop back on download error

download_flow = Flow(start=collect_input_node)

def main():
    shared_data = {} # Initialize shared data dictionary
    download_flow.run(shared_data)

if __name__ == "__main__":
    main()
