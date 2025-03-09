from lib.pocketflow import Node
# Greet the user with a welcoming message to the AI Trading Assistant, ask them to enter their request for downloading assets (STOCKS, INDEXES, CRYPTO, FOREX) or other requests. AI!
class MainInputNode(Node):
    def prep(self, shared):
        user_input = input("User Input: ")
        return user_input

    def post(self, shared, prep_res, exec_res):
        shared['user_input'] = prep_res
        return "llm"
