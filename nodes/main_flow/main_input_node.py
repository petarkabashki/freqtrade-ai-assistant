from lib.pocketflow import Node
class MainInputNode(Node):
    def prep(self, shared):
        user_input = input("""
                           Welcome to the AI Trading Assistant! 
                           
                           Please enter your request (e.g., download assets like STOCKS, INDEXES, CRYPTO, FOREX, or other requests): 
                           """)
        prep_res = user_input
        print(f"MainInputNode prep finished. Prep result: {prep_res}, Shared: {shared}")
        return prep_res

    def post(self, shared, prep_res, exec_res):
        print(f"MainInputNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action = "default"
        print(f"MainInputNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return "default"
