from openai import OpenAI
import openai
import requests
import os
# import faiss as faiss # Changed import here
import numpy as np
import base64

import google.generativeai as genai # Import google.generativeai for Gemini

import yaml # Import yaml to read config

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Get Google API Key

# Load config.yaml to read llm configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

llm_config = config.get('llm', {})
llm_provider = llm_config.get('provider', 'openai') # Default to openai if not configured
llm_model = llm_config.get('model', 'gpt-4o-mini')   # Default model


def call_llm(prompt):
    if llm_provider == 'openai':
        return call_openai_llm(prompt, llm_model)
    elif llm_provider == 'gemini':
        return call_gemini_llm(prompt, llm_model)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def call_openai_llm(prompt, model_name):
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    raw_response_content = response.choices[0].message.content

    print("Raw LLM Response (OpenAI):", raw_response_content) # Print raw response for debugging

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


def call_gemini_llm(prompt, model_name):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name) # Use model_name from config
    response = model.generate_content(prompt)
    raw_response_content = response.text

    print("Raw LLM Response (Gemini):", raw_response_content) # Print raw response for debugging

    # Robustly remove markdown code fences - Gemini uses markdown too
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
