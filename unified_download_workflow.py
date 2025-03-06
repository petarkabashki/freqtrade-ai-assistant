from pocketflow import Flow
from src.nodes.unified_input_node import UnifiedInputNode
from src.nodes.unified_validation_node import UnifiedValidationNode
from src.nodes.confirmation_node import ConfirmationNode
from src.nodes.download_execution_node import DownloadExecutionNode
from src.nodes.summary_node import SummaryNode
from src.nodes.exit_node import ExitNode

def create_download_flow():
    nodes = {
        "input": UnifiedInputNode(),
        "validation": UnifiedValidationNode(),
        "confirmation": ConfirmationNode(),
        "download": DownloadExecutionNode(),
        "summary": SummaryNode(),
        "exit": ExitNode(),
    }

    flow_definition = {
        nodes["input"]: {
            "validate_input": nodes["validation"],
            "exit": nodes["exit"],
        },
        nodes["validation"]: {
            "confirmation": nodes["confirmation"],
            "reinput": nodes["input"],
        },
        nodes["confirmation"]: {
            "execute_download": nodes["download"],
            "reinput": nodes["input"],
        },
        nodes["download"]: {
            "summary": nodes["summary"],
        },
        nodes["summary"]: {
            "exit": nodes["exit"],
        },
    }

    flow = Flow(start=nodes["input"])
    for src_node, transitions in flow_definition.items():
        for action, dest_node in transitions.items():
            flow.add_successor(src_node, dest_node, action=action)

    return flow

if __name__ == "__main__":
    download_flow = create_download_flow()
    download_flow.run({})
