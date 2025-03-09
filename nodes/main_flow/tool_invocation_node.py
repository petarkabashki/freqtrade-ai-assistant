from util.pocketflow import Node
from util.core_tools import search_google_tool, user_input_tool, \
    user_output_tool
from util.llm_tools.fs_tools import file_read, file_write, directory_listing, \
    ALLOWED_PATHS

class ToolInvocationNode(Node):
    def __init__(self, allowed_paths=None):
        super().__init__()
        self.allowed_paths = allowed_paths if allowed_paths is not None else []

    def prep(self, shared):
        ALLOWED_PATHS.clear()
        ALLOWED_PATHS.extend(self.allowed_paths)
        return super().prep(shared)

    def exec(self, prep_res, shared):
        tool_request = prep_res
        tool_name = tool_request.get("tool_name")
        tool_params = tool_request.get("tool_params", {})

        tool_result = None
        error = None

        if tool_name == "search_google":
            tool_result = search_google_tool(**tool_params)
        elif tool_name == "file_read":
            tool_result = file_read(**tool_params)
        elif tool_name == "file_write":
            tool_result = file_write(**tool_params)
        elif tool_name == "directory_listing":
            tool_result = directory_listing(**tool_params)
        elif tool_name == "user_input":
            tool_result = user_input_tool(**tool_params)
        elif tool_name == "user_output":
            tool_result = user_output_tool(**tool_params)
        else:
            error = f"Unknown tool requested: {tool_name}"

        if error:
            shared["tool_error"] = error
            print(f"Tool Invocation Error: {error}")
            return "tool_invocation_failure"
        else:
            shared["tool_results"] = tool_result
            print(f"Tool '{tool_name}' invoked successfully.")
            return "tool_invocation_success"

    def post(self, shared, prep_res, exec_res):
        if exec_res == "tool_invocation_success":
            shared['tool_loop_count'] += 1
            return "invocation_successful"
        elif exec_res == "tool_invocation_failure":
            return "invocation_failed"
        else:
            return "default"
