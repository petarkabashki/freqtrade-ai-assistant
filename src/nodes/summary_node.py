from pocketflow import Node
from utils.call_llm import call_llm

# Make this node accept pass the download command output to the llm to summarize it for the user. If it's an error provide the following options: (R)etry, (I)nput , (Q)uit. Retry should go back to the download and try again. Input should go back to the input node. Quit -> exit node. AI!
class SummaryNode(Node):
    def prep(self, shared):
        # Use download_output if download was successful, otherwise use command_output for errors. AI!
        self.download_output = shared.get('download_output')
        self.command_output = shared.get('command_output')
        return {}

    def exec(self, prep_res, shared):
        if self.download_output:
            # Summarize successful download output. AI!
            summary_prompt = f"""Summarize the following download output for the user:
            -----------------------------------
            {self.download_output}
            -----------------------------------
            """
            summary = call_llm(summary_prompt)
            print("\nDownload Summary:")
            print("-----------------------------------")
            print(summary)
            print("-----------------------------------")
            return "exit" # For successful download, go to exit. AI!
        elif self.command_output:
            # Summarize error and provide options. AI!
            error_summary_prompt = f"""Summarize the following error output for the user and based on it provide options: (R)etry, (I)nput , (Q)uit. Explain each option.
            -----------------------------------
            {self.command_output}
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
                return "retry_download" # Action for retry download. AI!
            elif user_choice == 'i':
                return "reinput" # Action for going back to input. AI!
            elif user_choice == 'q':
                return "exit" # Action for exit. AI!
        else:
            # This case should ideally not happen, but handle it just in case. AI!
            print("\nNo download output or error output found.")
            return "exit"

    def post(self, shared, prep_res, exec_res):
        return exec_res
