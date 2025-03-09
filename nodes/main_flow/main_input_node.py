from lib.pocketflow import Node
class MainInputNode(Node):
    def prep(self, shared):
        user_input = input("""
                           Welcome to the AI Trading Assistant! 
                           
                           Please enter your request (e.g., download assets like STOCKS, INDEXES, CRYPTO, FOREX, or other requests): 
                           """)
        return user_input

    def post(self, shared, prep_res, exec_res):
        shared['user_input'] = prep_res
        return "llm"
