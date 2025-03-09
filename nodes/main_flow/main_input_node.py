from lib.pocketflow import Node
class MainInputNode(Node):
    def prep(self, shared): # make sure there are no leading blanks.
        user_input = input("""
                           Welcome to the AI Trading Assistant! 
                           
                           Please enter your request (e.g., download assets like STOCKS, INDEXES, CRYPTO, FOREX, or other requests): 
                           """)
        prep_res = user_input
        print(f"MainInputNode prep finished. Prep result: {prep_res}, Shared: {shared}") # AI: Log prep finish
        return prep_res

    def post(self, shared, prep_res, exec_res):
        print(f"MainInputNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}") # AI: Log post start
        action = "default" # Always default action to proceed in the flow
        print(f"MainInputNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}") # AI: Log post finish
        return "default"
