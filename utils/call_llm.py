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

    # Remove markdown code fences if present
    if raw_response_content.startswith("```json") and raw_response_content.endswith("```"):
        raw_response_content = raw_response_content[7:-3].strip() # Remove ```json and ``` and any extra whitespace

    return raw_response_content
