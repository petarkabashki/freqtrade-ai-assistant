from lib.pocketflow import Flow
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode
from nodes.main_flow.tool_result_processor_node import ToolResultProcessorNode
from nodes.main_flow.main_input_node import MainInputNode

class MainFlow(Flow):
    def __init__(self, config):
        agent_config = config.get('agent', {})
        max_tool_loops = agent_config.get('max_tool_loops', 3)
        allowed_paths = agent_config.get('allowed_paths', [])

        main_input_node = MainInputNode()
        agent_node = AgentNode(max_tool_loops=max_tool_loops, allowed_paths=allowed_paths) # Pass allowed_paths here
        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths) # Pass allowed_paths here
        tool_result_processor_node = ToolResultProcessorNode()

        main_input_node >> agent_node >> tool_invocation_node >> tool_result_processor_node

        # Loop for tool invocation (AgentNode -> ToolInvocationNode -> ToolResultProcessorNode -> AgentNode)
        tool_result_processor_node >> ("processing_complete", agent_node)
        agent_node >> ("tool_needed", tool_invocation_node) # if agent decides tool is needed, invoke tool
        agent_node >> ("direct_answer_ready", tool_result_processor_node) # if agent provides direct answer, process answer
        agent_node >> ("yaml_error", tool_result_processor_node) # if yaml parsing error, handle error
        agent_node >> ("max_loops_reached", tool_result_processor_node) # if max tool loops reached, handle max loops

        super().__init__(start=main_input_node) # Set start node for the flow
