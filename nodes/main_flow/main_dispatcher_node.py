from lib.pocketflow import Node
from lib.call_llm import call_llm # Keep call_llm
from lib.tools import search_google # Import search_google from lib.tools

class MainDispatcherNode(Node):
    def exec(self, prep_res, shared):
        user_input = prep_res
        prompt = f"""
        User request: {user_input}

        Analyze the user request and determine:
        - Does it require an external tool? (yes/no)
        - If yes, which tool is most appropriate from these options:
          - search_google: for general web search

        - What are the parameters needed to execute the tool?

        Respond in YAML format:
        \`\`\`yaml
        tool_needed: yes/no
        tool_name: <tool_name>  # e.g., search_google (if tool_needed is yes)
        tool_params:             # Parameters for the tool (if tool_needed is yes)
          <param_name_1>: <param_value_1>
        reason: <brief reason for the decision>
        \`\`\`"""
        llm_response_yaml = call_llm(prompt)
        # Parse YAML response (assuming llm_response_yaml is a YAML string)
        import yaml
        try:
            llm_response_data = yaml.safe_load(llm_response_yaml)
        except yaml.YAMLError as e:
            print(f"Error parsing LLM YAML response: {e}")
            return "yaml_error" # Action for YAML parsing error

        tool_needed = llm_response_data.get("tool_needed")
        tool_name = llm_response_data.get("tool_name")
        tool_params = llm_response_data.get("tool_params", {}) # Default to empty dict if no params

        if tool_needed == "yes":
            if tool_name == "search_google":
                query = tool_params.get("query") # Assuming 'query' is the param for search_google
                if query:
                    tool_result = search_google(query=query) # Execute search_google
                else:
                    tool_result = {"error": "Missing query parameter for search_google"}
            else:
                tool_result = {"error": f"Unknown tool requested: {tool_name}"}

            shared["tool_results"] = tool_result # Store tool results in shared

            if "error" in tool_result:
                print(f"Tool execution error: {tool_result['error']}")
                return "tool_failure" # Action for tool failure
            else:
                print(f"Tool execution successful. Results stored in shared['tool_results']")
                return "tool_success"  # Action for tool success

        else: # tool_needed != "yes" (can be "no" or None if LLM fails to decide)
            llm_prompt_answer = f"User request: {user_input}\n Directly answer the request:"
            llm_answer = call_llm(llm_prompt_answer)
            shared["llm_answer"] = llm_answer
            print(f"Direct LLM Answer: {llm_answer}")
            return "answer_directly" # Action for direct answer

    def post(self, shared, prep_res, exec_res):
        if exec_res == "tool_success":
            return "tool_results_ready" # Transition to node that processes tool results
        elif exec_res == "tool_failure":
            return "tool_error"       # Transition to error handling node
        elif exec_res == "answer_directly":
            return "direct_answer_ready" # Transition to node that handles direct answer
        elif exec_res == "yaml_error":
            return "yaml_error" # Transition for YAML parsing error
        else:
            return "default" # Default action if none of the above
