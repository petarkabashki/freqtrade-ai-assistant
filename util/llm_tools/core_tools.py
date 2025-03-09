import json
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
import yaml
import os
import logging

logger = logging.getLogger(__name__)


# from util.llm_tools.fs_tools import file_read, file_write, directory_listing, ALLOWED_PATHS # Import file tools


def search_google_tool(query):
    # https://serpapi.com/search-api
    api_key = os.environ.get('SERPAPI_API_KEY')
    if not api_key:
        return {"error": "SERPAPI_API_KEY environment variable not set"}
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    r = requests.get("https://serpapi.com/search", params=params)
    if r.status_code == 200:
        return r.json()
    else:
        logger.error(f"SerpAPI request failed with status code: {r.status_code}")
        return {"error": f"SerpAPI request failed with status code: {r.status_code}"}


def execute_sql_tool(query):
    conn = sqlite3.connect("mydb.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        return result
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return {"error": f"Database error: {e}"}
    finally:
        conn.close()

def run_code_tool(code_str):
    env = {}
    try:
        exec(code_str, env)
        return env
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        return {"error": f"Error executing code: {e}"}


def crawl_web_tool(url):
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.string, soup.get_text()
    except requests.RequestException as e:
        logger.error(f"Error crawling web page {url}: {e}")
        return {"error": f"Error crawling web page {url}: {e}"}


def transcribe_audio_tool(file_path):
    # https://platform.openai.com/docs/api-reference/audio/transcriptions
    try:
        audio_file= open(file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio file {file_path}: {e}")
        return {"error": f"Error transcribing audio file {file_path}: {e}"}


def send_email_tool(to_address, subject, body, from_address, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_address, password)
            server.sendmail(from_address, [to_address], msg.as_string())
        return {"success": f"Email sent to {to_address}"}
    except Exception as e:
        logger.error(f"Error sending email to {to_address}: {e}")
        return {"error": f"Error sending email to {to_address}: {e}"}


def extract_text_from_pdf_tool(pdf_path):
    # doc = fitz.open(pdf_path) # Commented out
    # text = ""
    # for page in doc:
    #     text += page.get_text()
    # doc.close()
    # return text
    return "PDF text extraction disabled due to missing library (fitz)" # Modified to return a message


def extract_text_from_image_pdf_tool(pdf_path, page_num=0): # page_num is 0-based
    # pdf_document = fitz.open(pdf_path) # Commented out
    # page = pdf_document[page_num]
    # pix = page.get_pixmap()
    # img_data = pix.tobytes("png")
    # prompt = "Extract text from this image in detail. If there are tables, extract them in markdown format."
    # return call_llm_vision_tool(prompt, img_data)
    return "Image PDF text extraction disabled due to missing library (fitz)" # Modified to return a message


def user_input_tool(prompt): # Renamed from user_input_llm_query_tool to user_input_tool
    user_query = input(f"{prompt}: ")
    logger.info(f"User input received: {user_query}")
    return user_query


def user_output_tool(message):
    print(message)
    logger.info(f"User output displayed: {message}")
    return {"success": "Output displayed."}


def get_embedding_tool(text):
    client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")
    try:
        r = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return r.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding for text: {e}")
        return {"error": f"Error getting embedding for text: {e}"}


def search_index_tool(index, query_embedding, top_k=5):
    try:
        D, I = index.search(
            np.array([query_embedding]).astype('float32'),
            top_k
        )
        return I, D
    except Exception as e:
        logger.error(f"Error searching index: {e}")
        return {"error": f"Error searching index: {e}"}


def call_llm_tool(prompt):
    client = openai.OpenAI(api_key="YOUR_API_KEY_HERE")
    try:
        r = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {"error": f"LLM call failed: {e}"}


def call_llm_vision_tool(prompt, image_data):
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
