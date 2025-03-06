from pocketflow import Node

class ConfirmationNode(Node):
    def prep(self, shared):
        validated_input_values = shared['validated_input_values']
        self.confirmation_message = f"""
        \nConfirmation:
        Exchange: {validated_input_values['exchange']}
        Asset Pair: {validated_input_values['asset_pair']}
        Timeframe: {validated_input_values['timeframe']}
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
        return {}
