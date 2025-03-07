from pocketflow import Node

class UnifiedInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange

    def prep(self, shared):
        re_entry_prompt = shared.get('re_entry_prompt', "")
        errors = shared.get('errors', [])

        prompt_lines = [
            "\nPlease provide exchange, pair and timeframe",
        ]
        if re_entry_prompt:
            prompt_lines.append(re_entry_prompt) # corrected line: append re_entry_prompt to prompt_lines
        else:
            prompt_lines.insert(1, "  Example: 'binance BTC/USDT 1d'")

        prompt_lines.append(
            "  Enter 'q' or 'quit' to exit at any time.\n Please enter: ")

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
