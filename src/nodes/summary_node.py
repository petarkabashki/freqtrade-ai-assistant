from pocketflow import Node
from utils.call_llm import call_llm

class SummaryNode(Node):
    def prep(self, shared):
        self.download_output = shared.get('download_output')
        return {}

    def exec(self, prep_res, shared):
        # for errors the llm should provide retry/input/quit, for success or no output it should provide input/quit. Input is resetting the collected info. AI!
        if self.download_output:
            error_summary_prompt = f"""Summarize the following download output and/or error output for the user and based on it provide options: (R)etry, (I)nput , (Q)uit. Explain each option.
            -----------------------------------
            {self.download_output}
            -----------------------------------
            """
            error_summary = call_llm(error_summary_prompt)
            print("\nDownload Error Summary:")
            print("-----------------------------------")
            print(error_summary)
            print("-----------------------------------")
            print("\nChoose an action:")
            print("(R)etry: Retry the download with the same parameters.")
            print("(I)nput: Go back to input node to change parameters.")
            print("(Q)uit: Exit the program.")

            while True:
                user_choice = input("Enter action (R/I/Q): ").strip().lower()
                if user_choice in ['r', 'i', 'q']:
                    break
                else:
                    print("Invalid choice. Please enter R, I, or Q.")

            if user_choice == 'r':
                return "retry_download"
            elif user_choice == 'i':
                return "reinput"
            elif user_choice == 'q':
                return "exit"
        else:
            print("\nNo download output or error output found.")
            return "exit"

    def post(self, shared, prep_res, exec_res):
        return exec_res
