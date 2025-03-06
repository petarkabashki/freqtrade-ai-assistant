from pocketflow import Node
from utils.call_llm import call_llm # Changed import to utils.call_llm - VERIFY THIS IS CORRECT

class SummaryNode(Node):
    def prep(self, shared):
        command_output = shared['command_output']
        return command_output

    def exec(self, prep_res, shared):
        output_message = prep_res['output_message']
        command = prep_res['command']

        # --- LLM Summary ---
        summary_prompt = f"""
        Please summarize the output of the following terminal command.
        Command: `{command}`
        Output:
        ```
        {output_message}
        ```
        Focus on the outcome (success/failure, any errors) and provide a concise summary.
        """
        summary = call_llm(summary_prompt) # Assuming call_llm is defined

        return {'summary_message': summary}


    def post(self, shared, prep_res, exec_res):
        print("\n--- Download Summary ---")
        print(exec_res['summary_message'])
        print("---\n")

        # Save last valid inputs to shared memory
        validated_input = shared['validated_input']
        # save_shared_memory(validated_input) # Removed from here, should be in summary node
        return 'input' # Loop back to input for next download
