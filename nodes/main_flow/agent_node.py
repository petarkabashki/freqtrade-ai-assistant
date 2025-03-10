from util.pocketflow import Node
from util.call_llm import call_llm
import yaml
import logging
import json # AI: Import json
from nodes.main_flow.tool_descriptions import tool_descriptions_json # AI: Import tool descriptions json

logger = logging.getLogger(__name__)

class AgentNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def __init__(self, max_tool_loops=3, allowed_paths=None,
                 data_folder="freq-data", message_history_limit=5):
        super().__init__()
        self.max_tool_loops = max_tool_loops
        self.allowed_paths = allowed_paths if allowed_paths is not None else []
        self.data_folder = data_folder
        self.message_history_limit = message_history_limit
        self.tool_descriptions = json.loads(tool_descriptions_json) # AI: Load tool descriptions from json
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
            shared["llm_answer"] = f"{self.ORANGE_COLOR_CODE}{llm_answer.strip()}{self.RESET_COLOR_CODE}" # Make agent answer orange
            logger.info(f"AgentNode Answer based on Tool Results: {llm_answer.strip()}")
            exec_res = "answer_directly" # AI: Set action to answer directly
        else: # AI: If no tool results, proceed with tool/action decision as before
            history_text = ""
            if message_history:
                history_text = "Message History:\n"
                for msg in message_history:
                    history_text += f"- {msg['role']}: {msg['content']}\n"

            tool_descriptions_text = "Available Tools:\n" # AI: Start tool descriptions
            for tool_name, tool_info in self.tool_descriptions.items(): # AI: Loop through tool descriptions and info
                description = tool_info["description"] # AI: Get tool description
                arguments = tool_info["arguments"] # AI: Get tool arguments
                arguments_text = ", ".join([f"{arg_name}: {arg_desc}" for arg_name, arg_desc in arguments.items()]) # AI: Format arguments
                tool_descriptions_text += f"- {tool_name}: {description} Arguments: {arguments_text}\n" # AI: Add each tool description with arguments

            prompt = f"""
You are a FINANCIAL Research Assistant AI.
Your TOP PRIORITY is to answer questions about financial assets, commodities, crypto and other assets, using web search and/or redirecting to subflows. 
You can use the web search tool to find more about current asset prices, tickers and similar information to supplement the user's request, and/or to guide further questions you ask the user.
Keep clarifying and searching the web until you can answer the question.

So far the conversation has been:
{history_text}


Last user input: {user_input}


You can use the following tools:
{tool_descriptions_text} 

Your response is always in yaml format of the form:
```yaml
tool_needed: yes
tool_name: search_web
tool_params:
  - param1:
  - param2:
reason: The reason you need to call that tool
action: tool_needed | answer_ready
```
            """
            llm_response_yaml = call_llm(prompt)
            logger.info(f"AgentNode LLM Response (YAML): {llm_response_yaml}")
            try:
                llm_response_data = yaml.safe_load(llm_response_yaml)
                if not isinstance(llm_response_data, dict): # Check if yaml.safe_load returned a dict
                    raise yaml.YAMLError("YAML load did not return a dictionary")
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
                shared["llm_answer"] = f"{self.ORANGE_COLOR_CODE}{llm_answer.strip()}{self.RESET_COLOR_CODE}" # Make agent answer orange
                logger.info(f"Direct LLM Answer: {llm_answer.strip()}")
                exec_res = "answer_directly"

        logger.info(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"AgentNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action_map = {
            "answer_directly": "answer_ready",
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
