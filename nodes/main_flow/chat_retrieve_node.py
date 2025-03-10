from util.pocketflow import Node
import logging

logger = logging.getLogger(__name__)

class ChatRetrieveNode(Node):
    def prep(self, shared):
        # shared.setdefault("history", []) # AI: Removed unused history
        # shared.setdefault("memory_index", None) # AI: Removed unused memory_index
        user_input = input("You: ")
        if user_input.strip().lower() == '/q':
            return "quit"  # Return "quit" as prep_res if user input is '/q'
        if user_input.strip().lower() == '/message-history':
            message_history = shared.get('message_history', [])
            print("\n--- Message History ---")
            if message_history:
                for msg in message_history:
                    print(f"- {msg['role']}: {msg['content']}")
            else:
                print("No message history available.")
            print("--- End of History ---\n")
            return "command_executed"  # Return "command_executed" when command is handled
        logger.info(f"ChatRetrieveNode prep finished. Prep result: {user_input}, Shared: {shared}")
        return user_input

    def exec(self, prep_res, shared):
        logger.info(f"ChatRetrieveNode exec started. Prep result: {prep_res}, Shared: {shared}")
        if prep_res == "quit" or prep_res == "command_executed": # Handle quit and command_executed directly in prep and post
            exec_res = {"input_command": prep_res} # or just pass prep_res as exec_res
        else:
            exec_res = {"user_input": prep_res}
        logger.info(f"ChatRetrieveNode exec finished. Exec result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"ChatRetrieveNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        if prep_res == "quit":
            action = "quit" # Correctly set action to quit for '/q' command
        elif prep_res == "command_executed":
            action = None # No action needed, loop in input node
        else:
            action = "continue"
        logger.info(f"ChatRetrieveNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
