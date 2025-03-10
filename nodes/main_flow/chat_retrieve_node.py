from util.pocketflow import Node
from util.call_llm import get_embedding
import logging

logger = logging.getLogger(__name__)

class ChatRetrieveNode(Node):
    def prep(self, shared):
        shared.setdefault("history", [])
        shared.setdefault("memory_index", None)
        user_input = input("You: ")
        if user_input.strip().lower() == '/q':
            return "quit"  # Return "quit" as prep_res if user input is '/q'
        logger.info(f"ChatRetrieveNode prep finished. Prep result: {user_input}, Shared: {shared}")
        return user_input

    def exec(self, prep_res, shared):
        user_input = prep_res
        if user_input == "quit": # Handle quit case
            return "quit"

        logger.info(f"ChatRetrieveNode exec started. Prep result: {prep_res}, Shared: {shared}")
        embedding = get_embedding(user_input)
        logger.info(f"ChatRetrieveNode exec finished. Prep result: {prep_res}, Exec result: {(user_input, [])}, Shared: {shared}") # Keep consistent exec result format
        return user_input, [] # Return user_input and relevant messages (empty for now)

    def post(self, shared, prep_res, exec_res):
        user_input = prep_res
        logger.info(f"ChatRetrieveNode post finished. Action: continue, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        if user_input != "quit":
            message_history = shared.get('message_history', [])
            message_history.append({"role": "user", "content": user_input}) # Add user input to message history
            shared['message_history'] = message_history
            return "continue"
        else:
            return "quit"
