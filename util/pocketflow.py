import logging

logger = logging.getLogger(__name__)

class Node:
    def __init__(self):
        self.successors = {}
        self.cur_retry = 0  # Initialize retry counter

    def prep(self, shared):
        print(f"Node {self.__class__.__name__} prep started")
        return None

    def exec(self, prep_res, shared):
        print(f"Node {self.__class__.__name__} exec started with prep_res: {prep_res}")
        return None

    def post(self, shared, prep_res, exec_res):
        print(f"Node {self.__class__.__name__} post started with exec_res: {exec_res}")
        return "default"  # Default action

    def run(self, shared):
        prep_result = self.prep(shared)
        exec_result = self.exec(prep_result, shared)
        action_result = self.post(shared, prep_result, exec_result)
        return action_result

    def __rshift__(self, other_node):
        self.successors["default"] = other_node
        return other_node

    def __sub__(self, action_name):
        class ActionLink:
            def __init__(self, node, action_name):
                self.node = node
                self.action_name = action_name

            def __rshift__(self, next_node):
                self.node.successors[self.action_name] = next_node
                return next_node

        return ActionLink(self, action_name)


class Flow(Node): # Flow is a special type of Node
    def __init__(self, start):
        super().__init__()
        self.start = start
        self.nodes = {} # Track nodes in the flow for easy access if needed

    def run(self, shared):
        current_node = self.start
        action = "default" # Initial action

        while True: # AI: Loop indefinitely for conversation
            self.nodes[current_node.__class__.__name__] = current_node # Track node
            logger.info(f"\nExecuting Node: {current_node.__class__.__name__}")
            action = current_node.run(shared)
            logger.info(f"Node {current_node.__class__.__name__} returned action: {action}")
            if action is None:
                break # No action means stop
            next_node = self.get_next_node(current_node, action)
            if not next_node:
                break # AI: Terminate loop if next_node is None, not restart
            else:
                current_node = next_node # Move to the next node

        logger.info(f"Flow execution finished.\n")
        return action

    def get_next_node(self, curr, action):
        return curr.successors.get(action)


class BatchNode(Node):
    def prep(self, shared):
        logger.debug(f"BatchNode {self.__class__.__name__} prep started")
        return [] # Expecting a list of items

    def exec(self, item):
        logger.debug(f"BatchNode {self.__class__.__name__} exec item: {item}")
        return None

    def post(self, shared, prep_res, exec_res_list):
        logger.debug(f"BatchNode {self.__class__.__name__} post started with exec_res_list: {exec_res_list}")
        return "default"

    def run(self, shared):
        prep_result = self.prep(shared)
        exec_results = []
        if prep_result and isinstance(prep_result, list): # Check if prep_result is a list and not empty
            for item in prep_result:
                exec_result = self.exec(item)
                exec_results.append(exec_result)
        action_result = self.post(shared, prep_result, exec_results)
        return action_result


class ParameterizedNode(Node): # Define ParameterizedNode here
    pass
