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
                pprint.pprint(message_history)
            else:
                print("No message history available.")
            print("--- End of History ---\n")
            return "message_history"
        elif user_input.strip().lower() == '/shared':
            print("\n--- Shared Store ---")
            pprint.pprint(shared)
            print("--- End of Shared Store ---\n")
            return "shared_store"
        elif user_input.strip().lower().startswith('/delete-shared '):
            path_to_delete = user_input.strip().lower()[len('/delete-shared '):]
            return "delete_shared", path_to_delete
        else:
            print("Unknown command. Available commands: /q, /message-history, /shared, /delete-shared <path>")
            return "unknown_command", None

    def exec(self, prep_res, shared):
        if prep_res[0] == "quit":
            return {"command": "quit"}
        elif prep_res[0] == "message_history":
            return {"command": "message_history"}
        elif prep_res[0] == "shared_store":
            return {"command": "shared_store"}
        elif prep_res[0] == "delete_shared":
            path_to_delete = prep_res[1]
            try:
                parts = path_to_delete.split('.')
                current = shared
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        return {"command": "delete_shared_error", "error": f"Path '{path_to_delete}' not found in shared store."}
                    current = current[part]
                if parts[-1] in current:
                    del current[parts[-1]]
                    return {"command": "delete_shared_success", "path_deleted": path_to_delete}
                else:
                    return {"command": "delete_shared_error", "error": f"Path '{path_to_delete}' not found in shared store."}
            except Exception as e:
                return {"command": "delete_shared_error", "error": str(e)}
        elif prep_res[0] == "unknown_command":
            return {"command": "unknown_command"}
        else:
            return {"command": "unknown"}

    def post(self, shared, prep_res, exec_res):
        if exec_res["command"] == "quit":
            return "quit"
        elif exec_res["command"] in ["message_history", "shared_store", "delete_shared_success", "delete_shared_error", "unknown_command", "unknown"]:
            return "continue_input" # Action to go back to input for more commands or regular input
        else:
            return None # No default action, should not reach here
