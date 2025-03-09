from lib.pocketflow import Node
from lib.call_llm import call_llm

class MainDispatcherNode(Node):
    def exec(self, prep_res, shared):
        user_input = prep_res
        prompt = f"Process this user input: {user_input}"
        llm_response = call_llm(prompt)
        return llm_response

    def post(self, shared, prep_res, exec_res):
        print(f"LLM Response: {exec_res}")
        shared['llm_response'] = exec_res
        return "input"
