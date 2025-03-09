import json
import os
import requests
import sqlite3
import smtplib
import subprocess
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from functools import lru_cache
import openai # Added import here
import base64
# import fitz  # PyMuPDF # Commented out import
import numpy as np # Added import here


def search_google(query):
    # https://serpapi.com/search-api
    params = {
        "engine": "google",
        "q": query,
        "api_key": "YOUR_API_KEY" #  https://serpapi.com/dashboard
    }
    r = requests.get("https://serpapi.com/search", params=params)
    return r.json()

def file_read(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def file_write(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)

def directory_listing(dir_path):
    return os.listdir(dir_path)

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

def crawl_web(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string, soup.get_text()

def transcribe_audio(file_path):
    # https://platform.openai.com/docs/api-reference/audio/transcriptions
    audio_file= open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def send_email(to_address, subject, body, from_address, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_address, password)
        server.sendmail(from_address, [to_address], msg.as_string())

def extract_text_from_pdf(pdf_path):
    # doc = fitz.open(pdf_path) # Commented out
    # text = ""
    # for page in doc:
    #     text += page.get_text()
    # doc.close()
    # return text
    return "PDF text extraction disabled due to missing library (fitz)" # Modified to return a message

def extract_text_from_image_pdf(pdf_path, page_num=0): # page_num is 0-based
    # pdf_document = fitz.open(pdf_path) # Commented out
    # page = pdf_document[page_num]
    # pix = page.get_pixmap()
    # img_data = pix.tobytes("png")
    # prompt = "Extract text from this image in detail. If there are tables, extract them in markdown format."
    # return call_llm_vision(prompt, img_data)
    return "Image PDF text extraction disabled due to missing library (fitz)" # Modified to return a message

def user_input_llm_query(prompt):
    user_query = input(f"{prompt}: ")
    return user_query

def user_output(message):
    print(message)
    return {}


def get_embedding(text):
    client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")
    r = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return r.data[0].embedding

def search_index(index, query_embedding, top_k=5):
    D, I = index.search(
        np.array([query_embedding]).astype('float32'),
        top_k
    )
    return I, D

def call_llm(prompt):
    client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def call_llm_vision(prompt, image_data):
    # client = openai.OpenAI(api_key="YOUR_API_KEY_HERE") # Commented out
    # img_base64 = base64.b64encode(image_data).decode('utf-8') # Commented out

    # response = client.chat.completions.create( # Commented out
    #     model="gpt-4o", # Commented out
    #     messages=[{ # Commented out
    #         "role": "user", # Commented out
    #         "content": [ # Commented out
    #             {"type": "text", "text": prompt}, # Commented out
    #             {"type": "image_url",  # Commented out
    #              "image_url": {"url": f"image/png;base64,{img_base64}"}} # Commented out
    #         ] # Commented out
    #     }] # Commented out
    # ) # Commented out
    # return response.choices[0].message.content # Commented out
    return "Vision LLM calls disabled due to missing library (fitz)" # Modified to return a message
