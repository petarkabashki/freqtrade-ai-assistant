from util.pocketflow import Flow
from nodes.main_flow.tool_invocation_node import ToolInvocationNode
from nodes.main_flow.tool_result_processor_node import ToolResultProcessorNode
from nodes.main_flow.main_input_node import MainInputNode
from nodes.freqtrade.freqtrade_flow import FreqtradeFlow
from nodes.main_flow.chat_retrieve_node import ChatRetrieveNode # AI: Import ChatRetrieveNode
from nodes.main_flow.chat_reply_node import ChatReplyNode # AI: Import ChatReplyNode
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

        main_input_node = MainInputNode()
        super().__init__(start=main_input_node)

        # AI: Initialize new chat memory nodes
        chat_retrieve_node = ChatRetrieveNode()
        chat_reply_node = ChatReplyNode() # AI: Removed extra arguments

        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths)
        tool_result_processor_node = ToolResultProcessorNode()
        freqtrade_flow = FreqtradeFlow()
        self.freqtrade_flow = freqtrade_flow

        # AI: Flow wiring for chat memory
        main_input_node >> chat_retrieve_node >> chat_reply_node >> tool_invocation_node >> tool_result_processor_node
        tool_result_processor_node >> ("processing_complete", main_input_node) # AI: Loop back to main_input_node for conversation
        tool_result_processor_node >> ("default", chat_retrieve_node) # Loop back to chat_retrieve_node for tool processing

        chat_reply_node >> ("tool_needed", tool_invocation_node) # tool needed
        chat_reply_node >> ("direct_answer_ready", tool_result_processor_node) # answer
        chat_reply_node >> ("yaml_error", tool_result_processor_node) # yaml error
        chat_reply_node >> ("max_loops_reached", tool_result_processor_node) # max loops


        # Sub-flow transitions
        chat_reply_node >> ("crypto_download_requested", self.freqtrade_flow) # Route crypto download requests to freqtrade_flow
        main_input_node - "quit" >> None

    def get_next_node(self, curr, action):
        nxt = super().get_next_node(curr, action)
        logger.debug(f"MainFlow.get_next_node: curr={curr.__class__.__name__}, action='{action}', next_node={nxt.__class__.__name__ if nxt else None}")
        return nxt
