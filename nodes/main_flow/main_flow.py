from util.pocketflow import Flow
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode
# from nodes.main_flow.main_input_node import MainInputNode # AI: Remove MainInputNode import
from nodes.freqtrade.freqtrade_flow import FreqtradeFlow
from nodes.main_flow.chat_retrieve_node import ChatRetrieveNode
from nodes.main_flow.chat_reply_node import ChatReplyNode
import logging

logger = logging.getLogger(__name__)

class MainFlow(Flow):
    def __init__(self, config):
        agent_config = config.get('agent', {})
        max_tool_loops = agent_config.get('max_tool_loops', 3)
        allowed_paths = agent_config.get('allowed_paths', [])
        data_folder = config.get('data_folder', 'freq-data')
        message_history_limit = agent_config.get('message_history_limit', 5)
        logger.info(f"MainFlow initialized with config: {config}")

        # AI: Initialize new chat memory nodes
        chat_retrieve_node = ChatRetrieveNode() # AI: Initialize ChatRetrieveNode here - moved to be before super().__init__
        super().__init__(start=chat_retrieve_node) # AI: set start to chat_retrieve_node

        # main_input_node = MainInputNode() # AI: Remove MainInputNode initialization


        chat_reply_node = ChatReplyNode()
        agent_node = AgentNode(max_tool_loops=max_tool_loops,
                                allowed_paths=allowed_paths,
                                data_folder=data_folder,
                                message_history_limit=message_history_limit)

        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths)
        freqtrade_flow = FreqtradeFlow()
        self.freqtrade_flow = freqtrade_flow

        chat_retrieve_node >> agent_node >> tool_invocation_node

        agent_node - "tool_invocation_success" >> agent_node
        agent_node - "tool_invocation_failure" >> agent_node
        agent_node - "direct_answer_ready" >> chat_retrieve_node
        agent_node - "yaml_error" >> chat_retrieve_node
        agent_node - "max_loops_reached" >> chat_retrieve_node


        # Sub-flow transitions
        agent_node - "crypto_download_requested" >> self.freqtrade_flow # Route crypto download requests to freqtrade_flow - no change needed
        chat_retrieve_node - "quit" >> None

    def get_next_node(self, curr, action):
        nxt = super().get_next_node(curr, action)
        logger.debug(f"MainFlow.get_next_node: curr={curr.__class__.__name__}, action='{action}', next_node={nxt.__class__.__name__ if nxt else None}")
        return nxt
