import json
import requests
import sqlite3
import smtplib
import subprocess
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from functools import lru_cache
import openai
import base64
import numpy as np
import yaml
import os
import logging

logger = logging.getLogger(__name__)
from serpapi import GoogleSearch

def search_web_tool(query):
    """Tool to search google for a query."""
    api_key = os.environ.get('SERPAPI_API_KEY')

    if not api_key:
        return {"error": "SERPAPI_API_KEY environment variable not set"}

    search = GoogleSearch({
    "q": query,
    # "location": "Austin,Texas",
    "api_key": api_key
    })
    result = search.get_dict()
    return result # AI: Return the search result


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
    return "PDF text extraction disabled due to missing library (fitz)"

def extract_text_from_image_pdf_tool(pdf_path, page_num=0):
    return "Image PDF text extraction disabled due to missing library (fitz)"


def user_input_tool(prompt):
    user_query = input(f"{prompt}: ")
    logger.info(f"User input received: {user_query}")
    return user_query


def user_output_tool(message):
    print(message)
    logger.info(f"User output displayed: {message}")
    return {"success": "Output displayed."}


def get_embedding_tool(text):
    # Dummy implementation for embedding
    logger.info(f"get_embedding_tool called with text: {text}")
    return np.random.rand(1536).tolist() # Return a dummy embedding of size 1536

def create_index_tool(embeddings):
    # Dummy implementation for index creation
    logger.info(f"create_index_tool called with embeddings of length: {len(embeddings)}")
    return "dummy_index" # Return a dummy index

def search_index_tool(index, query_embedding, top_k=5):
    # Dummy implementation for index search
    logger.info(f"search_index_tool called with index: {index}, query_embedding and top_k: {top_k}")
    return [([0, 1], [0.1, 0.2]) , ([2, 3], [0.3, 0.4])] # Return dummy index and distances

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
    return "Vision LLM calls disabled due to missing library (fitz)"
