from util.pocketflow import Node
import logging

logger = logging.getLogger(__name__)

class ChatRetrieveNode(Node):
    def prep(self, shared):
        user_input = input("You: ")
        if user_input.strip().lower() == '/q':
            return "quit" # Indicate quit command
        elif user_input.strip().startswith('/'):
            return "command_input"  # Indicate command input
        logger.info(f"ChatRetrieveNode prep finished. Prep result: {user_input}, Shared: {shared}")
        return user_input

    def exec(self, prep_res, shared):
        logger.info(f"ChatRetrieveNode exec started. Prep result: {prep_res}, Shared: {shared}")
        if prep_res == "quit":
            exec_res = {"input_type": "quit"} # Indicate quit input
        elif prep_res == "command_input":
            exec_res = {"input_type": "command"} # Indicate command input
        else:
            exec_res = {"user_input": prep_res}
        logger.info(f"ChatRetrieveNode exec finished. Exec result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"ChatRetrieveNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        if prep_res == "quit":
            action = "quit" # Action for quit
        elif prep_res == "command_input":
            action = "command_input" # Action for command input
        else:
            action = "continue"
        logger.info(f"ChatRetrieveNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
