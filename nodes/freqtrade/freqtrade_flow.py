from util.pocketflow import *
from .input_node import InputNode
from .validation_node import ValidationNode
from .confirmation_node import ConfirmationNode
from .download_node import DownloadNode
from .summary_node import SummaryNode
from .exit_node import ExitNode

class FreqtradeFlow(Flow):
    def __init__(self):
        nodes = {
            "input": InputNode(),
            "validation": ValidationNode(),
            "confirmation": ConfirmationNode(),
            "download": DownloadNode(),
            "summary": SummaryNode(),
            "exit": ExitNode(),
        }

        input_node = nodes["input"]
        validation_node = nodes["validation"]
        confirmation_node = nodes["confirmation"]
        download_node = nodes["download"]
        summary_node = nodes["summary"]
        exit_node = nodes["exit"]

        input_node >> ("validate_input", validation_node)
        input_node >> ("exit", exit_node)
        validation_node >> ("confirmation", confirmation_node)
        validation_node >> ("reinput", input_node)
        confirmation_node >> ("execute_download", download_node)
        confirmation_node >> ("reinput", input_node)
        download_node >> ("summary", summary_node)
        summary_node >> ("exit", exit_node)
        summary_node >> ("input", input_node)

        super().__init__(start=input_node) # Pass start node to super constructor
