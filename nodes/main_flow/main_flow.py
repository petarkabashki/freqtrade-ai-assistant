from lib.pocketflow import Flow
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode
from nodes.main_flow.tool_result_processor_node import ToolResultProcessorNode
from nodes.main_flow.main_input_node import MainInputNode
from nodes.freqtrade.freqtrade_flow import FreqtradeFlow

class MainFlow(Flow):
    def __init__(self, config):
        agent_config = config.get('agent', {})
        max_tool_loops = agent_config.get('max_tool_loops', 3)
        allowed_paths = agent_config.get('allowed_paths', [])
        data_folder = config.get('data_folder', 'freq-data')
        print(f"MainFlow initialized with config: {config}")

        super().__init__(start=main_input_node) # Set start node for the flow

        main_input_node = MainInputNode()
        agent_node = AgentNode(max_tool_loops=max_tool_loops,
                                allowed_paths=allowed_paths,
                                data_folder=data_folder)
        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths)
        tool_result_processor_node = ToolResultProcessorNode()
        freqtrade_flow = FreqtradeFlow()
        self.freqtrade_flow = freqtrade_flow # Store for debugging

        main_input_node >> agent_node >> tool_invocation_node >> \
            tool_result_processor_node

        # Loop for tool invocation
        # (AgentNode -> ToolInvocationNode -> ToolResultProcessorNode -> AgentNode)
        tool_result_processor_node >> ("processing_complete", agent_node)
        tool_result_processor_node >> ("default", agent_node) # default loop
        agent_node >> ("tool_needed", tool_invocation_node) # tool needed
        agent_node >> ("direct_answer_ready", tool_result_processor_node) # answer
        agent_node >> ("yaml_error", tool_result_processor_node) # yaml error
        agent_node >> ("max_loops_reached", tool_result_processor_node) # max loops
        agent_node >> ("crypto_download_requested", freqtrade_flow) # crypto

    def get_next_node(self, curr, action):
        nxt = super().get_next_node(curr, action)
        print(f"DEBUG: MainFlow.get_next_node: curr={curr.__class__.__name__}, action='{action}', next_node={nxt.__class__.__name__ if nxt else None}") # DEBUG LOG
        return nxt
