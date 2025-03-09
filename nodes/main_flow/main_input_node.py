from util.pocketflow import Node
import logging

logger = logging.getLogger(__name__)

class MainInputNode(Node):
    def prep(self, shared):
        user_input = input("""Welcome to the AI Trading Assistant!

Please enter your request (e.g., download assets like STOCKS, INDEXES, CRYPTO, FOREX, or other requests, or '/q' to quit):
""")
        prep_res = user_input
        logger.info(f"MainInputNode prep finished. Prep result: {prep_res}, Shared: {shared}")
        return prep_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"MainInputNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action = "default"
        if prep_res.strip().lower() == '/q':
            action = "quit" # AI: Added 'quit' action
        logger.info(f"MainInputNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
