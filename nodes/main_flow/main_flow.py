from util.pocketflow import Flow
from nodes.main_flow.agent_node import AgentNode
from nodes.main_flow.tool_invocation_node import ToolInvocationNode
# from nodes.main_flow.main_input_node import MainInputNode # Remove MainInputNode import
from nodes.freqtrade.freqtrade_flow import FreqtradeFlow
from nodes.main_flow.chat_retrieve_node import ChatRetrieveNode
from nodes.main_flow.command_input_node import CommandInputNode # Import CommandInputNode
# from nodes.main_flow.chat_reply_node import ChatReplyNode # AI: Remove ChatReplyNode import
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

        # Initialize new chat memory nodes
        chat_retrieve_node = ChatRetrieveNode() # Initialize ChatRetrieveNode here - moved to be before super().__init__
        command_input_node = CommandInputNode() # Initialize CommandInputNode
        super().__init__(start=chat_retrieve_node) # set start to chat_retrieve_node

        # main_input_node = MainInputNode() # Remove MainInputNode initialization


        # chat_reply_node = ChatReplyNode() # Remove ChatReplyNode instantiation
        agent_node = AgentNode(max_tool_loops=max_tool_loops, # Pass max_tool_loops from config
                                allowed_paths=allowed_paths,
                                data_folder=data_folder,
                                message_history_limit=message_history_limit)

        tool_invocation_node = ToolInvocationNode(allowed_paths=allowed_paths)
        freqtrade_flow = FreqtradeFlow()
        self.freqtrade_flow = freqtrade_flow

        chat_retrieve_node - "continue" >> agent_node
        chat_retrieve_node - "command_input" >> command_input_node # Transition to CommandInputNode for commands
        chat_retrieve_node - "quit" >> None # Quit from chat retrieve node
        chat_retrieve_node - "command_input_detected" >> command_input_node # Route command input to command node
        command_input_node - "continue_input" >> chat_retrieve_node # Loop back to ChatRetrieveNode after single slash command
        command_input_node - "command_input_loop" >> command_input_node # Loop back to CommandInputNode itself for double slash command
        # command_input_node - "quit" >> None # Remove quit transition from command input node - handled in chat_retrieve_node now

        agent_node - "tool_needed" >> tool_invocation_node # Explicit transition for tool needed

        # these 2 conditional transition should be the other way around.
        tool_invocation_node - "tool_invocation_success" >> agent_node
        tool_invocation_node - "tool_invocation_failure" >> agent_node


        agent_node - "answer_ready" >> chat_retrieve_node # Route direct answers to chat_retrieve_node - changed from chat_reply_node
        agent_node - "yaml_error" >> chat_retrieve_node
        agent_node - "max_loops_reached" >> chat_retrieve_node

        # chat_reply_node - "continue" >> chat_retrieve_node # Remove ChatReplyNode loop - not needed anymore


        # Sub-flow transitions
        agent_node - "crypto_download_requested" >> self.freqtrade_flow # Route crypto download requests to freqtrade_flow - no change needed
        # chat_retrieve_node - "quit" >> None # Moved quit transition here - No, keep it where it is, after the continue transition.

    def get_next_node(self, curr, action):
        nxt = super().get_next_node(curr, action)
        logger.debug(f"MainFlow.get_next_node: curr={curr.__class__.__name__}, action='{action}', next_node={nxt.__class__.__name__ if nxt else None}")
        return nxt
