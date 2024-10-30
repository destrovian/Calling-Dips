import os
import time
import requests
import logging
from telegram import Bot
import psycopg2
from psycopg2 import sql

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize the Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Function to check if the database is ready
def check_database_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        logging.info("Connected to the database successfully.")
        return True
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return False

URLS = os.getenv('URLS')

if URLS:
    URLS = [url.strip() for url in URLS.split(",") if url.strip()]
else:
    print("No URLs found.")

# Function to check the website
def check_website():
    for url in URLS:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f"{url} is up!")
            else:
                logging.warning(f"{url} returned status code {response.status_code}")
                send_alert(f"{url} is down! Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error checking {url}: {e}")
            send_alert(f"Error checking {url}: {e}")

# Function to send alerts to Telegram
def send_alert(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info("Alert sent to Telegram.")
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

# Main function to control the flow of the application
def main():
    database_ready = False

    # Wait for the database to be ready
    while not database_ready:
        database_ready = check_database_connection()
        if not database_ready:
            logging.info("Waiting for database...")
            time.sleep(5)  # Wait before retrying

    interval = 60  # Check every 60 seconds

    # Start checking the website
    while True:
        check_website()
        time.sleep(interval)

if __name__ == "__main__":
    main()
