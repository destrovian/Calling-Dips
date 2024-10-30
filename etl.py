import requests
from bs4 import BeautifulSoup
import bson
import hashlib
from sqlalchemy import create_engine, Column, String, LargeBinary, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# SQLAlchemy setup for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Telegram bot setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Base class for declarative models
Base = declarative_base()

# Define the WebsiteState model (equivalent to a table)
class WebsiteState(Base):
    __tablename__ = "website_states"
    
    url = Column(String, primary_key=True, index=True)
    last_fetched = Column(DateTime, default=datetime.now)
    html_bson = Column(LargeBinary)
    content_hash = Column(String)

# Initialize the database schema (if not already created)
def create_tables():
    Base.metadata.create_all(bind=engine)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    requests.post(url, data=payload)

URLS = os.getenv('URLS')

# If the URLs are separated by commas, split them into a list
if URLS:
    URLS = [url.strip() for url in URLS.split(',') if url.strip()]

def fetch_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# Hash the content to detect changes
def hash_content(content):
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()  # Extract textual content
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Save or update the website state
def save_website_state(db_session, url, content, content_hash):
    # Encode content as BSON
    bson_data = bson.dumps({'html': content})
    
    # Check if the URL already exists in the database
    state = db_session.query(WebsiteState).filter_by(url=url).first()
    
    if state:
        # Update existing record
        state.last_fetched = datetime.now()
        state.html_bson = bson_data
        state.content_hash = content_hash
    else:
        # Insert new record
        new_state = WebsiteState(
            url=url,
            last_fetched=datetime.now(),
            html_bson=bson_data,
            content_hash=content_hash
        )
        db_session.add(new_state)

    # Commit the transaction
    db_session.commit()

# Check if content has changed by comparing hashes
def has_content_changed(db_session, url, new_content_hash):
    state = db_session.query(WebsiteState).filter_by(url=url).first()
    
    if state is None:
        return True  # No previous record, treat as changed
    
    return state.content_hash != new_content_hash

# Main function to check the website for changes
def check_website(url):
    db_session = SessionLocal()
    
    try:
        print(f'getting content for {url}')
        content = fetch_content(url)
        new_hash = hash_content(content)

        if has_content_changed(db_session, url, new_hash):
            message = f"Content has changed for {url}"
            print(message)
            send_telegram_message(message)
            save_website_state(db_session, url, content, new_hash)
        else:
            print(f"No changes for {url}")

    except Exception as e:
        print(f"Error checking {url}: {e}")
        send_telegram_message(f"Error checking {url}: {e}")

    finally:
        db_session.close()

# Scheduler to periodically check the websites
def schedule_checks():
    #scheduler = BlockingScheduler()
    
    # Run the check every hour for each URL
    while True:
        for url in URLS:
            check_website(url)
            time.sleep(2)
        
        time.sleep(60)
        


if __name__ == "__main__":
    # Create the database tables
    create_tables()
    
    # Start the periodic checks
    schedule_checks()