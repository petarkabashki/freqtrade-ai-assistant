import json

tool_descriptions = {
    "search_web": {
        "description": "Tool to search the web for information. To be used for claryfying the user's query, or find more about their intent - asset names, timeframes, etc.",
        "arguments": {
            "query": "string - use the original user input"
        }
    },
    # "execute_sql": {
    #     "description": "Tool to execute SQL queries.",
    #     "arguments": {
    #         "query": "string - The SQL query to execute."
    #     }
    # },
    # "run_code": {
    #     "description": "Tool to execute Python code.",
    #     "arguments": {
    #         "code_str": "string - The Python code to execute."
    #     }
    # },
    # "crawl_web": {
    #     "description": "Tool to crawl a webpage and extract text.",
    #     "arguments": {
    #         "url": "string - The URL of the webpage to crawl."
    #     }
    # },
    # "transcribe_audio": {
    #     "description": "Tool to transcribe audio from a file.",
    #     "arguments": {
    #         "file_path": "string - The file path to an audio file."
    #     }
    # },
    # "send_email": {
    #     "description": "Tool to send an email.",
    #     "arguments": {
    #         "to_address": "string - The recipient's email address.",
    #         "subject": "string - The email subject.",
    #         "body": "string - The email body text.",
    #         "from_address": "string - Your email address.",
    #         "password": "string - Your email password."
    #     }
    # },
    # "extract_text_from_pdf": {
    #     "description": "Tool to extract text from a PDF file.",
    #     "arguments": {
    #         "pdf_path": "string - The file path to a PDF file."
    #     }
    # },
    # "extract_text_from_image_pdf": {
    #     "description": "Tool to extract text from an image-based PDF file.",
    #     "arguments": {
    #         "pdf_path": "string - The file path to a PDF file.",
    #         "page_num": "integer - The page number to extract text from (default is 0)."
    #     }
    # },
    # "user_input": {
    #     "description": "Tool to get user input.",
    #     "arguments": {
    #         "prompt": "string - The prompt string to display to the user."
    #     }
    # },
    # "user_output": {
    #     "description": "Tool to display output to the user.",
    #     "arguments": {
    #         "message": "string - The message string to display."
    #     }
    # },
    # "get_embedding": {
    #     "description": "Tool to get embeddings for a text.",
    #     "arguments": {
    #         "text": "string - The text to embed."
    #     }
    # },
    # "create_index": {
    #     "description": "Tool to create an index from embeddings.",
    #     "arguments": {
    #         "embeddings": "list of embeddings - A list of embeddings to index."
    #     }
    # },
    # "search_index": {
    #     "description": "Tool to search an index with a query embedding.",
    #     "arguments": {
    #         "index": "index object - The index to search.",
    #         "query_embedding": "embedding - The embedding to query with.",
    #         "top_k": "integer - The number of top results to return (default is 5)."
    #     }
    # },
    # "call_llm": {
    #     "description": "Tool to call a Large Language Model with a prompt.",
    #     "arguments": {
    #         "prompt": "string - The prompt string for the LLM."
    #     }
    # },
    # "call_llm_vision": {
    #     "description": "Tool to call a vision-enabled Large Language Model with a prompt and image data.",
    #     "arguments": {
    #         "prompt": "string - The prompt string for the LLM.",
    #         "image_data": "image data - The image data for the LLM vision."
    #     }
    # },
    # "file_read": {
    #     "description": "Tool to read content from a file.",
    #     "arguments": {
    #         "file_path": "string - The file path to read from."
    #     }
    # },
    # "file_write": {
    #     "description": "Tool to write content to a file.",
    #     "arguments": {
    #         "file_path": "string - The file path to write to.",
    #         "content": "string - The content to write to the file."
    #     }
    # },
    # "directory_listing": {
    #     "description": "Tool to list files and directories in a given directory.",
    #     "arguments": {
    #         "dir_path": "string - The directory path to list."
    #     }
    # }
}

tool_descriptions_json = json.dumps(tool_descriptions, indent=4)

print(tool_descriptions_json)
