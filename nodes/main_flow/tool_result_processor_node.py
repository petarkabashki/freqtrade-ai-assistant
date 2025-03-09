from util.pocketflow import Node
import logging

logger = logging.getLogger(__name__)

class ToolResultProcessorNode(Node):
    def prep(self, shared):
        self.tool_request = shared.get("tool_request", {})
        return super().prep(shared)

    def exec(self, prep_res, shared):
        tool_results = shared.get("tool_results")
        llm_answer = shared.get("llm_answer")
        tool_error = shared.get("tool_error")
        tool_request_from_agent = shared.get("tool_request", {})
        tool_name = tool_request_from_agent.get("tool_name")

        if tool_results:
            logger.info("Tool Results Received:")
            logger.info(tool_results)
            if tool_name == "search_google": # if the tool was google search, decide if results are sufficient
                search_results = tool_results.get("organic_results", [])
                if search_results:
                    logger.info("Google Search Results Summary:")
                    for result in search_results[:3]: # Print top 3 snippets
                        logger.info(f"- {result.get('title')}: {result.get('snippet')}")
                    user_input = input("Are these search results helpful? (yes/no/retry)[y]: ")
                    if user_input.lower() in ['y', 'yes', '']:
                        return "tool_results_processed" # consider results processed if user says yes or default
                    elif user_input.lower() in ['n', 'no']:
                        return "tool_results_processing_needed" # signal for another loop if user says no
                    else:
                        return "tool_invocation_failure" # retry if user input is not yes/no
                return "tool_results_processed" # if no organic results, consider processed anyway for now
        elif llm_answer:
            logger.info("\nFinal Answer from LLM:")
            logger.info(llm_answer)
            return "llm_answer_ready"
        elif tool_error:
            logger.error(f"Tool Error: {tool_error}")
            return "tool_error_detected"
        else:
            logger.warning("No tool results, LLM answer, or tool error found.")
            return "no_results"


    def post(self, shared, prep_res, exec_res):
        logger.info(f"ToolResultProcessorNode post started. Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        if exec_res == "tool_results_processing_needed":
            action = "default" # loop back to agent for refinement if processing needed
        else:
            action = "processing_complete" # move to final answer if processed or other cases
        logger.info(f"ToolResultProcessorNode post finished. Action: {action}, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return action
