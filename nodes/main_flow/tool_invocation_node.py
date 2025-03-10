from util.pocketflow import ParameterizedNode
import logging
from util.llm_tools import core_tools, fs_tools # corrected import path
import os

logger = logging.getLogger(__name__)
# don't pass a different action for errors, leave the llm handle that. AI!
class ToolInvocationNode(ParameterizedNode):

    def __init__(self, allowed_paths=None):
        super().__init__()
        self.allowed_paths = allowed_paths if allowed_paths is not None else []
        self.tools = self._setup_tools(allowed_paths)
        logger.info(f"ToolInvocationNode initialized with allowed_paths={allowed_paths}")

    def prep(self, shared):
        tool_request = shared.get("tool_request", {})
        logger.info(f"ToolInvocationNode prep started. Tool Request: {tool_request}, Shared keys: {shared.keys()}, Full Shared: {shared}") # <--- ADDED LOGGING HERE
        if not tool_request: # Changed to check for boolean True
            logger.warning("Tool requested but 'tool_needed' is not 'yes' or tool_request is missing.")
            return None  # or raise an exception?

        tool_name = tool_request.get("tool_name")
        tool_params = tool_request.get("tool_params", {})

        if not tool_name:
            logger.error("Tool name is missing in tool request.")
            return None

        tool = self.tools.get(tool_name)
        if not tool:
            logger.error(f"Tool '{tool_name}' not found in available tools.")
            return None

        logger.info(f"ToolInvocationNode prep finished. Tool: {tool_name}, Params: {tool_params}")
        return tool, tool_params

    def exec(self, prep_res, shared):
        if not prep_res:
            return "tool_not_found"

        tool, tool_params = prep_res
        tool_name = shared['tool_request']['tool_name']
        logger.info(f"ToolInvocationNode exec started. Tool: {tool_name}, Params: {tool_params}")

        try:
            if tool_params:
                logger.info(f"Executing tool '{tool_name}' with params: {tool_params}")
                tool_result = tool(**tool_params) # Execute tool with parameters
            else:
                logger.info(f"Executing tool '{tool_name}' without params.")
                tool_result = tool() # Execute tool without parameters

            shared["tool_results"] = tool_result # Store tool results in shared
            logger.info(f"Tool '{tool_name}' execution successful. Result: {tool_result}")
            exec_res = "tool_invocation_success" # Indicate tool success
        except Exception as e:
            error_message = f"Error executing tool '{tool_name}': {e}"
            logger.error(error_message)
            shared["tool_error"] = error_message # Store error message in shared
            exec_res = "tool_invocation_failure" # Indicate tool failure

        logger.info(f"ToolInvocationNode exec finished with result: {exec_res}, Shared: {shared}")
        return exec_res # Return action based on tool execution result

    def post(self, shared, prep_res, exec_res): # Pass exec_res action through
        logger.info(f"ToolInvocationNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action = exec_res # Action is same as exec result (success or failure)
        logger.info(f"ToolInvocationNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action # Pass through action

    def _setup_tools(self, allowed_paths):
        tools = {
            "search_web": core_tools.search_web_tool, # Use search_web_tool
            # "execute_sql": core_tools.execute_sql_tool,
            # "run_code": core_tools.run_code_tool,
            # "crawl_web": core_tools.crawl_web_tool,
            # "transcribe_audio": core_tools.transcribe_audio_tool,
            # "send_email": core_tools.send_email_tool,
            # "extract_text_from_pdf": core_tools.extract_text_from_pdf_tool,
            # "extract_text_from_image_pdf": core_tools.extract_text_from_image_pdf_tool,
            # "user_input": core_tools.user_input_tool,
            # "user_output": core_tools.user_output_tool,
            # "get_embedding": core_tools.get_embedding_tool,
            # "create_index": core_tools.create_index_tool,
            # "search_index": core_tools.search_index_tool,
            # "call_llm": core_tools.call_llm_tool,
            # "call_llm_vision": core_tools.call_llm_vision_tool,
            # "file_read": fs_tools.file_read_tool,
            # "file_write": fs_tools.file_write_tool,
            # "directory_listing": fs_tools.directory_listing_tool,
        }
        return tools
