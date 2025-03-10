from util.pocketflow import Node
import logging
import pprint

logger = logging.getLogger(__name__)

class CommandInputNode(Node):
    def prep(self, shared):
        user_input = input("Enter command: ")
        if user_input.strip().lower() == '/q':
            return "quit"
        elif user_input.strip().lower() == '/message-history':
            message_history = shared.get('message_history', [])
            print("\n--- Message History ---")
            if message_history:
                for msg in message_history:
                    print(f"- {msg['role']}: {msg['content']}")
            else:
                print("No message history available.")
            print("--- End of History ---\n")
            return "message_history"
        elif user_input.strip().lower() == '/shared':
            print("\n--- Shared Store ---")
            pprint.pprint(shared)
            print("--- End of Shared Store ---\n")
            return "shared_store"
        else:
            print("Unknown command. Available commands: /q, /message-history, /shared")
            return "unknown_command"

    def exec(self, prep_res, shared):
        if prep_res == "quit":
            return {"command": "quit"}
        elif prep_res == "message_history":
            return {"command": "message_history"}
        elif prep_res == "shared_store":
            return {"command": "shared_store"}
        elif prep_res == "unknown_command":
            return {"command": "unknown_command"}
        else:
            return {"command": "unknown"}

    def post(self, shared, prep_res, exec_res):
        if exec_res["command"] == "quit":
            return "quit"
        elif exec_res["command"] in ["message_history", "shared_store", "unknown_command", "unknown"]:
            return "continue_input" # Action to go back to input for more commands or regular input
        else:
            return None # No default action, should not reach here
