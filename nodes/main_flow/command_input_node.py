from util.pocketflow import Node
import logging
import pprint

logger = logging.getLogger(__name__)

class CommandInputNode(Node):
    def prep(self, shared):
        user_command = shared.get('command_input', '').lower() # Get command from shared store
        if not user_command:
            user_command_input = input("Enter command (or press Enter to continue): ") # Ask for command if empty
            if not user_command_input.strip():
                return "no_command" # Indicate no command was provided if user just presses Enter
            shared['command_input'] = user_command_input.strip().lower() # Store the new command input
            user_command = shared['command_input'] # Update user_command to the new input

        user_command = user_command.lstrip('/') # Remove leading slashes here

        if user_command == 'q':
            return "quit"
        elif user_command == 'messages':
            message_history = shared.get('message_history', [])
            print("\n--- Messages History ---")
            if message_history:
                pprint.pprint(message_history)
            else:
                print("No message history available.")
            print("--- End of History ---\n")
            return "messages_history"
        elif user_command == 'shared':
            print("\n--- Shared Store ---")
            pprint.pprint(shared)
            print("--- End of Shared Store ---\n")
            return "shared_store"
        elif user_command.startswith('delete-shared '):
            path_to_delete = user_command[len('delete-shared '):]
            return "delete_shared", path_to_delete
        elif user_command in ['?', 'help']: # Added help command check
            return "help_command" # Indicate help command
        else:
            print("Unknown command. Available commands: /q, /messages, /shared, /delete-shared <path>, /?") # Added /? to available commands
            return "unknown_command", None

    def exec(self, prep_res, shared):
        user_command = shared.get('command_input', '').lower() # Get command from shared store
        if prep_res == "quit":
            return {"command": "quit", "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res == "messages_history":
            return {"command": "messages_history", "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res == "shared_store":
            return {"command": "shared_store", "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res[0] == "delete_shared":
            path_to_delete = prep_res[1]
            try:
                parts = path_to_delete.split('.')
                current = shared
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        return {"command": "delete_shared_error", "error": f"Path '{path_to_delete}' not found in shared store.", "command_prefix": self._get_command_prefix(user_command)}
                    current = current[part]
                if parts[-1] in current:
                    del current[parts[-1]]
                    return {"command": "delete_shared_success", "path_deleted": path_to_delete, "command_prefix": self._get_command_prefix(user_command)}
                else:
                    return {"command": "delete_shared_error", "error": f"Path '{path_to_delete}' not found in shared store.", "command_prefix": self._get_command_prefix(user_command)}
            except Exception as e:
                return {"command": "delete_shared_error", "error": str(e), "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res[0] == "unknown_command":
            return {"command": "unknown_command", "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res == "no_command":
            return {"command": "no_command", "command_prefix": self._get_command_prefix(user_command)}
        elif prep_res == "help_command": # Handle help command
            help_message = """
Available commands:
/q - Quit the application
/messages - Show message history
/shared - Show shared store content
/delete-shared <path> - Delete a path from the shared store (e.g., /delete-shared tool_request.tool_name)
/? or /help - Show this help message
            """
            print(help_message)
            return {"command": "help_command", "help_message": help_message, "command_prefix": self._get_command_prefix(user_command)} # Return help message in exec_res
        else:
            return {"command": "unknown", "command_prefix": self._get_command_prefix(user_command)}

    def post(self, shared, prep_res, exec_res):
        command_prefix = exec_res.get("command_prefix", "")
        if exec_res["command"] == "quit":
            return "quit"
        elif exec_res["command"] in ["messages_history", "shared_store", "delete_shared_success", "delete_shared_error", "unknown_command", "unknown", "no_command", "help_command"]: # Added help_command to action list
            if command_prefix == "//":
                action = "command_input_loop" # Action to loop back to command input for more commands
            else:
                action = "continue_input" # Action to go back to input for regular input
        elif exec_res["command"] == "no_command":
            action = "continue_input"
        else:
            action = None # No default action, should not reach here

        if 'command_input' in shared:
            del shared['command_input'] # Clear command input from shared store

        return action
    def _get_command_prefix(self, user_command):
        if user_command.startswith('//'):
            return "//"
        elif user_command.startswith('/'):
            return "/"
        return ""
