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
                history_text += f"- {msg['role']}: {msg['content']}\n"
        prompt = f"""
        {history_text}
        User request: {user_input}

        AI assistant for financial data analysis. 
        For generic questions, assume a financial topic and use search_google tool to provide information.
        Effectively use tools based on user intent.

        Categories:
        1. Crypto Download (CRITICAL SUB-FLOW): For cryptocurrency download requests, trigger 'crypto_download_requested' action for FreqtradeFlow.
        2. General Financial Info Seek: For generic financial questions, use search_google tool.
        3. Check Data: For requests about available data, list files in '{self.data_folder}'.
        4. Data Question: For questions about local data, use file_read tool.

        Tools:
        - search_google: Web search for general information, especially financial topics.
        - file_read: Read content from local files in '{self.data_folder}'.
        - directory_listing: List files and directories in '{self.data_folder}'.
        - user_input: Ask user for more information or clarification.
        - user_output: Display output to the user.

        Output YAML to indicate action and tool. For crypto download, action MUST be 'crypto_download_requested'.
        For generic financial questions, default to using search_google.
        ```yaml
        tool_needed: yes/no
        tool_name: <tool_name> 
        tool_params: ... 
        reason: <decision reason>
        action: <action_indicator> # if crypto download, action MUST be 'crypto_download_requested'
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
        elif tool_name == "search_google":
            tool_request = {
                "tool_name": tool_name,
                "tool_params": tool_params}
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
        message_history.append({"role": "user", "content": user_input})
        message_history.append({"role": "assistant", "content": llm_response})

        if len(message_history) > self.message_history_limit:
            message_history = message_history[-self.message_history_limit:]
        shared['message_history'] = message_history

        logger.info(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
