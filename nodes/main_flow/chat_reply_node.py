from util.pocketflow import Node
from util.call_llm import call_llm
import logging
from util.llm_tools.core_tools import get_embedding_tool, create_index_tool
import numpy as np # Ensure numpy is imported


logger = logging.getLogger(__name__)

class ChatReplyNode(Node):
    def prep(self, shared):
        user_input = shared["user_input"]
        recent = shared["history"][-8:]
        relevant = shared.get("relevant", [])
        logger.info(f"ChatReplyNode prep finished. Prep result: {(user_input, recent, relevant)}, Shared: {shared}")
        return user_input, recent, relevant

    def exec(self, prep_res, shared):
        user_input, recent, relevant = prep_res
        msgs = [{"role":"system","content":"You are a helpful AI assistant for financial data analysis."}]
        if relevant:
            relevant_content = "\n".join([rel['content'] for rel in relevant]) # Extract content from relevant messages
            msgs.append({"role":"system","content":f"Relevant context from past conversation: {relevant_content}"})
        msgs.extend(recent)
        msgs.append({"role":"user","content":user_input})
        ans = call_llm(msgs)
        logger.info(f"ChatReplyNode exec finished. Prep result: {prep_res}, Exec result: {ans}, Shared: {shared}")
        return ans

    def post(self, shared, prep_res, exec_res):
        user_input, _, _ = prep_res
        assistant_response = exec_res
        shared["history"].append({"role":"user","content":user_input})
        shared["history"].append({"role":"assistant","content":assistant_response})

        # Manage memory index
        if len(shared["history"]) == 8 and shared["memory_index"] is None: # Check if memory_index is None before creating
            embs = []
            for i in range(0, 8, 2):
                text = shared["history"][i]["content"] + " " + shared["history"][i+1]["content"]
                emb_res = get_embedding_tool(text) # Use get_embedding_tool
                if "error" in emb_res:
                    logger.error(f"Embedding error during index creation: {emb_res['error']}")
                    return "embedding_error" # Handle embedding error
                embs.append(emb_res)
            shared["memory_index"] = create_index_tool(embs) # Use create_index_tool
        elif len(shared["history"]) > 8 and shared["memory_index"] is not None: # Check if memory_index is not None before adding
            text = shared["history"][-2]["content"] + " " + shared["history"][-1]["content"]
            new_emb_res = get_embedding_tool(text) # Use get_embedding_tool
            if "error" in new_emb_res:
                logger.error(f"Embedding error during index update: {new_emb_res['error']}")
                return "embedding_error" # Handle embedding error
            new_emb = np.array([new_emb_res]).astype('float32')
            index = shared["memory_index"]
            # Check if index is not None before adding
            if index is not None:
                index.add(new_emb)
            else:
                logger.warning("Memory index is None, cannot add new embedding.")


        print(f"Assistant: {assistant_response}") # Keep user output for now
        logger.info(f"ChatReplyNode post finished. Action: continue, Shared: {shared}, Prep result: {prep_res}, Exec result: {exec_res}")
        return "continue"
