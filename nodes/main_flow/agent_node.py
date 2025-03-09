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
        user_input = prep_res
        tool_results = shared.get("tool_results", None) # Get tool results from shared
        logger.info(f"AgentNode exec started. Prep result: {prep_res}, Shared: {shared}, Tool Results: {tool_results}")
        user_input = prep_res
        message_history = shared.get('message_history', []) # Get message history from shared

        if tool_results: # AI: Check if tool results are available
            llm_prompt_answer_tool_result = f"""
            User request: {user_input}
            Tool results: {tool_results}
            Based on the tool results, provide a concise and informative answer to the user.
            """
            llm_answer = call_llm(llm_prompt_answer_tool_result) # AI: Call LLM to answer based on tool results
            shared["llm_answer"] = llm_answer.strip()
            logger.info(f"AgentNode Answer based on Tool Results: {llm_answer.strip()}")
            exec_res = "answer_directly" # AI: Set action to answer directly
        else: # AI: If no tool results, proceed with tool/action decision as before
            history_text = ""
            if message_history:
                history_text = "Message History:\n"
                for msg in message_history:
                    history_text += f"- {msg['role']}: {msg['content']}\n"
            prompt = f"""
            You are an AI assistant designed to process user requests using tools and respond in a helpful way.
            You have access to tools for:
            - Web search (search_google)
            - Reading local files (file_read)
            - Listing directories (directory_listing)

            {history_text}
            User request: {user_input}

            AI assistant for financial data analysis and general knowledge.
            For questions that are not directly related to crypto download or local data, use search_google tool to provide information.
            Effectively use tools based on user intent.

            Categories:
            1. Crypto Download (CRITICAL SUB-FLOW): For cryptocurrency download requests (e.g., 'download ETH/USDT data'), trigger 'crypto_download_requested' action for FreqtradeFlow.
            2. General Financial Info Seek: For generic financial questions (e.g., 'what is cardano?', 'explain bitcoin halving', 'what's the price of gold'), use search_google tool to get the answer. This is the PRIMARY tool for financial and general knowledge queries.
            3. Check Data: For requests about available data (e.g., 'list available data', 'what data do you have'), list files in '{self.data_folder}'.
            4. Data Question: For questions about local data (e.g., 'summarize ETHUSDT data', 'analyze BTC data'), use file_read tool to read and process local data files.
            5. General Knowledge Question: For general knowledge questions that are not specific to finance but require web search (e.g., 'what is soffix?', 'who won nobel prize 2023'), use search_google tool.

            Tools:
            - search_google: Web search for general information, especially financial and general knowledge topics. Use this tool for categories 2 and 5.
            - file_read: Read content from local files in '{self.data_folder}'.
            - directory_listing: List files and directories in '{self.data_folder}'.
            - user_input: Ask user for more information or clarification.
            - user_output: Display output to the user.

            Output YAML to indicate action and tool.
            For crypto download requests, action MUST be 'crypto_download_requested'.
            For general financial or general knowledge questions, default to using search_google.
            If a tool is needed, tool_needed should be 'yes'.
            If no tool is needed for direct answer, tool_needed should be 'no'.

            Example YAML output for a general knowledge question (like 'what's the price of gold'):
            ```yaml
            tool_needed: yes
            tool_name: search_google
            tool_params:
              query: <user_question> # e.g., query: what's the price of gold?
            reason: User is asking a general financial question that requires web search.
            action: tool_needed
            ```

            Example YAML output for a crypto download request:
            ```yaml
            tool_needed: no
            tool_name: ""
            tool_params: ""
            reason: User is asking to download crypto data, triggering crypto download sub-flow.
            action: crypto_download_requested
            ```

            Example YAML output for a data check request:
            ```yaml
            tool_needed: yes
            tool_name: directory_listing
            tool_params:
              dir_path: {self.data_folder} # e.g., dir_path: freq-data
            reason: User is asking to check available data, listing directory.
            action: tool_needed
            ```

            Example YAML output for a direct answer (no tool needed):
            ```yaml
            tool_needed: no
            tool_name: ""
            tool_params: ""
            reason: User is asking a question that can be answered directly without tools, or a greeting.
            action: direct_answer_ready
            ```

            Now, based on the user request, output YAML:
            ```yaml
            tool_needed: yes/no
            tool_name: <tool_name> or ""
            tool_params: <tool_params_in_yaml_dictionary_format> or ""
            reason: <decision reason>
            action: <action_indicator> # if crypto download, action MUST be 'crypto_download_requested' or 'tool_needed' or 'direct_answer_ready'
            ```
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
            if tool_params is None:
                tool_params = {}
            if isinstance(tool_params, str): # AI: Handle case where tool_params is a string
                tool_params = {} # Treat string tool_params as empty dict
            action_indicator = llm_response_data.get("action")
            search_query = tool_params.get("query")
            shared["tool_request"] = llm_response_data

            if tool_needed == "yes":
                tool_request = {
                    "tool_name": tool_name,
                    "tool_params": tool_params
                }
                exec_res = tool_request
            elif action_indicator == "crypto_download_requested":
                exec_res = "crypto_download_requested"
            else: # Direct answer if no tool is explicitly needed and not crypto download
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
            "crypto_download_requested": "crypto_download_requested",
            "tool_invocation_success": "tool_invocation_success", # Added tool success action
            "tool_invocation_failure": "tool_invocation_failure"  # Added tool failure action
        }
        user_input = prep_res
        llm_response = shared.get("llm_answer", "")

        if exec_res == "tool_needed": # This condition is never met, exec_res is tool_request dict when tool is needed
            if shared['tool_loop_count'] < self.max_tool_loops:
                action = "tool_needed" # Should transition to ToolInvocationNode
            else: # Max tool loops reached, provide direct answer
                logger.warning("Maximum tool loop count reached. Providing direct answer.")
                action = "max_loops_reached"
        elif isinstance(exec_res, dict) and "tool_name" in exec_res: # Correctly handle tool request dict
            action = "tool_needed" # Transition to ToolInvocationNode
            shared['tool_loop_count'] += 1 # Increment loop count when tool is used
        elif exec_res in action_map:
            action = action_map[exec_res]
        else:
            action = "unknown_action"

        message_history = shared.get('message_history', [])
        message_history.append({"role": "user", "content": user_input})
        message_history.append({"role": "assistant", "content": llm_response})

        if len(message_history) > self.message_history_limit:
            message_history = message_history[-self.message_history_limit:]
        shared['message_history'] = message_history

        logger.info(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
