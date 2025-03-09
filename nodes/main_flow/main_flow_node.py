from lib.pocketflow import Flow, Node
from freq_assistant.nodes.main_flow.main_input_node import MainInputNode
from freq_assistant.nodes.main_flow.main_dispatcher_node import MainDispatcherNode

class MainFlowNode(Node):
    def exec(self, prep_res, shared):
        main_input_node = MainInputNode()
        main_dispatcher_node = MainDispatcherNode()

        main_input_node >> main_dispatcher_node

        main_flow = Flow(start=main_input_node)
        return main_flow

    def post(self, shared, prep_res, exec_res):
        shared['main_flow'] = exec_res
        return "run_flow"
