from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

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
