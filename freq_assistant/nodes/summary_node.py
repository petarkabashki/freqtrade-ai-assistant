from lib.pocketflow import Node
from lib.call_llm import call_llm

class SummaryNode(Node):
    def prep(self, shared):
        self.download_output = shared.get('download_output')
        self.download_success = shared.get('download_success')
        return {}

    def exec(self, prep_res, shared):
        if self.download_success:
            success_summary_prompt = f"""Summarize the following download output for the user and based on it provide options: (I)nput , (Q)uit. Explain each option. Input is to request new download parameters(exchange, pair, timeframe).
            If the download output is empty, assume it was successful.
            -----------------------------------
            {self.download_output}
            -----------------------------------
            """
            summary = call_llm(success_summary_prompt)
            print("\nDownload Summary:")
            print("-----------------------------------")
            print(summary)
            print("-----------------------------------")
            print("\nChoose an action:")
            print("(I)nput: Go back to input node to change parameters and reset collected info.")
            print("(Q)uit: Exit the program.")


            while True:
                user_choice = input("Enter action (Input/Quit) [I]: ").strip().lower()
                if not user_choice:
                    user_choice = 'i'
                    break
                if user_choice in ['i', 'q']:
                    break
                else:
                    print("Invalid choice. Please enter I, or Q.")


            if user_choice == 'i':
                shared['collected'] = {} # reset collected info
                shared['anew'] = True
                return "input"
            elif user_choice == 'q':
                return "exit"


        else:
            error_summary_prompt = f"""Summarize the following error output for the user and based on it provide options: (R)etry, (I)nput , (Q)uit. Explain each option.
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
            print("(R/I/Q)[R]: ")

            while True:
                user_choice = input("Enter action (R/I/Q)[R]: ").strip().lower()
                if not user_choice:
                    user_choice = 'r'
                    break
                if user_choice in ['r', 'i', 'q']:
                    break
                else:
                    print("Invalid choice. Please enter R, I, or Q.")

            if user_choice == 'r':
                return "retry_download"
            elif user_choice == 'i':
                shared['collected'] = {} # reset collected info
                return "reinput"
            elif user_choice == 'q':
                return "exit"


    def post(self, shared, prep_res, exec_res):
        return exec_res
