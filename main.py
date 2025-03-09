from nodes.main_flow.main_flow import MainFlow # Updated import to MainFlow and new file name
from lib.pocketflow import Flow

if __name__ == '__main__':
    main_flow_node = MainFlow() # Updated class name to MainFlow
    shared_data = {}
    main_flow_node.run(shared_data)
