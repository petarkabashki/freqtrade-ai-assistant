from lib.pocketflow import Flow
from nodes.main_flow.main_input_node import MainInputNode
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode # Import ToolInvocationNode
from nodes.main_flow.tool_result_processor_node import ToolResultProcessorNode

class MainFlow(Flow):
    def __init__(self, config): # Accept config as argument
        super().__init__(start=None)
        main_input_node = MainInputNode()
        agent_config = config.get('agent', {}) # Get agent config, default to empty dict
        max_tool_loops = agent_config.get('max_tool_loops', 3) # Get max_tool_loops, default to 3 if not in config
        allowed_paths = agent_config.get('allowed_paths', []) # Get allowed_paths, default to empty list if not in config
        agent_node = AgentNode(max_tool_loops=max_tool_loops, allowed_paths=allowed_paths) # Instantiate AgentNode with allowed_paths
        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths) # Instantiate ToolInvocationNode with allowed_paths
        tool_result_processor_node = ToolResultProcessorNode()

        main_input_node >> agent_node

        agent_node["tool_needed"] >> tool_invocation_node # Transition to invocation node when tool is needed
        agent_node["direct_answer_ready"] >> tool_result_processor_node
        agent_node["yaml_error"] >> tool_result_processor_node
        agent_node["max_loops_reached"] >> tool_result_processor_node # New transition for max loops reached

        tool_invocation_node["invocation_successful"] >> agent_node # Loop back to AgentNode on success
        tool_invocation_node["invocation_failed"] >> tool_result_processor_node

        self.start = main_input_node
