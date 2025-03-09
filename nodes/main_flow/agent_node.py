from lib.pocketflow import Node
from lib.call_llm import call_llm
from lib.core_tools import search_google_tool, user_input_tool, user_output_tool # Changed tool import: user_input_llm_query_tool -> user_input_tool
from lib.tools.fs_tools import file_read, file_write, directory_listing # Import file tools
import yaml # Import the yaml library

# The agent should call llm to respond to several categories of queries.
# One is for downloading crypto historical data; another is for downloading
# stock, indeces, forex, comodities data; another is answering questions
# about available downloaded historical data for various assets .
# The folder containing the files of such downloaded data is configurable
# in the app yaml config and is currently 'freq-data'.
class AgentNode(Node):
    def __init__(self, max_tool_loops=3, allowed_paths=None, data_folder="freq-data"):
        super().__init__()
        self.max_tool_loops = max_tool_loops
        self.allowed_paths = allowed_paths if allowed_paths is not None else [] # Store allowed_paths
        self.data_folder = data_folder
        print(f"AgentNode initialized with max_tool_loops={max_tool_loops}, allowed_paths={allowed_paths}, data_folder={data_folder}")

    def prep(self, shared):
        print(f"AgentNode prep started. Shared: {shared}")
        shared['tool_loop_count'] = 0 # Initialize loop counter in shared
        prep_res = super().prep(shared)
        print(f"AgentNode prep finished. Prep result: {prep_res}, Shared: {shared}")
        return prep_res

    def exec(self, prep_res, shared):
        print(f"AgentNode exec started. Prep result: {prep_res}, Shared: {shared}")
        user_input = prep_res
        prompt = f"""
        User request: {user_input}

        You are an AI assistant designed to help users manage and analyze
        financial data, including cryptocurrency data.
        You can use tools to access information and perform actions.

        When the user asks about:
        - **downloading cryptocurrency data**: This is a **CRITICAL** category.
          It includes explicit requests to download historical data for
          cryptocurrencies. Keywords indicating this intent are "download",
          "get history", "historical data" combined with cryptocurrency
          symbols (like BTC, ETH, ADA, SOL) and optional timeframes (like
          "daily", "weekly", "1d", "1w", "4h").
          **Examples of crypto download requests:**
          - "download bitcoin data"
          - "get ETH/USD history"
          - "download cardano on weekly timeframe"
          - "download solana weekly"
          - "download BTC/USDT daily"
          - "download ADA/USDT 1w"
          - "get historical data for ETH/BTC 4h"
          - "download crypto data for SOL/USD"

          If the user request **clearly and explicitly** asks to download
          cryptocurrency data, even if it includes a timeframe, **you MUST
          identify it as a crypto download request.** You should transition to
          a separate 'freqtrade flow' to handle this request.  **Do not
          attempt to use any tools for crypto download requests in this
          flow.**

          **Indicate a crypto download request by responding with:**
          `tool_needed: no` and set `action: crypto_download_requested`.
          The `reason` should be: "User requested cryptocurrency data
          download, which is handled by a separate flow."

        - **available data**: If the user asks what data is available or what
          files are present, use the 'directory_listing' tool to check the
          contents of the '{self.data_folder}' folder.
        - **questions about the data itself** (e.g., "average price of BTC",
          "what is the latest price of ETH"): Use the 'file_read' tool to
          read the contents of the relevant data files in the
          '{self.data_folder}' folder and then answer the question based on
          the data.

        Available tools:
        - search_google: for general web search
        - file_read: to read content from a file in the '{self.data_folder}' folder
        - file_write: to write content to a file in the '{self.data_folder}' folder
        - directory_listing: to list files and directories in the '{self.data_folder}' folder
        - user_input: to ask the user a question and get their response to
          refine the request
        - user_output: to display information to the user

        Analyze the user request and determine:
        - Does the user request fall into the **CRITICAL** category of
          "downloading cryptocurrency data"? If yes, respond immediately to
          trigger the 'freqtrade flow'.
        - For other types of requests: Does it require an external tool from
          the 'Available tools' list to answer the user request *directly
          within this flow*? (yes/no)
        - If yes (for non-crypto-download requests), which tool is most
          appropriate from the 'Available tools' list above?
        - What are the parameters needed to execute the tool?
        - If the request is to download cryptocurrency data, what is a brief
          reason for transitioning to the 'freqtrade flow'?

        Respond in YAML format:
        ```yaml
        tool_needed: yes/no  # MUST be 'no' for crypto download requests
        tool_name: <tool_name>  # e.g., directory_listing (if tool_needed is yes for non-crypto requests) or None (if tool_needed is no, including crypto download requests)
        tool_params:             # Parameters for the tool (if tool_needed is yes for non-crypto requests) - MUST be empty for crypto download requests
          <param_name_1>: <param_value_1>
        reason: <brief reason for the decision> # MUST clearly state "User requested cryptocurrency data download, which is handled by a separate flow." for crypto download requests.
        action: <action_indicator> # MUST be 'crypto_download_requested' if request is to download crypto data, otherwise None for crypto download requests, or other action if tool is needed in this flow.
        ```"""
        llm_response_yaml = call_llm(prompt)
        print(f"AgentNode LLM Response (YAML): {llm_response_yaml}")
        try:
            llm_response_data = yaml.safe_load(llm_response_yaml)
        except yaml.YAMLError as e:
            print(f"Error parsing LLM YAML response: {e}")
            exec_res = "yaml_error"
            print(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
            return exec_res

        tool_needed = llm_response_data.get("tool_needed")
        tool_name = llm_response_data.get("tool_name")
        tool_params = llm_response_data.get("tool_params", {})
        action_indicator = llm_response_data.get("action")

        if tool_needed == "yes":
            tool_request = { # Create tool request dictionary
                "tool_name": tool_name,
                "tool_params": tool_params
            }
            exec_res = tool_request
        elif action_indicator == "crypto_download_requested":
            exec_res = "crypto_download_requested"
        else:
            llm_prompt_answer = f"User request: {user_input}\n Directly answer the request:"
            llm_answer = call_llm(llm_prompt_answer)
            shared["llm_answer"] = llm_answer
            print(f"Direct LLM Answer: {llm_answer}")
            exec_res = "answer_directly"

        print(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        print(f"AgentNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
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
        elif exec_res == "crypto_download_requested":
            action = "crypto_download_requested"
        elif isinstance(exec_res, dict) and "tool_name" in exec_res: # Check if exec_res is a tool request
            action = "tool_needed" # Action indicating a tool is needed
        else:
            action = "default"

        print(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
