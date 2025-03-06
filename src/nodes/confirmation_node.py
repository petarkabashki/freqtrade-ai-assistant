from pocketflow import Node

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
