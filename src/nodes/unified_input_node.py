from pocketflow import Node
from utils.call_llm import call_llm
import yaml

class UnifiedInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange

    def prep(self, shared):
        previous_errors = shared.get('previous_errors', {})
        error_message = previous_errors.get("user_error_message", "")
        re_entry_prompt = previous_errors.get("re_entry_prompt", "")

        if error_message:
            print(f"{self.ORANGE_COLOR_CODE}Validation Error: {error_message}\033[0m") # Orange colored error message

        prompt_lines = [
            "\nPlease provide the information to download:",
            "  Enter 'q' or 'quit' to exit at any time.",
        ]
        if re_entry_prompt:
            prompt_lines.insert(1, f"  {re_entry_prompt}") # Insert re-entry prompt if available
        else:
            prompt_lines.insert(1, "  Example inputs: 'Binance BTC/USDT daily', 'Kucoin ETH/BTC 1 week', 'Coinbase ADA monthly'") # Example inputs hint

        prompt_lines.extend([
            "  Describe exchange, asset pair, and timeframe: ",
        ])

        self.user_prompt = "\n".join(prompt_lines)

        with open("src/nodes/input_extraction_prompt.txt", "r") as prompt_file:
            self.llm_prompt_template = prompt_file.read()

        return {}

    def _get_user_input(self, prompt):
        return input(prompt).strip()

    def exec(self, prep_res, shared):
        while True:
            user_input = self._get_user_input(self.user_prompt)

            if user_input.lower() in ['q', 'quit']:
                return "exit"

            llm_prompt = self.llm_prompt_template.format(user_input=user_input)
            llm_response_str = call_llm(llm_prompt)

            try:
                llm_response = yaml.safe_load(llm_response_str)
                if not isinstance(llm_response, dict):
                    raise yaml.YAMLError("LLM response is not a YAML object")

                exchange = llm_response.get("exchange")
                asset_pair = llm_response.get("asset_pair")
                timeframe = llm_response.get("timeframe")

                if not all([exchange, asset_pair, timeframe]):
                    raise ValueError("LLM response missing fields")

                current_input_to_validate = {
                    "exchange": exchange.lower(), # Standardize exchange to lowercase
                    "asset_pair": asset_pair.upper(), # Standardize asset_pair to uppercase
                    "timeframe": timeframe.lower()  # Standardize timeframe to lowercase
                }
                shared['current_input_to_validate'] = current_input_to_validate
                return "validate_input"

            except (yaml.YAMLError, ValueError) as e:
                error_message = f"Could not understand input. Please try again providing exchange, asset pair, and timeframe. Details: {e}"
                print(f"{self.ORANGE_COLOR_CODE}Input Error: {error_message}\033[0m") # Orange colored error message
                shared['previous_errors'] = {
                    "user_error_message": "Invalid input format. Please provide exchange, asset pair, and timeframe.",
                    "re_entry_prompt": "Re-enter exchange, asset pair, and timeframe (e.g., Binance BTC/USDT 1d):"
                }
                continue # Loop again if input is invalid

    def post(self, shared, prep_res, exec_res):
        return exec_res
