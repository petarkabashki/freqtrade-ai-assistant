from pocketflow import Flow
# remove 'Unified' from the names of the in the following 2 lines. Update everywhere. AI!
from src.nodes.input_node import InputNode
from src.nodes.validation_node import ValidationNode
from src.nodes.confirmation_node import ConfirmationNode
from src.nodes.download_execution_node import DownloadExecutionNode
from src.nodes.summary_node import SummaryNode
from src.nodes.exit_node import ExitNode

def create_download_flow():
    nodes = {
        "input": InputNode(),
        "validation": ValidationNode(),
        "confirmation": ConfirmationNode(),
        "download": DownloadExecutionNode(),
        "summary": SummaryNode(),
        "exit": ExitNode(),
    }

    input_node = nodes["input"]
    validation_node = nodes["validation"]
    confirmation_node = nodes["confirmation"]
    download_node = nodes["download"]
    summary_node = nodes["summary"]
    exit_node = nodes["exit"]

    input_node - "validate_input" >> validation_node
    input_node - "exit" >> exit_node

    validation_node - "confirmation" >> confirmation_node
    validation_node - "reinput" >> input_node

    confirmation_node - "execute_download" >> download_node
    confirmation_node - "reinput" >> input_node

    download_node - "summary" >> summary_node

    summary_node - "exit" >> exit_node


    flow = Flow(start=input_node)
    return flow

if __name__ == "__main__":
    download_flow = create_download_flow()
    download_flow.run({})
