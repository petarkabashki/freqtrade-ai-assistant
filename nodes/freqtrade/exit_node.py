from util.pocketflow import Node

class ExitNode(Node):
    GRAY_COLOR_CODE = "\033[90m"  # ANSI escape code for gray
    RESET_COLOR_CODE = "\033[0m"   # ANSI escape code to reset color

    def exec(self, prep_res, shared):
        print(f"{self.GRAY_COLOR_CODE}\nThanks for using the Freqtrade Download Assistant!{self.RESET_COLOR_CODE}")

    def post(self, shared, prep_res, exec_res):
        return None
