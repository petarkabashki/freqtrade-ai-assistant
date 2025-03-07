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
            prompt_lines = errors.append(re_entry_prompt)
        else:
            prompt_lines.insert(1, "  Example: 'binance BTC/USDT 1d'")

        prompt_lines.append(
            "  Enter 'q' or 'quit' to exit at any time.\n Please enter: ")
        
        user_prompt = "\n".join(prompt_lines)
        user_input = input(user_prompt)
        return user_input


    def exec(self, user_input, shared):
        print(f"user_input: {user_input}")
        print(f"shared: {shared}")

        if user_input.lower() in ['q', 'quit']:
            return "exit"

        shared['last_user_input'] = user_input # Store raw user input in shared memory, using 'last_input' as key
        return "validate_input" # Always go to validation

    def post(self, exec_res):
        return exec_res
