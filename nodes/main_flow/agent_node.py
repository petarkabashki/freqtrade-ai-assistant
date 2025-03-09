from lib.pocketflow import Node
from lib.call_llm import call_llm
from lib.core_tools import search_google_tool, user_input_tool, user_output_tool # Changed tool import: user_input_llm_query_tool -> user_input_tool
from lib.tools.fs_tools import file_read, file_write, directory_listing # Import file tools
import yaml # Import the yaml library

# The agent should call llm to respond to several categories of queries. One is for downloading crypto historical data; another is for downloading stock, indeces, forex, comodities data; another is answering questions about available downloaded historical data for various assets . The folder containing the files of such downloaded data is configurable in the app yaml config and is currently 'freq-data'.
class AgentNode(Node):
    def __init__(self, max_tool_loops=3, allowed_paths=None, data_folder="freq-data"): # AI: Added data_folder to constructor
        super().__init__()
        self.max_tool_loops = max_tool_loops
        self.allowed_paths = allowed_paths if allowed_paths is not None else [] # Store allowed_paths
        self.data_folder = data_folder # AI: Store data_folder
        print(f"AgentNode initialized with max_tool_loops={max_tool_loops}, allowed_paths={allowed_paths}, data_folder={data_folder}") # AI: Log initialization

    def prep(self, shared):
        print(f"AgentNode prep started. Shared: {shared}") # AI: Log prep start
        shared['tool_loop_count'] = 0 # Initialize loop counter in shared
        prep_res = super().prep(shared)
        print(f"AgentNode prep finished. Prep result: {prep_res}, Shared: {shared}") # AI: Log prep finish
        return prep_res

    def exec(self, prep_res, shared):
        print(f"AgentNode exec started. Prep result: {prep_res}, Shared: {shared}") # AI: Log exec start
        user_input = prep_res
        prompt = f"""
        User request: {user_input}

        You are an AI assistant designed to help users manage and analyze financial data.
        You can use tools to access information.

        When the user asks about available data, you should check the contents of the '{self.data_folder}' folder using the 'directory_listing' tool.

        Available tools:
        - search_google: for general web search
        - file_read: to read content from a file
        - file_write: to write content to a file
        - directory_listing: to list files and directories in a given path
        - user_input: to ask the user a question and get their response to refine the request
        - user_output: to display information to the user

        Analyze the user request and determine:
        - Does it require an external tool? (yes/no)
        - If yes, which tool is most appropriate from the 'Available tools' list above?
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
        print(f"AgentNode LLM Response (YAML): {llm_response_yaml}") # AI: Log LLM YAML response
        try:
            llm_response_data = yaml.safe_load(llm_response_yaml)
        except yaml.YAMLError as e:
            print(f"Error parsing LLM YAML response: {e}")
            exec_res = "yaml_error"
            print(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}") # AI: Log exec finish
            return exec_res

        tool_needed = llm_response_data.get("tool_needed")
        tool_name = llm_response_data.get("tool_name")
        tool_params = llm_response_data.get("tool_params", {})

        if tool_needed == "yes":
            tool_request = { # Create tool request dictionary
                "tool_name": tool_name,
                "tool_params": tool_params
            }
            exec_res = tool_request
        else:
            llm_prompt_answer = f"User request: {user_input}\n Directly answer the request:"
            llm_answer = call_llm(llm_prompt_answer)
            shared["llm_answer"] = llm_answer
            print(f"Direct LLM Answer: {llm_answer}") # AI: Log direct LLM answer
            exec_res = "answer_directly"

        print(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}") # AI: Log exec finish
        return exec_res

    def post(self, shared, prep_res, exec_res):
        print(f"AgentNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}") # AI: Log post start
        if exec_res == "tool_needed": # Corrected: exec_res will be tool_request dict in "tool_needed" case now
            if shared['tool_loop_count'] < self.max_tool_loops: # Check loop count
                action = "tool_needed"
            else:
                print("Maximum tool loop count reached.")
                action = "max_loops_reached" # Transition for max loops reached
        elif exec_res == "answer_directly":
            action = "direct_answer_ready"
        elif exec_res == "yaml_error":
            action = "yaml_error"
        elif isinstance(exec_res, dict) and "tool_name" in exec_res: # Check if exec_res is a tool request
            action = "tool_needed" # Action indicating a tool is needed
        else:
            action = "default"

        print(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}") # AI: Log post finish
        return action
