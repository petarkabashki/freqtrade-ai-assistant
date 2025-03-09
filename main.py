from freq_assistant.nodes.main_flow.main_flow_node import MainFlowNode
from lib.pocketflow import Flow

if __name__ == '__main__':
    main_flow_node = MainFlowNode()
    shared_data = {}
    main_flow = main_flow_node.run(shared_data)
    main_flow.run(shared_data)
