from pocketflow import Flow
from src.nodes.unified_input_node import UnifiedInputNode
from src.nodes.unified_validation_node import UnifiedValidationNode
from src.nodes.confirmation_node import ConfirmationNode
from src.nodes.download_execution_node import DownloadExecutionNode
from src.nodes.summary_node import SummaryNode
from src.nodes.exit_node import ExitNode

def create_download_flow():
    input_node = UnifiedInputNode()
    validation_node = UnifiedValidationNode()
    confirmation_node = ConfirmationNode()
    download_node = DownloadExecutionNode()
    summary_node = SummaryNode()
    exit_node = ExitNode()

    flow = Flow(start=input_node)
    flow.add_successor(input_node, validation_node, action="validate_input")
    flow.add_successor(input_node, exit_node, action="exit")
    flow.add_successor(validation_node, confirmation_node, action="confirmation")
    flow.add_successor(validation_node, input_node, action="reinput") # Loop back to input on validation failure
    flow.add_successor(confirmation_node, download_node, action="execute_download")
    flow.add_successor(confirmation_node, input_node, action="reinput") # Loop back to input on no confirmation
    flow.add_successor(download_node, summary_node, action="summary")
    flow.add_successor(summary_node, exit_node, action="exit")

    return flow

if __name__ == "__main__":
    download_flow = create_download_flow()
    download_flow.run({})
