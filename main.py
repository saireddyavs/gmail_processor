import logging
import os
from config import config
from src.repositories.email_repository import get_email_repository
from src.services.gmail_service import get_gmail_service
from src.services.rule_engine import RuleEngine
from config import appconfig


# --- Logging Setup ---
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger("gmail_processor")
logger.setLevel(logging.INFO)

# Create a file handler to write logs to a file
file_handler = logging.FileHandler("logs/gmail_processor.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Create a stream handler to print logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Customize the console format
stream_handler.setFormatter(stream_formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Example usage
logger.info("Logger is set up and working.")

if __name__ == "__main__":
    appconfig=appconfig.AppConfig()
    email_repo = get_email_repository(appconfig.database_file)
    email_repo.create_table()

    gmail_service = get_gmail_service(appconfig.credentials_file,appconfig.token_file,appconfig.scopes)
    rule_engine = RuleEngine(appconfig.rules_file, gmail_service,logger)

    emails = gmail_service.fetch_emails(1)

    # for email in emails:
    #     email_repo.save(email)

    # emails = email_repo.get_all()
    # for email in emails:
    #     if email.status != 'read':
    #         rule_engine.process_email(email)
    #         email_repo.update_status(email.id, email.status)

    email_repo._conn.close()
