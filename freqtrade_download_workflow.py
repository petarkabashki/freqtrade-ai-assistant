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

        # VERY EXPLICIT CHECK RIGHT BEFORE ACCESS
        if prep_res is None or not isinstance(prep_res, dict):
            raise ValueError("CRITICAL ERROR: prep_res is None or not a dict right before accessing prep_res['exchange']!")


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
        return 'validate_exchange'

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
        return 'validate_pair'

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


validate_exchange_node = ValidateExchangeNode()
collect_pair_node = CollectPairNode()
validate_pair_node = ValidatePairNode()
collect_timeframe_node = CollectTimeframeNode()
validate_timeframe_node = ValidateTimeframeNode()
execute_download_node = ExecuteDownloadNode()
quit_node = QuitNode()

collect_exchange_node - "validate_exchange" >> validate_exchange_node
collect_exchange_node - "quit" >> quit_node

validate_exchange_node - "collect_pair" >> collect_pair_node
validate_exchange_node - "retry_exchange" >> collect_exchange_node

collect_pair_node - "validate_pair" >> validate_pair_node
validate_pair_node - "collect_timeframe" >> collect_timeframe_node
validate_pair_node - "retry_pair" >> collect_pair_node

collect_timeframe_node - "validate_timeframe" >> validate_timeframe_node
validate_timeframe_node - "execute_download" >> execute_download_node
validate_timeframe_node - "retry_timeframe" >> collect_timeframe_node

execute_download_node - "start_over" >> collect_exchange_node
execute_download_node - "retry_input" >> collect_exchange_node

download_flow = Flow(start=collect_exchange_node)

def main():
    shared_data = {} # Initialize shared data dictionary
    download_flow.run(shared_data)

if __name__ == "__main__":
    main()
