from pocketflow import Node

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
        return {}
