from pocketflow import Node

class InputNode(Node): # Class name is already InputNode, this is correct
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m" # ANSI escape code to reset color
    GRAY_COLOR_CODE = "\033[90m" # ANSI escape code for gray
    LIGHT_GREEN_COLOR_CODE = "\033[92m" # ANSI escape code for light green
    INITIAL_MESSAGE = f"""
    {LIGHT_GREEN_COLOR_CODE}Welcome to the Freqtrade Download Assistant!{RESET_COLOR_CODE}

    Please provide exchange, pair and timeframe:
    """


    def prep(self, shared):
        print(f'shared: {shared}')
        errors = shared.get('errors', [])

        prompt_lines = []

        prompt_lines.append(
            f"{self.GRAY_COLOR_CODE}  Enter 'q' or 'quit' to exit at any time.{self.RESET_COLOR_CODE}")

        if len(errors) > 0:

            user_error_message = errors.get('user_error_message', "")
            re_entry_prompt = errors.get('re_entry_prompt', "")
            prompt_lines.append(f"{self.ORANGE_COLOR_CODE}{user_error_message}{self.RESET_COLOR_CODE}")
            prompt_lines.append(f'{re_entry_prompt}: ')
        else:
            prompt_lines.append(self.INITIAL_MESSAGE)


        self.user_prompt = "\n".join(prompt_lines)
        return {}

    def _get_user_input(self, prompt):
        return input(prompt).strip()


    def exec(self, prep_res, shared):
        user_input = self._get_user_input(self.user_prompt)

        if user_input.lower() in ['q', 'quit']:
            return "exit"

        shared['last_user_input'] = user_input
        return "validate_input"

    def post(self, shared, prep_res, exec_res):
        return exec_res
