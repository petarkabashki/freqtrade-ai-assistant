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


# def create_index(embeddings):
#     dim = len(embeddings[0])
#     index = faiss.IndexFlatL2(dim)
#     index.add(np.array(embeddings).astype('float32'))
#     return index

def search_index(index, query_embedding, top_k=5):
    D, I = index.search(
        np.array([query_embedding]).astype('float32'), 
        top_k
    )
    return I, D

# index = create_index(embeddings)
# search_index(index, query_embedding)

import sqlite3

def execute_sql(query):
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

# run_code("print('Hello, world!')")

# import fitz  # PyMuPDF

# def extract_text(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     doc.close()
#     return text

# extract_text("document.pdf")

# def call_llm_vision(prompt, image_data):
#     client = OpenAI(api_key=API_KEY)
#     img_base64 = base64.b64encode(image_data).decode('utf-8')

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[{
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": prompt},
#                 {"type": "image_url", 
#                  "image_url": {"url": f"image/png;base64,{img_base64}"}}
#             ]
#         }]
#     )

#     return response.choices[0].message.content

# pdf_document = fitz.open("document.pdf")
# page_num = 0
# page = pdf_document[page_num]
# pix = page.get_pixmap()
# img_data = pix.tobytes("png")

# call_llm_vision("Extract text from this image", img_data)

def crawl_web(url):
    from bs4 import BeautifulSoup
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string, soup.get_text()


def search_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": "YOUR_API_KEY"
    }
    r = requests.get("https://serpapi.com/search", params=params)
    return r.json()

def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

# def text_to_speech(text):
#     import pyttsx3
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

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
