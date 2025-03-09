from lib.pocketflow import Node
from lib.call_llm import call_llm
from lib.core_tools import search_google_tool, user_input_llm_query_tool, user_output_tool # Changed tool imports
from lib.tools.fs_tools import file_read, file_write, directory_listing # Import file tools
import yaml # Import the yaml library

class AgentNode(Node):
    def __init__(self, max_tool_loops=3, allowed_paths=None): # Add allowed_paths to constructor
        super().__init__()
        self.max_tool_loops = max_tool_loops
        self.allowed_paths = allowed_paths if allowed_paths is not None else [] # Store allowed_paths

    def prep(self, shared):
        shared['tool_loop_count'] = 0 # Initialize loop counter in shared
        return super().prep(shared)

    def exec(self, prep_res, shared):
        user_input = prep_res
        prompt = f"""
        User request: {user_input}

        Analyze the user request and determine:
        - Does it require an external tool? (yes/no)
        - If yes, which tool is most appropriate from these options:
          - search_google: for general web search
          - file_read: to read content from a file
          - file_write: to write content to a file
          - directory_listing: to list files and directories in a given path
          - user_input_llm_query: to ask the user a question and get their response to refine the request
          - user_output: to display information to the user

        - What are the parameters needed to execute the tool?

        Respond in YAML format:
        ```yaml
        tool_needed: yes/no
        tool_name: <tool_name>  # e.g., search_google (if tool_needed is yes)
        tool_params:             # Parameters for the tool (if tool_needed is yes)
          <param_name_1>: <param_value_1>
        reason: <brief reason for the decision>
        ```"""
        llm_response_yaml = call_llm(prompt)
        try:
            llm_response_data = yaml.safe_load(llm_response_yaml)
        except yaml.YAMLError as e:
            print(f"Error parsing LLM YAML response: {e}")
            return "yaml_error"

        tool_needed = llm_response_data.get("tool_needed")
        tool_name = llm_response_data.get("tool_name")
        tool_params = llm_response_data.get("tool_params", {})

        if tool_needed == "yes":
            tool_request = { # Create tool request dictionary
                "tool_name": tool_name,
                "tool_params": tool_params
            }
            return tool_request # Return the tool request as exec_res
        else:
            llm_prompt_answer = f"User request: {user_input}\n Directly answer the request:"
            llm_answer = call_llm(llm_prompt_answer)
            shared["llm_answer"] = llm_answer
            print(f"Direct LLM Answer: {llm_answer}")
            return "answer_directly"

    def post(self, shared, prep_res, exec_res):
        if exec_res == "tool_needed": # Corrected: exec_res will be tool_request dict in "tool_needed" case now
            if shared['tool_loop_count'] < self.max_tool_loops: # Check loop count
                return "tool_needed" # Proceed to tool invocation if within limit
            else:
                print("Maximum tool loop count reached.")
                return "max_loops_reached" # Transition for max loops reached
        elif exec_res == "answer_directly":
            return "direct_answer_ready"
        elif exec_res == "yaml_error":
            return "yaml_error"
        elif isinstance(exec_res, dict) and "tool_name" in exec_res: # Check if exec_res is a tool request
            return "tool_needed" # Action indicating a tool is needed
        else:
            return "default"
