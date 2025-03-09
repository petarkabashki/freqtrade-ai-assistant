from freq_assistant.nodes.main_flow.main_input_node import MainInputNode
from freq_assistant.nodes.main_flow.main_dispatcher_node import MainDispatcherNode
from lib.pocketflow import Flow

#use the main_flow node here AI!
if __name__ == '__main__':
    main_input = MainInputNode()
    main_dispatcher = MainDispatcherNode()

    main_input - "llm" >> main_dispatcher
    main_dispatcher - "input" >> main_input

    main_flow = Flow(start=main_input)
    shared_data = {}
    main_flow.run(shared_data)
