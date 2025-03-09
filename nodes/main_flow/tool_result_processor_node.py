from util.pocketflow import Node

class ToolResultProcessorNode(Node):
    def exec(self, prep_res, shared):
        tool_results = shared.get("tool_results")
        llm_answer = shared.get("llm_answer")
        tool_error = shared.get("tool_error")

        if tool_results:
            print("Tool Results:")
            print(tool_results)
            return "tool_results_processed"
        elif llm_answer:
            print("LLM Answer:")
            print(llm_answer)
            return "llm_answer_processed"
        elif tool_error:
            print("Tool Error:")
            print(tool_error)
            return "tool_error_processed"
        else:
            print("No results to process.")
            return "no_results"

    def post(self, shared, prep_res, exec_res):
        if exec_res in ["tool_results_processed", "llm_answer_processed",
                           "tool_error_processed", "no_results"]:
            return "processing_complete"
        else:
            return "default"
