import logging

logger = logging.getLogger(__name__)

class Node:
    GRAY_COLOR_CODE = "\033[90m"  # ANSI escape code for gray
    YELLOW_COLOR_CODE = "\033[93m" # ANSI escape code for yellow
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def __init__(self):
        self.successors = {}
        self.cur_retry = 0
        self.max_retries = 1 # default is no retry
        self.wait = 0 # default is no wait

    def prep(self, shared):
        logger.debug(f"{self.__class__.__name__}.prep()")
        return None

    def exec(self, prep_res, shared):
        logger.debug(f"{self.__class__.__name__}.exec(prep_res)")
        return None

    def post(self, shared, prep_res, exec_res):
        logger.debug(f"{self.__class__.__name__}.post(shared, prep_res, exec_res)")
        return "default" # default action is "default"

    def run(self, shared):
        logger.info(f"{self.__class__.__name__}.run() started")
        prep_res = None
        exec_res = None
        action = "default" # Initialize action to default

        try:
            prep_res = self.prep(shared)
            exec_res = self.exec(prep_res, shared)
            action = self.post(shared, prep_res, exec_res)
        except Exception as e:
            if self.cur_retry < self.max_retries:
                self.cur_retry += 1
                logger.warning(f"{self.__class__.__name__}.exec() failed, retry {self.cur_retry}/{self.max_retries} after {self.wait} seconds. Exception: {e}")
                import time
                time.sleep(self.wait)
                return self.run(shared) # Recursive retry
            else:
                logger.error(f"{self.__class__.__name__}.exec() failed after {self.max_retries} retries. Exception: {e}")
                action = self.exec_fallback(prep_res, e) # Call fallback
                if action is None: # if fallback does not return action, default to "error"
                    action = "error"

        logger.info(f"{self.__class__.__name__}.run() finished, action: '{action}'")
        self.cur_retry = 0 # reset retry counter after run
        return action

    def exec_fallback(self, prep_res, exc):
        logger.error(f"{self.__class__.__name__}.exec_fallback() called for exception: {exc}")
        return None # default fallback does nothing

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
                return next_node # Allow chaining
        return ActionLink(self, action_name)

class Flow(Node): # Flow is a special type of Node
    GRAY_COLOR_CODE = "\033[90m"  # ANSI escape code for gray
    YELLOW_COLOR_CODE = "\033[93m" # ANSI escape code for yellow
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def __init__(self, start):
        super().__init__() # Initialize Node superclass
        self.start = start
        self.nodes = {} # to keep track of nodes in the flow, not used yet
        self.params = {} # flow level params, can be overwritten by parent flow

    def run(self, shared):
        logger.info(f"{self.__class__.__name__}.run() started")
        current_node = self.start
        action = "default" # initial action

        while current_node:
            logger.debug(f"Current node: {current_node.__class__.__name__}")
            action = current_node.run(shared) # Execute the current node and get the action
            if not action:
                action = "default" # in case node returns None action, treat as default

            next_node = self.get_next_node(current_node, action)
            logger.debug(f"Action: '{action}', Next node: {next_node.__class__.__name__ if next_node else None}")
            current_node = next_node # Move to the next node

        logger.info(f"{self.__class__.__name__}.run() finished")
        return action # return last action, for nested flows

    def get_next_node(self, curr, action):
        if action in curr.successors:
            nxt = curr.successors[action]
            transition_message = f"Transition: {curr.__class__.__name__} - '{action}' -> {nxt.__class__.__name__ if nxt else 'None'}"
            print(f"{self.YELLOW_COLOR_CODE}{transition_message}{self.RESET_COLOR_CODE}") # Print transition in yellow
            logger.debug(transition_message)
            return nxt
        else:
            logger.debug(f"No transition defined for action '{action}' from node {curr.__class__.__name__}")
            return None # No next node defined for this action

    def set_params(self, params):
        self.params = params

class BatchNode(Node):
    GRAY_COLOR_CODE = "\033[90m"  # ANSI escape code for gray
    YELLOW_COLOR_CODE = "\033[93m" # ANSI escape code for yellow
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def prep(self, shared):
        logger.debug(f"{self.__class__.__name__}.prep()")
        return [] # Expecting a list of items to process

    def exec(self, item): # process single item
        logger.debug(f"{self.__class__.__name__}.exec(item)")
        return item

    def post(self, shared, prep_res, exec_res_list):
        logger.debug(f"{self.__class__.__name__}.post(shared, prep_res, exec_res_list)")
        return "default"

    def run(self, shared):
        logger.info(f"{self.__class__.__name__}.run() started")
        prep_res = None
        exec_res_list = []
        action = "default"

        try:
            prep_res = self.prep(shared) # get iterable from prep
            if not isinstance(prep_res, list):
                prep_res = list(prep_res) # Ensure prep_res is a list

            logger.debug(f"{self.__class__.__name__}.run() - Processing {len(prep_res)} items")
            for item in prep_res: # loop through iterable
                item_exec_res = self.exec(item) # process each item
                exec_res_list.append(item_exec_res) # collect results

            action = self.post(shared, prep_res, exec_res_list) # process all results
        except Exception as e:
            if self.cur_retry < self.max_retries:
                self.cur_retry += 1
                logger.warning(f"{self.__class__.__name__}.exec() failed, retry {self.cur_retry}/{self.max_retries} after {self.wait} seconds. Exception: {e}")
                import time
                time.sleep(self.wait)
                return self.run(shared) # Recursive retry
            else:
                logger.error(f"{self.__class__.__name__}.exec() failed after {self.max_retries} retries. Exception: {e}")
                action = self.exec_fallback(prep_res, e) # Call fallback
                if action is None: # if fallback does not return action, default to "error"
                    action = "error"

        logger.info(f"{self.__class__.__name__}.run() finished, action: '{action}'")
        self.cur_retry = 0 # reset retry counter
        return action

class ParameterizedNode(Node): # Define ParameterizedNode here
    GRAY_COLOR_CODE = "\033[90m"  # ANSI escape code for gray
    YELLOW_COLOR_CODE = "\033[93m" # ANSI escape code for yellow
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def __init__(self):
        super().__init__()
        self.params = {}

    def set_params(self, params):
        self.params = params
        return self # for chaining