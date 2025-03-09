from lib.pocketflow import Flow, Node
from nodes.main_flow.main_dispatcher_node import MainDispatcherNode
from nodes.main_flow.main_input_node import MainInputNode

class MainFlowNode(Flow): # Changed inheritance from Node to Flow
    def __init__(self):
        super().__init__(start=None) # Initialize Flow without start node initially
        main_input_node = MainInputNode()
        main_dispatcher_node = MainDispatcherNode()

        main_input_node >> main_dispatcher_node

        self.start = main_input_node # Set the start node for the Flow

    # No need for exec method anymore as MainFlowNode is now a Flow itself
    # def exec(self, prep_res, shared):
    #     main_input_node = MainInputNode()
    #     main_dispatcher_node = MainDispatcherNode()
    #
    #     main_input_node >> main_dispatcher_node
    #
    #     main_flow = Flow(start=main_input_node)
    #     main_flow.run(shared) # Actually run the flow here

    def post(self, shared, prep_res, exec_res):
        return "default" # Or any appropriate action for MainFlowNode itself if needed
