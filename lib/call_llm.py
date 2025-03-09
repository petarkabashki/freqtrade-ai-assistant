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

def search_index(index, query_embedding, top_k=5):
    import faiss
    import numpy as np
    D, I = index.search(
        np.array([query_embedding]).astype('float32'),
        top_k
    )
    return I, D

def execute_sql(query):
    import sqlite3
    conn = sqlite3.connect("mydb.db")
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def run_code(code_str):
    env = {}
    exec(code_str, env)
    return env

def crawl_web(url):
    from bs4 import BeautifulSoup
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string, soup.get_text()

def search_google(query):
    import requests
    params = {
        "engine": "google",
        "q": query,
        "api_key": "YOUR_API_KEY"
    }
    r = requests.get("https://serpapi.com/search", params=params)
    return r.json()

def transcribe_audio(file_path):
    import openai
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def send_email(to_address, subject, body, from_address, password):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_address, password)
        server.sendmail(from_address, [to_address], msg.as_string())

def file_read(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"

def file_write(file_path, content"):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote content to file '{file_path}'"
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"

def directory_listing(dir_path):
    import os
    try:
        items = os.listdir(dir_path)
        return "\n".join(items)
    except FileNotFoundError:
        return f"Error: Directory not found at path '{dir_path}'"
    except NotADirectoryError:
        return f"Error: '{dir_path}' is not a directory"
    except Exception as e:
        return f"Error listing directory '{dir_path}': {e}"
