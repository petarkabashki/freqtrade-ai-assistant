from pocketflow import Node

class ExitNode(Node):
    def exec(self, prep_res, shared):
        print("\nThank you for using the Freqtrade Download Assistant!")
        return None # No output

    def post(self, shared, prep_res, exec_res):
        return None # End of flow
