import requests
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# File path to store the last known IP address
IP_FILE_PATH = '/opt/airflow/ip_address.txt'

def send_telegram_message(new_ip):
    """Send a message with the new IP address."""
    message = f"Your Raspberry Pi's IP address has changed to {new_ip}"
    response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        params={"chat_id": TELEGRAM_CHAT_ID, "text": message}
    )
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print(f"Telegram notification sent: {message}")

def get_public_ip():
    """Fetch the current public IP address."""
    response = requests.get('https://api.ipify.org')
    return response.text

def check_ip_change():
    """Check if the IP address has changed and update the stored IP."""
    current_ip = get_public_ip()
    saved_ip = None

    # Read the saved IP if it exists
    if os.path.exists(IP_FILE_PATH):
        with open(IP_FILE_PATH, "r") as file:
            saved_ip = file.read().strip()

    # If IP has changed, update the file and return the new IP for notification
    if current_ip != saved_ip:
        with open(IP_FILE_PATH, "w") as file:
            file.write(current_ip)
        return current_ip  # Return the new IP for notification
    return None

def notify_ip_change(**kwargs):
    """Check for IP change and notify if it has changed."""
    new_ip = check_ip_change()
    if new_ip:
        send_telegram_message(new_ip)
        print(f"IP changed to {new_ip}")
    else:
        print("IP has not changed.")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'ip_change_notifier',
    default_args=default_args,
    description='A DAG to notify IP address change via Telegram',
    schedule_interval=timedelta(minutes=60),  # runs every 60 minutes
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Task to check for IP change and notify
    check_and_notify_task = PythonOperator(
        task_id='check_and_notify_ip_change',
        python_callable=notify_ip_change,
        provide_context=True
    )

    # Define task dependencies (only one task here)
    check_and_notify_task
