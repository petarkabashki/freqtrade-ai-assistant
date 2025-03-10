from openai import OpenAI
import openai
import requests
import os
# import faiss as faiss # Changed import here
import numpy as np
import base64

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

# I need a way to use different models and providers, and add gemini, AI!
def call_llm(prompt):
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_response_content = response.choices[0].message.content

    print("Raw LLM Response:", raw_response_content) # Print raw response for debugging

    # Robustly remove markdown code fences by searching for them
    start_fence_yaml = "```yaml"
    start_fence_json = "```json"
    end_fence = "```"

    start_index = -1
    end_index = -1

    if start_fence_yaml in raw_response_content:
        start_index = raw_response_content.find(start_fence_yaml) + len(start_fence_yaml)
    elif start_fence_json in raw_response_content:
        start_index = raw_response_content.find(start_fence_json) + len(start_fence_json)

    if start_index != -1:
        end_index = raw_response_content.rfind(end_fence) # Find last occurrence

    if start_index != -1 and end_index != -1 and end_index > start_index:
        raw_response_content = raw_response_content[start_index:end_index].strip() # Extract content between fences


    return raw_response_content

def get_embedding(text):
    client = OpenAI(api_key=API_KEY)
    r = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return r.data[0].embedding

# def search_index(index, query_embedding, top_k=5):
#     import faiss
#     import numpy as np
#     D, I = index.search(
#         np.array([query_embedding]).astype('float32'),
#         top_k
#     )
#     return I, D


def call_llm_vision(prompt, image_data):
    client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")
    img_base64 = base64.b64encode(image_data).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"image/png;base64,{img_base64}"}}
            ]
        }]
    )
    return response.choices[0].message.content
