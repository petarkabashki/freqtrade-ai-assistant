from util.pocketflow import Node
import logging
from util.llm_tools.core_tools import get_embedding_tool, search_index_tool, create_index_tool
import numpy as np # Import numpy


logger = logging.getLogger(__name__)

class ChatRetrieveNode(Node):
    def prep(self, shared):
        shared.setdefault("history", [])
        shared.setdefault("memory_index", None)
        user_input = input("You: ")
        if user_input.strip().lower() == '/q':
            return "quit"  # Return "quit" as prep_res if user input is '/q'
        logger.info(f"ChatRetrieveNode prep finished. Prep result: {user_input}, Shared: {shared}")
        return user_input

    def exec(self, prep_res, shared):
        if prep_res == "quit": # Check if prep_res is "quit"
            return "quit" # Return "quit" as exec_res
        user_input = prep_res
        emb_res = get_embedding_tool(user_input) # Use get_embedding_tool
        if "error" in emb_res:
            logger.error(f"Embedding error: {emb_res['error']}")
            return {"error": "Embedding failed"}
        emb = emb_res
        relevant = []
        if len(shared["history"]) > 8 and shared["memory_index"]:
            index = shared["memory_index"]
            search_res = search_index_tool(index, emb, top_k=2) # Use search_index_tool
            if "error" in search_res:
                logger.error(f"Vector search error: {search_res['error']}")
                return {"error": "Vector search failed"}
            idx, _ = search_res
            relevant = [shared["history"][i[0]] for i in idx[0]] if idx is not None and len(idx) > 0 and len(idx[0]) > 0 else [] # Handle cases where idx might be None or empty
        logger.info(f"ChatRetrieveNode exec finished. Prep result: {user_input}, Exec result: {(user_input, relevant)}, Shared: {shared}")
        return (user_input, relevant)

    def post(self, shared, prep_res, exec_res):
        if exec_res == "quit": # Check if exec_res is "quit"
            return "quit" # Return "quit" action
        user_input, relevant = exec_res
        shared["user_input"] = user_input
        shared["relevant"] = relevant
        logger.info(f"ChatRetrieveNode post finished. Action: continue, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return "continue"
