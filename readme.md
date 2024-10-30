# Web Content Change Detection ETL

This project is designed to periodically check specified websites for content changes and notify via Telegram if any changes are detected. The project uses Python, SQLAlchemy for database interactions, and APScheduler for scheduling periodic checks.

## Prerequisites

- Python 3.6+
- PostgreSQL
- Docker (optional, for containerized deployment)

## Setup

### 1. Clone the Repository

```sh
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a .env file in the root directory and add the following variables:

```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
URLS=<comma-separated-list-of-urls>
```

### 5. Initialize the Database

Run the following command to create the necessary database tables:

```sh
python -c "from etl import create_tables; create_tables()"
```

## Running the ETL

### 1. Run the ETL Script

```sh
python etl.py
```

This will start the scheduler to periodically check the websites specified in the [`URLS`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A50%2C%22character%22%3A0%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition") environment variable.

### 2. Docker Deployment (Optional)

To deploy the project using Docker, follow these steps:

1. Build the Docker image:

    ```sh
    docker build -t web-content-change-detector .
    ```

2. Run the Docker container:

    ```sh
    docker-compose up -d
    ```

## Project Structure

- etl.py: Main ETL script that checks websites for content changes and updates the database.
- .env : Environment variables configuration file.
- docker-compose.yaml: Docker Compose configuration for containerized deployment.
- Dockerfile: Dockerfile for building the Docker image.
- load-env.sh: Script to load environment variables.
- requirements.txt: Python dependencies.
- wait-for-it.sh: Script to wait for the database to be ready (used in Docker deployment).

## Functions

### [`fetch_content(url)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A56%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Fetches the content of the specified URL.

### [`hash_content(content)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A65%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Hashes the content to detect changes.

### [`save_website_state(db_session, url, content, content_hash)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A71%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Saves or updates the website state in the database.

### [`has_content_changed(db_session, url, new_content_hash)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A97%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Checks if the content has changed by comparing hashes.

### [`check_website(url)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A106%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Main function to check the website for changes.

### [`schedule_checks()`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A129%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Scheduler to periodically check the websites.

### [`send_telegram_message(message)`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fd%3A%2FUsers%2Fra10532a%2FDocuments%2F03_CodeTesting%2FCalling-Dips%2Fetl.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A42%2C%22character%22%3A4%7D%7D%5D%2C%22719335d9-e666-404a-b40f-a3c958a36907%22%5D "Go to definition")

Sends a message via Telegram.

## License

This project is licensed under the MIT License.

---

Feel free to customize this README to better fit your project's needs.