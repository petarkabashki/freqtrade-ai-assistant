from pocketflow import Node

class UnifiedInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m" # ANSI escape code to reset color
    GRAY_COLOR_CODE = "\033[90m" # ANSI escape code for gray

    def prep(self, shared):
        print(f'shared: {shared}')
        errors = shared.get('errors', [])

        prompt_lines = [
            "\nPlease provide exchange, pair and timeframe",
        ]
        if len(errors) > 0:

            user_error_message = errors.get('user_error_message', "")
            re_entry_prompt = errors.get('re_entry_prompt', "")
            prompt_lines.append(f"{self.ORANGE_COLOR_CODE}{user_error_message}{self.RESET_COLOR_CODE}")
            prompt_lines.append(re_entry_prompt) # corrected line: append re_entry_prompt to prompt_lines
        else:
            prompt_lines.insert(1, "  Example: 'binance BTC/USDT 1d'")

        #wrap this line in gray color AI!
        prompt_lines.append(
            f"{self.GRAY_COLOR_CODE}  Enter 'q' or 'quit' to exit at any time.\n Please enter: {self.RESET_COLOR_CODE}")

        self.user_prompt = "\n".join(prompt_lines)
        return {} # corrected line: return empty dict as prep_res

    def _get_user_input(self, prompt):
        return input(prompt).strip()


    def exec(self, prep_res, shared): # corrected line: add prep_res argument
        user_input = self._get_user_input(self.user_prompt)

        if user_input.lower() in ['q', 'quit']:
            return "exit"

        shared['last_user_input'] = user_input # Store raw user input in shared memory, using 'last_input' as key
        return "validate_input" # Always go to validation

    def post(self, shared, prep_res, exec_res): # corrected line: use standard post method signature
        return exec_res
