from pocketflow import Node

class UnifiedInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange

    def prep(self, shared):
        previous_errors = shared.get('previous_errors', {})
        error_message = previous_errors.get("user_error_message", "")
        re_entry_prompt = previous_errors.get("re_entry_prompt", "")

        if error_message:
            print(f"{self.ORANGE_COLOR_CODE}Validation Error: {error_message}\033[0m") # Orange colored error message

        prompt_lines = [
            "\nPlease provide the following information to download ",
            "  Enter 'q' or 'quit' to exit at any time.",
        ]
        if re_entry_prompt:
            prompt_lines.insert(1, f"  {re_entry_prompt}") # Insert re-entry prompt if available
        else:
            prompt_lines.insert(1, "  Which exchange, asset pair, and timeframe do you want to download?") # Default prompt

        prompt_lines.extend([
            "  (e.g., binance BTC/USDT 1d): ",
        ])

        self.user_prompt = "\n".join(prompt_lines)
        return {}

    def _get_user_input(self, prompt):
        return input(prompt).strip()

    def exec(self, prep_res, shared):
        while True:
            user_input = self._get_user_input(self.user_prompt)

            if user_input.lower() in ['q', 'quit']:
                return "exit"

            parts = user_input.split()
            if len(parts) >= 3:
                exchange, asset_pair_base, timeframe = parts[0], parts[1], parts[2]
                asset_pair = f"{asset_pair_base.upper()}/USDT" if "/" not in asset_pair_base else asset_pair_base.upper() # Default QUOTE to USDT
                current_input_to_validate = {
                    "exchange": exchange.lower(), # Standardize exchange to lowercase
                    "asset_pair": asset_pair,
                    "timeframe": timeframe.lower()  # Standardize timeframe to lowercase
                }
                shared['current_input_to_validate'] = current_input_to_validate
                return "validate_input"
            else:
                print(f"{self.ORANGE_COLOR_CODE}Invalid input format. Please provide exchange, asset pair, and timeframe.\033[0m") # Orange colored error message
                continue # Loop again if input is invalid

    def post(self, shared, prep_res, exec_res):
        return {}
