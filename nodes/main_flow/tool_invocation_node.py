from lib.pocketflow import Node
from lib.tools import search_google, file_read, file_write, directory_listing, user_input_llm_query, user_output  # Import all tools

class ToolInvocationNode(Node):
    def exec(self, prep_res, shared):
        tool_request = prep_res # prep_res will contain the tool request from AgentNode
        tool_name = tool_request.get("tool_name")
        tool_params = tool_request.get("tool_params", {})

        tool_result = None
        error = None

        if tool_name == "search_google":
            tool_result = search_google(**tool_params) # Use ** to unpack params
        elif tool_name == "file_read":
            tool_result = file_read(**tool_params)
        elif tool_name == "file_write":
            tool_result = file_write(**tool_params)
        elif tool_name == "directory_listing":
            tool_result = directory_listing(**tool_params)
        elif tool_name == "user_input_llm_query":
            tool_result = user_input_llm_query(**tool_params)
        elif tool_name == "user_output":
            tool_result = user_output(**tool_params)
        else:
            error = f"Unknown tool requested: {tool_name}"

        if error:
            shared["tool_error"] = error
            print(f"Tool Invocation Error: {error}")
            return "tool_invocation_failure"
        else:
            shared["tool_results"] = tool_result # Store results in shared
            print(f"Tool '{tool_name}' invoked successfully.")
            return "tool_invocation_success"

    def post(self, shared, prep_res, exec_res):
        if exec_res == "tool_invocation_success":
            shared['tool_loop_count'] += 1 # Increment loop counter after successful invocation
            return "invocation_successful"
        elif exec_res == "tool_invocation_failure":
            return "invocation_failed"
        else:
            return "default"
