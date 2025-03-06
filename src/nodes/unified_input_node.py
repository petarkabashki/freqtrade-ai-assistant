from pocketflow import Node

class UnifiedInputNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange

    def prep(self, shared):
        re_entry_prompt = shared.get('re_entry_prompt', "")

        prompt_lines = [
            "\nPlease provide the required information:",
            "  Enter 'q' or 'quit' to exit at any time.",
        ]
        if re_entry_prompt:
            prompt_lines.insert(1, f"  {re_entry_prompt}")
        else:
            prompt_lines.insert(1, "  Example: 'binance BTC/USDT 1d'")

        prompt_lines.extend([
            "  Your input: ",
        ])

        self.user_prompt = "\n".join(prompt_lines)
        return {}

    def _get_user_input(self, prompt):
        return input(prompt).strip()

    def exec(self, prep_res, shared):
        user_input = self._get_user_input(self.user_prompt)

        if user_input.lower() in ['q', 'quit']:
            return "exit"

        shared['last_input'] = user_input # Store raw user input in shared memory, using 'last_input' as key
        shared['current_input_to_validate'] = {'last_input': shared['last_input']} # Initialize current_input_to_validate with last_input
        return "validate_input" # Always go to validation

    def post(self, shared, prep_res, exec_res):
        return exec_res
