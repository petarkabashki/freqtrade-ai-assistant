from lib.pocketflow import Node

class MainInputNode(Node):
    def prep(self, shared):
        user_input = input("User Input: ")
        return user_input

    def post(self, shared, prep_res, exec_res):
        shared['user_input'] = prep_res
        return "llm"
