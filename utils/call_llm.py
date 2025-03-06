from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

def call_llm(prompt):
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_response_content = response.choices[0].message.content
    print("Raw LLM Response:", raw_response_content) # Print raw response for debugging
    return raw_response_content

def get_embedding(text):
    client = OpenAI(api_key=API_KEY)
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding
