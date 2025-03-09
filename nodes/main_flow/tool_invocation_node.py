from util.pocketflow import Node, ParameterizedNode
from util.llm_tools.fs_tools import file_read_tool, file_write_tool, directory_listing_tool
from util.llm_tools import search_google_tool, user_input_tool, user_output_tool


class ToolInvocationNode(ParameterizedNode):
    def __init__(self, allowed_paths=None):
        super().__init__()
        self.available_tools = self._setup_tools(allowed_paths)
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
        tool_result = None
        error = None

        if tool_name == "file_read":
            tool_result = self.available_tools["file_read"](**tool_params)
        elif tool_name == "file_write":
            tool_result = self.available_tools["file_write"](**tool_params)
        elif tool_name == "directory_listing":
            tool_result = self.available_tools["directory_listing"](**tool_params)
        elif tool_name == "search_google":
            tool_result = self.available_tools["search_google"](**tool_params)
        elif tool_name == "user_input":
            tool_result = self.available_tools["user_input"](**tool_params)
        elif tool_name == "user_output":
            tool_result = self.available_tools["user_output"](**tool_params)
        else:
            error = f"Unknown tool requested: {tool_name}"

        if error:
            self.params["tool_error"] = error
            print(f"Tool Invocation Error: {error}")
            return "tool_invocation_failure"
        else:
            self.params["tool_results"] = tool_result
            print(f"Tool '{tool_name}' invoked successfully.")
            return "tool_invocation_success"
 
    def post(self, shared, prep_res, exec_res):
        print(f"ToolInvocationNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        action = "tool_executed"
        print(f"ToolInvocationNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return "tool_executed"

    def _setup_tools(self, allowed_paths):
        fs_tools_config = {"allowed_paths": allowed_paths}
        return {
            "file_read": file_read_tool,
            "file_write": file_write_tool,
            "directory_listing": directory_listing_tool,
            "search_google": search_google_tool,
            "user_input": user_input_tool,
            "user_output": user_output_tool,
        }
