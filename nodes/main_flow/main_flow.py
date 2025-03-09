from lib.pocketflow import Flow
from nodes.main_flow.main_input_node import MainInputNode
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode # Import ToolInvocationNode
from nodes.main_flow.tool_result_processor_node import ToolResultProcessorNode

class MainFlow(Flow):
    def __init__(self):
        super().__init__(start=None)
        main_input_node = MainInputNode()
        agent_node = AgentNode()
        tool_invocation_node = ToolInvocationNode() # Instantiate ToolInvocationNode
        tool_result_processor_node = ToolResultProcessorNode()

        main_input_node >> agent_node

        agent_node["tool_needed"] >> tool_invocation_node # Transition to invocation node when tool is needed
        agent_node["direct_answer_ready"] >> tool_result_processor_node # Example: Direct answer goes to result processor
        agent_node["yaml_error"] >> tool_result_processor_node # Example: YAML error handling

        tool_invocation_node["invocation_successful"] >> agent_node # Loop back to AgentNode on success
        tool_invocation_node["invocation_failed"] >> tool_result_processor_node # Example: Handle invocation failure

        self.start = main_input_node
