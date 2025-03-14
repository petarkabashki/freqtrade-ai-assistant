from util.pocketflow import Node
from util.call_llm import call_llm
import yaml
import logging
import json
from nodes.main_flow.tool_descriptions import tool_descriptions_json

logger = logging.getLogger(__name__)

class AgentNode(Node):
    ORANGE_COLOR_CODE = "\033[38;5;208m"  # ANSI escape code for orange
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def __init__(self, max_tool_loops=3, allowed_paths=None,
                 data_folder="freq-data", message_history_limit=5):
        super().__init__()
        self.max_tool_loops = max_tool_loops # Set max_tool_loops from constructor
        self.allowed_paths = allowed_paths if allowed_paths is not None else []
        self.data_folder = data_folder
        self.message_history_limit = message_history_limit
        self.tool_descriptions = json.loads(tool_descriptions_json)
        logger.info(f"AgentNode initialized with max_tool_loops={max_tool_loops}, "
              f"allowed_paths={allowed_paths}, data_folder={data_folder}, message_history_limit={message_history_limit}")

    def prep(self, shared):
        logger.info(f"AgentNode prep started. Shared: {shared}")
        shared['tool_loop_count'] = 0 # Initialize tool_loop_count in prep
        if 'message_history' not in shared:
            shared['message_history'] = []
        prep_res = super().prep(shared)
        logger.info(f"AgentNode prep finished. Prep result: {prep_res}, Shared: {shared}")
        return prep_res

    def exec(self, prep_res, shared):
        # user input is the last message in the message history
        user_input = prep_res
        tool_results = shared.get("tool_results", None) # Get tool results from shared
        logger.info(f"AgentNode exec started. Prep result: {prep_res}, Shared: {shared}, Tool Results: {tool_results}")
        user_input = prep_res
        message_history = shared.get('message_history', []) # Get message history from shared
        tool_loop_count = shared.get('tool_loop_count', 0) # Get tool loop count from shared

        if tool_results: # Check if tool results are available
            llm_prompt_answer_tool_result = f"""
            User request: {user_input}
            Tool results: {tool_results}
            Based on the tool results, provide a concise and informative answer to the user.
            """
            llm_answer = call_llm(llm_prompt_answer_tool_result) # Call LLM to answer based on tool results
            shared["llm_answer"] = f"{self.ORANGE_COLOR_CODE}{llm_answer.strip()}{self.RESET_COLOR_CODE}" # Make agent answer orange
            logger.info(f"AgentNode Answer based on Tool Results: {llm_answer.strip()}")
            exec_res = {"action": "answer_ready", "final_answer": llm_answer.strip()} # Set action to answer_ready - Corrected action name, keep exec_res as dict
        else: # If no tool results, proceed with tool/action decision as before
            history_text = ""
            if message_history:
                history_text = "Message History:\n"
                for msg in message_history:
                    history_text += f"- {msg['role']}: {msg['content']}\n"

            tool_descriptions_text = "Available Tools:\n" # Start tool descriptions
            for tool_name, tool_info in self.tool_descriptions.items(): # Loop through tool descriptions and info
                description = tool_info["description"] # Get tool description
                arguments = tool_info["arguments"] # Get tool arguments
                arguments_text = ", ".join([f"{arg_name}: {arg_desc}" for arg_name, arg_desc in arguments.items()]) # Format arguments
                tool_descriptions_text += f"- {tool_name}: {description} Arguments: {arguments_text}\n" # Add each tool description with arguments

            prompt = f"""
You are a FINANCIAL Research Assistant AI.
Your TOP PRIORITY is to answer questions about financial assets, commodities, crypto and other assets, using web search and/or redirecting to subflows.
You can use the web search tool to find more about current asset prices, tickers and similar information to supplement the user's request, and/or to guide further questions you ask the user.
Use clarifying questions when needed, or search the web and use the search results until you can answer the question.
Once you are ready with the final answer, put it in 'final_answer'.
So far the conversation has been:
{history_text}


Last user input: {user_input}


You can use the following tools:
{tool_descriptions_text}

When using the 'search_web' tool, to clarify user intent about assets, commodities, or crypto, you MUST use the user's original input as the query.

Your response is always in yaml format of the form:
```yaml
tool_needed: yes
tool_name: search_web
tool_params:
  query: "Use the user input as the query for the search_web tool: '{user_input}'"
reason: The reason you need to call that tool
action: tool_needed | answer_ready
final_answer: None
```
            """
            llm_response_yaml = call_llm(prompt)
            logger.info(f"AgentNode LLM Response (YAML): {llm_response_yaml}")
            try:
                llm_response_data = yaml.safe_load(llm_response_yaml)
                if not isinstance(llm_response_data, dict): # Check if yaml.safe_load returned a dict
                    raise yaml.YAMLError("YAML load did not return a dictionary")
                exec_res = llm_response_data # Assign parsed yaml dict to exec_res
            except yaml.YAMLError as e:
                logger.error(f"Error parsing LLM YAML response: {e}")
                exec_res = {"action": "yaml_error"} # Set exec_res to dict with error action
                logger.info(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
                return exec_res

            if exec_res.get("tool_needed") == True: # Check if tool is needed
                shared['tool_loop_count'] = tool_loop_count + 1 # Increment tool loop count
                if shared['tool_loop_count'] > self.max_tool_loops: # Check if max loops reached
                    logger.warning(f"AgentNode: Max tool loops reached ({self.max_tool_loops}). Terminating tool invocation.")
                    exec_res = {"action": "max_loops_reached", "final_answer": "Reached maximum tool invocation loops."} # Set action to max loops reached
                else:
                    logger.info(f"AgentNode: Tool loop count: {shared['tool_loop_count']}, max loops: {self.max_tool_loops}")


            logger.info(f"AgentNode exec - exec_res before return: {exec_res}") # Added logging

        logger.info(f"AgentNode exec finished with result: {exec_res}, Shared: {shared}")
        return exec_res

    def post(self, shared, prep_res, exec_res):
        logger.info(f"AgentNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")

        tool_needed = exec_res.get("tool_needed")
        tool_name = exec_res.get("tool_name")
        tool_params = exec_res.get("tool_params", {})
        if tool_params is None:
            tool_params = {}

        action_indicator = exec_res.get("action")
        action = "continue" # Default action

        if tool_needed == True: # Changed to boolean True
            tool_request = {
                "tool_name": tool_name,
                "tool_params": tool_params
            } # tool_params is already a dict
            shared["tool_request"] = tool_request # <---- MOVE THIS LINE UP
            action = "tool_needed" # Set action to tool_needed
        elif action_indicator == "answer_ready":
            shared['message_history'].append({"role": "assistant", "content": exec_res.get("final_answer")}) # add llm response to message history - EXEC END
            action = "answer_ready" # Set action to answer_ready
        elif action_indicator == "max_loops_reached": # Handle max loops reached action
            action = "max_loops_reached" # Set action to max_loops_reached


        logger.info(f"AgentNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}") # <---- LOGGING AFTER SETTING shared["tool_request"]


        if action not in ["answer_ready", "tool_needed", "continue", "yaml_error", "max_loops_reached"]: # Added max_loops_reached to allowed actions
            raise ValueError(f"Invalid action in AgentNode.post: {action}") # Raise error for invalid action

        return action
