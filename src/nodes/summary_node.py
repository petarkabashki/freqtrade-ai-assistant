from pocketflow import Node

# Make this node accept pass the download command output to the llm to summarize it for the user. If it's an error provide the following options: (R)etry, (I)nput , (Q)uit. Retry should go back to the download and try again. Input should go back to the input node. Quit -> exit node. AI!
class SummaryNode(Node):
    def prep(self, shared):
        self.command_output = shared['command_output']
        return {}

    def exec(self, prep_res, shared):
        print("\nDownload Command Output:")
        print("-----------------------------------")
        print(self.command_output)
        print("-----------------------------------")
        return "exit"

    def post(self, shared, prep_res, exec_res):
        return "exit"
