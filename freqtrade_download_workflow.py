from pocketflow import Flow, Node
import subprocess
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# Utility function for LLM calls
def call_llm(prompt):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Read API key from environment variable
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Specify the model
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None

class CollectExchangeNode(Node):
    def prep(self, shared):
        default_exchange = shared.get('exchange', '')
        return {'default_exchange': default_exchange}

    def exec(self, prep_res):
        default_exchange = prep_res.get('default_exchange', '')
        exchange = input(f"Enter exchange (binance, ftx, kucoin, coinbase) or 'q' to quit (default: {default_exchange}): ").lower()
        if exchange == 'q':
            return {'action': 'quit'}
        return {'exchange': exchange}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('action') == 'quit':
            return 'quit'
        shared['exchange'] = exec_res.get('exchange')
        return 'collect_pair'

class CollectPairNode(Node):
    def prep(self, shared):
        default_pair = shared.get('pair', '')
        return {'default_pair': default_pair}

    def exec(self, prep_res):
        default_pair = prep_res.get('default_pair', '')
        pair = input(f"Enter pair (e.g., BTC/USDT) (default: {default_pair}): ").upper()
        return {'pair': pair}

    def post(self, shared, prep_res, exec_res):
        shared['pair'] = exec_res.get('pair')
        return 'collect_timeframe'

class CollectTimeframeNode(Node):
    def prep(self, shared):
        default_timeframe = shared.get('timeframe', '')
        return {'default_timeframe': default_timeframe}

    def exec(self, prep_res):
        default_timeframe = prep_res.get('default_timeframe', '')
        timeframe = input(f"Enter timeframe (1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y) (default: {default_timeframe}): ").lower()
        return {'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        shared['timeframe'] = exec_res.get('timeframe')
        return 'validate_all_inputs'

class ExecuteDownloadNode(Node):
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

        command = [
            "freqtrade", "download-data",
            "--userdir", "./freq-user-data",
            "--data-format-ohlcv", "json",
            "--exchange", exchange,
            "-t", timeframe,
            "--timerange=20200101-",
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
            shared['last_exchange'] = prep_res['exchange']
            shared['last_pair'] = prep_res['pair']
            shared['last_timeframe'] = prep_res['timeframe']
            return 'collect_exchange'
        else:
            print(f"Download Error: {exec_res.get('message')}")
            return 'collect_exchange'

class QuitNode(Node):
    def exec(self, prep_res):
        return "Thank you for using the Freqtrade Download Assistant!"

    def post(self, shared, prep_res, exec_res):
        print(exec_res)
        return None

class ValidateAllInputsNode(Node):
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

        prompt = f"""
        You are a validation assistant for the Freqtrade download assistant.
        Validate the following user inputs for a freqtrade download command.
        Return a YAML structure with a validation status and instructions for the next action.

        Exchange: {exchange}
        Pair: {pair}
        Timeframe: {timeframe}

        Here are the validation rules:
        - Exchange: Must be one of (binance, ftx, kucoin, coinbase).
        - Pair: Must be in the form of BASE/QUOTE, in which BTC is the base and USDT is the quote. If no quote part is given, assume USDT.
        - Timeframe: Must be one of (1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y).

        The YAML structure should contain:
        - 'validation_status': OK or NOT_OK.
        - If NOT_OK, include:
            - 'error_messages': A list of dictionaries, each with 'field' and 'message' keys, describing the validation errors.
            - 'next_action':  A string indicating which input to retry: 'retry_exchange', 'retry_pair', 'retry_timeframe', or 'retry_all' if unclear.
        - If OK, include:
            - 'next_action': 'execute_download'

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
        llm_response = call_llm(prompt)
        if llm_response:
            try:
                validation_result = yaml.safe_load(llm_response)
                return validation_result
            except yaml.YAMLError as e:
                print(f"Error parsing LLM response as YAML: {e}")
                return {'validation_status': 'NOT_OK',
                        'error_messages': [{'field': 'all', 'message': 'Failed to parse LLM response.'}],
                        'next_action': 'retry_all'}
        else:
            return {'validation_status': 'NOT_OK',
                    'error_messages': [{'field': 'all', 'message': 'LLM call failed.'}],
                    'next_action': 'retry_all'}

    def post(self, shared, prep_res, exec_res):
        if exec_res.get('validation_status') == 'NOT_OK':
            print("Validation errors:")
            for error in exec_res.get('error_messages', []):
                print(f"  - {error['field']}: {error['message']}")
            next_action = exec_res.get('next_action', 'collect_exchange')
            if next_action == 'retry_exchange':
                return 'collect_exchange'
            elif next_action == 'retry_pair':
                return 'collect_pair'
            elif next_action == 'retry_timeframe':
                return 'collect_timeframe'
            elif next_action == 'retry_all':
                return 'collect_exchange'  # Default to retry exchange
            else:
                return 'collect_exchange'  # Default to retry exchange
        elif exec_res.get('next_action') == 'execute_download':
            return 'execute_download'
        else:
            return 'collect_exchange'

# Instantiate nodes
validate_all_inputs_node = ValidateAllInputsNode()
collect_pair_node = CollectPairNode()
collect_timeframe_node = CollectTimeframeNode()
execute_download_node = ExecuteDownloadNode()
quit_node = QuitNode()
collect_exchange_node = CollectExchangeNode()

# Define flow
collect_exchange_node - "quit" >> quit_node
collect_exchange_node >> collect_pair_node
collect_pair_node >> collect_timeframe_node
collect_timeframe_node >> validate_all_inputs_node
validate_all_inputs_node - "execute_download" >> execute_download_node
validate_all_inputs_node - "collect_exchange" >> collect_exchange_node
validate_all_inputs_node - "collect_pair" >> collect_pair_node
validate_all_inputs_node - "collect_timeframe" >> collect_timeframe_node
execute_download_node >> collect_exchange_node # on success or error, retry from the beginning

download_flow = Flow(start=collect_exchange_node)

def main():
    shared_data = {}
    download_flow.run(shared_data)

if __name__ == "__main__":
    main()
