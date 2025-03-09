import requests
import sqlite3
import os
from bs4 import BeautifulSoup
import openai
import smtplib
from email.mime.text import MIMEText

def search_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": "YOUR_API_KEY" # Consider using environment variable for API key
    }
    r = requests.get("https://serpapi.com/search", params=params)
    return r.json()

def file_read(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"

def file_write(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote content to file '{file_path}'"
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"

def directory_listing(dir_path):
    try:
        items = os.listdir(dir_path)
        return "\n".join(items)
    except FileNotFoundError:
        return f"Error: Directory not found at path '{dir_path}'"
    except NotADirectoryError:
        return f"Error: '{dir_path}' is not a directory"
    except Exception as e:
        return f"Error listing directory '{dir_path}': {e}"

def execute_sql(query):
    conn = sqlite3.connect("mydb.db") # Consider making db path configurable
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def run_code(code_str):
    env = {}
    exec(code_str, env) # Be extremely cautious with exec()
    return env

def crawl_web(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.string, soup.get_text()

def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file) # Requires openai.Audio
    return transcript["text"]

def send_email(to_address, subject, body, from_address, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server: # Gmail specific, might need to be more generic
        server.login(from_address, password)
        server.sendmail(from_address, [to_address], msg.as_string())
