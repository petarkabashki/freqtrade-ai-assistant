from util.pocketflow import Node
from util.call_llm import call_llm
import yaml
import logging

logger = logging.getLogger(__name__)

class AgentNode(Node):
    def __init__(self, max_tool_loops=3, allowed_paths=None,
                 data_folder="freq-data", message_history_limit=5):
        super().__init__()
        self.max_tool_loops = max_tool_loops
        self.allowed_paths = allowed_paths if allowed_paths is not None else []
        self.data_folder = data_folder
        self.message_history_limit = message_history_limit
        logger.info(f"AgentNode initialized with max_tool_loops={max_tool_loops}, "
              f"allowed_paths={allowed_paths}, data_folder={data_folder}, message_history_limit={message_history_limit}")

    def prep(self, shared):
        logger.info(f"AgentNode prep started. Shared: {shared}")
        shared['tool_loop_count'] = 0
        if 'message_history' not in shared:
            shared['message_history'] = []
        prep_res = super().prep(shared)
        logger.info(f"AgentNode prep finished. Prep result: {prep_res}, Shared: {shared}")
        return prep_res

    def exec(self, prep_res, shared):
        logger.info(f"AgentNode exec started. Prep result: {prep_res}, Shared: {shared}")
        user_input = prep_res
        message_history = shared.get('message_history', [])

        history_text = ""
        if message_history:
            history_text = "Message History:\n"
            for msg in message_history:
                history_text += f"- User: {msg['user_input']}\n"
                history_text += f"- Assistant: {msg['llm_response']}\n"

        prompt = f"""
        {history_text}
        User request: {user_input}

        You are an AI assistant designed to help users manage and analyze
        financial data, including cryptocurrency data, stocks, indexes and forex.
        You can use tools to access information and perform actions.

        Analyze the user request to determine the user intent and whether a tool is needed.

        Here are the categories of user requests and how to handle them:

        1. **Cryptocurrency Data Download Request**:
           - **Category**: **CRITICAL**. Explicit requests to download historical data for cryptocurrencies.
           - **Keywords**: "download", "get history", "historical data" combined with cryptocurrency symbols (like BTC, ETH, ADA, SOL) and optional timeframes (like "daily", "weekly", "1d", "1w", "4h").
           - **Examples**:
             - "download bitcoin data"
             - "get ETH/USD history"
             - "download cardano on weekly timeframe"
             - "download solana weekly"
             - "download BTC/USDT daily"
             - "download ADA/USDT 1w"
             - "get historical data for ETH/BTC 4h"
             - "download crypto data for SOL/USD"
           - **Handling**: If the user request **clearly and explicitly** asks to download cryptocurrency data, even with a timeframe, identify it as a crypto download request. Transition to the 'freqtrade flow'. **Do not use tools for crypto download requests in this flow.**
           - **Response**:
             ```yaml
             tool_needed: no
             tool_name: None
             tool_params: {{}}
             reason: "User requested cryptocurrency data download, which is handled by a separate flow."
             action: crypto_download_requested
             ```

        2. **General Information Seeking Request**:
           - **Category**: General questions about financial data, stocks, indexes, forex, or market information that requires up-to-date information.
           - **Keywords**: Questions like "what is", "current price", "latest news", "population of", etc., related to financial instruments or general knowledge.
           - **Examples**:
             - "what is sp500 ?"
             - "current price of AAPL stock"
             - "latest news on forex markets"
             - "what are recent events in crypto market"
           - **Handling**: Use the 'search_google' tool to answer these requests.

        3. **Check Available Data Request**:
           - **Category**: User asks about available data or files.
           - **Keywords**: "available data", "what files are present", "list files in", etc., related to the '{self.data_folder}' folder.
           - **Handling**: Use the 'directory_listing' tool to check the contents of the '{self.data_folder}' folder.

        4. **Data-Specific Question Request**:
           - **Category**: Questions about the content of local data files.
           - **Examples**:
             - "average price of BTC"
             - "what is the latest price of ETH from my files"
           - **Handling**: Use the 'file_read' tool to read relevant data files from the '{self.data_folder}' folder and answer based on the data.

        **Available tools:**
        - search_google: for general web search
        - file_read: to read content from a file in the '{self.data_folder}' folder
        - file_write: to write content to a file in the '{self.data_folder}' folder
        - directory_listing: to list files and directories in the '{self.data_folder}' folder
        - user_input: to ask the user a question and get their response to refine the request
        - user_output: to display information to the user


        Analyze the user request and respond in YAML format to indicate the best action.

        For **General Information Seeking Request** (category 2), respond with:
        ```yaml
        tool_needed: yes
        tool_name: search_google
        tool_params:
          query: <search_query> # The user query as search term for google search
        reason: "User is asking for general information and google search is needed."
        action: tool_needed
        ```
        For **Check Available Data Request** (category 3), respond with:
        ```yaml
        tool_needed: yes
        tool_name: directory_listing
        tool_params:
          dir_path: {self.data_folder}
        reason: "User is asking to list files in the data directory."
        action: tool_needed
        ```
        For **Data-Specific Question Request** (category 4), respond with:
        ```yaml
        tool_needed: yes
        tool_name: file_read
        tool_params:
          file_path: <relevant_file_path> # Determine the relevant file path
        reason: "User is asking a question about specific data, file read is needed."
        action: tool_needed
        ```
        For **Cryptocurrency Data Download Request** (category 1), respond with:
        ```yaml
        tool_needed: no
        tool_name: None
        tool_params: {{}}
        reason: "User requested cryptocurrency data download, which is handled by a separate flow."
        action: crypto_download_requested
        ```
        If **no tool is needed** or for cases not explicitly covered, respond with:
        ```yaml
        tool_needed: no
        tool_name: None
        tool_params: {{}}
        reason: "Direct answer from LLM is possible or no tool is needed for this request."
        action: direct_answer_ready
        ```
        In cases of ambiguity or if you need more clarification from the user, use the 'user_input' tool.
        Remember to always respond in YAML format as shown in the examples.
        Determine which category best fits the user request and respond accordingly.
        """
        llm_response_yaml = call_llm(prompt)
        logger.info(f"AgentNode LLM Response (YAML): {llm_response_yaml}")
        try:
            llm_response_data = yaml.safe_load(llm_response_yaml)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing LLM YAML response: {e}")
            exec_res = "yaml_error"
            logger.info(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
            return exec_res

        tool_needed = llm_response_data.get("tool_needed")
        tool_name = llm_response_data.get("tool_name")
        tool_params = llm_response_data.get("tool_params", {})
        action_indicator = llm_response_data.get("action")
        search_query = tool_params.get("query") # Extract search query if google search is used
        shared["tool_request"] = llm_response_data # Store tool request in shared for ToolResultProcessorNode

        if tool_needed == "yes":
            tool_request = {
                "tool_name": tool_name,
                "tool_params": tool_params
            }
            exec_res = tool_request
        elif action_indicator == "crypto_download_requested":
            exec_res = "crypto_download_requested"
        elif tool_name == "search_google": # if google search is used, pass the query as exec_res
            tool_request = {
                "tool_name": tool_name,
                "tool_params": tool_params} # tool params already contains query
        else:
            llm_prompt_answer = f"User request: {user_input}\n Directly answer the request:"
            llm_answer = call_llm(llm_prompt_answer)
            shared["llm_answer"] = llm_answer.strip()
            logger.info(f"Direct LLM Answer: {llm_answer.strip()}")
            exec_res = "answer_directly"

        logger.info(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"AgentNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action_map = {
            "answer_directly": "direct_answer_ready",
            "yaml_error": "yaml_error",
            "crypto_download_requested": "crypto_download_requested"
        }
        user_input = prep_res
        llm_response = shared.get("llm_answer", "")

        if exec_res == "tool_needed":
            if shared['tool_loop_count'] < self.max_tool_loops:
                action = "tool_needed"
            else:
                logger.warning("Maximum tool loop count reached.")
                action = "max_loops_reached"
        elif isinstance(exec_res, dict) and "tool_name" in exec_res:
            action = "tool_needed"
        elif exec_res in action_map:
            action = action_map[exec_res]
        else:
            action = "unknown_action"

        message_history = shared.get('message_history', [])
        message_history.append({"user_input": user_input, "llm_response": llm_response})

        if len(message_history) > self.message_history_limit:
            message_history = message_history[-self.message_history_limit:]
        shared['message_history'] = message_history

        logger.info(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
