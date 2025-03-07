from pocketflow import Node

class ExitNode(Node):
    def exec(self, prep_res, shared):
        print("\nThanks for using the Freqtrade Download Assistant!")
        return None

    def post(self, shared, prep_res, exec_res):
        return {}
