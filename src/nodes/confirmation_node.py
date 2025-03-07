from pocketflow import Node

class ConfirmationNode(Node):
    def prep(self, shared):
        collected_values = shared['collected']
        self.confirmation_message = f"""
        \nConfirmation:
        Exchange: {collected_values['exchange']}
        Asset Pair: {collected_values['asset_pair']}
        Timeframe: {collected_values['timeframe']}
        Confirm download? (y/n): """
        return {}

    def _get_user_confirmation(self, message):
        return input(message).strip().lower()

    def exec(self, prep_res, shared):
        user_confirmation = self._get_user_confirmation(self.confirmation_message)
        if user_confirmation in ['yes', 'y']:
            return "execute_download"
        else:
            return "reinput"

    def post(self, shared, prep_res, exec_res):
        return exec_res
