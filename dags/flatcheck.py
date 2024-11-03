import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Directory to store website content and hashes
DATA_DIR = '/opt/airflow/data'
os.makedirs(DATA_DIR, exist_ok=True)

# Telegram bot setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URLS to monitor, separated by commas
URLS = os.getenv('URLS')
if URLS:
    URLS = [url.strip() for url in URLS.split(',') if url.strip()]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False
}

with DAG(
    'website_change_detection',
    default_args=default_args,
    description='A DAG to detect changes in website content',
    schedule_interval=timedelta(minutes=30),  # adjust interval as needed
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    def send_telegram_message(message):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.status_code} - {response.text}")
        else:
            print(f"Message sent successfully: {message}")

    def fetch_content(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def normalize_content(content):
        soup = BeautifulSoup(content, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        normalized_text = '\n'.join(chunk for chunk in chunks if chunk)
        return normalized_text

    def hash_content(content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_local_state_path(url):
        return os.path.join(DATA_DIR, hashlib.md5(url.encode('utf-8')).hexdigest())

    def has_content_changed(url, new_content_hash):
        state_path = get_local_state_path(url)
        if not os.path.exists(state_path):
            return True
        with open(state_path, 'r', encoding='utf-8') as f:
            old_content_hash = f.read().strip()
        return old_content_hash != new_content_hash

    def save_website_state(url, content, new_content_hash):
        state_path = get_local_state_path(url)
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(new_content_hash)
        content_path = f"{state_path}.html"
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def check_website(url):
        try:
            content = fetch_content(url)
            normalized_content = normalize_content(content)
            new_hash = hash_content(normalized_content)

            if has_content_changed(url, new_hash):
                message = f"Content has changed for {url}"
                print(message)
                send_telegram_message(message)
                save_website_state(url, content, new_hash)
            else:
                print(f"No changes for {url}")

        except Exception as e:
            print(f"Error checking {url}: {e}")
            send_telegram_message(f"Error checking {url}: {e}")

    def check_all_websites(**kwargs):
        for url in URLS:
            check_website(url)

    # Task to run the check_all_websites function
    check_websites_task = PythonOperator(
        task_id='check_all_websites',
        python_callable=check_all_websites,
        provide_context=True
    )
