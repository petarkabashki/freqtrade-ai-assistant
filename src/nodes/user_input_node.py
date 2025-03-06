from pocketflow import Node
import json  # For shared memory (using a file for simplicity)

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

class UserInputNode(Node):
    def prep(self, shared):
        last_inputs = load_shared_memory()
        shared['last_inputs'] = last_inputs
        return None

    def exec(self, prep_res, shared):
        print("\nEnter 'q' to quit at any time.")
        last_inputs = shared['last_inputs']

        # Check for validation errors from previous ValidationNode run
        validation_errors = shared.get('validation_errors')
        if validation_errors:
            print("\nValidation Errors:")
            for input_type, result in validation_errors.items():
                if not result['is_valid']:
                    error_message = result.get('error', 'Unknown error')
                    print(f"- Invalid {input_type}: {error_message}")
                elif result['is_valid']:
                    print(f"- {input_type} was previously valid.")
            shared.pop('validation_errors', None)

        default_exchange = last_inputs.get('exchange') if last_inputs else None
        default_asset_pair = last_inputs.get('asset_pair') if last_inputs else None
        default_timeframe = last_inputs.get('timeframe') if last_inputs else None

        while True:
            exchange_prompt = "Exchange"
            if default_exchange:
                exchange_prompt = f"{exchange_prompt} (default: {default_exchange})"
            exchange = input(f"{exchange_prompt}: ").strip()
            if not exchange and default_exchange:
                exchange = default_exchange
            elif not exchange:
                exchange = 'binance'
            if exchange.lower() == 'q': return 'quit'

            asset_pair_prompt = "Asset Pair"
            if default_asset_pair:
                asset_pair_prompt = f"{asset_pair_prompt} (default: {default_asset_pair})"
            asset_pair = input(f"{asset_pair_prompt}: ").strip()
            if not asset_pair and default_asset_pair:
                asset_pair = default_asset_pair
            elif not asset_pair:
                asset_pair = 'BTC/USDT'
            if asset_pair.lower() == 'q': return 'quit'

            timeframe_prompt = "Timeframe"
            if default_timeframe:
                timeframe_prompt = f"{timeframe_prompt} (default: {default_timeframe})"
            timeframe = input(f"{timeframe_prompt}: ").strip()
            if not timeframe and default_timeframe:
                timeframe = default_timeframe
            elif not timeframe:
                timeframe = '1d'
            if timeframe.lower() == 'q': return 'quit'

            return {'exchange': exchange, 'asset_pair': asset_pair, 'timeframe': timeframe}

    def post(self, shared, prep_res, exec_res):
        if exec_res == 'quit':
            return 'quit'
        shared['user_input'] = exec_res
        return 'validate'
