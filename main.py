
from src.repositories.email_repository import get_email_repository
from src.services.gmail_service import get_gmail_service
from src.services.rule_engine import RuleEngine
from config import appconfig
from logs import logs

def initialize_services():
    """Initialize services like Gmail and Email repository."""
    try:
        appconfig_instance = appconfig.AppConfig()

        # Initialize email repository
        email_repo = get_email_repository(appconfig_instance.database_file)
        email_repo.create_table()

        # Initialize Gmail service
        gmail_service = get_gmail_service(appconfig_instance.credentials_file, appconfig_instance.token_file, appconfig_instance.scopes)
        
        # Initialize Rule Engine
        rule_engine = RuleEngine(appconfig_instance.rules_file, gmail_service, logger)
        
        return email_repo, gmail_service, rule_engine
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise


def fetch_and_process_emails(gmail_service, email_repo, rule_engine):
    """Fetch emails and process them based on the rules."""
    try:
        emails = gmail_service.fetch_emails(1)

        for email in emails:
            email_repo.save(email)

        # emails = email_repo.get_all()
        # for email in emails:
        #     if email.status != 'read':
        #         rule_engine.process_email(email)
        #         email_repo.update_status(email.id, email.status)

    except Exception as e:
        logger.error(f"Error fetching or processing emails: {e}")
        raise


def main():
    """Main entry point for the application."""
    email_repo = None
    try:
        appconfig_instance = appconfig.AppConfig()
        # Setup logger
        global logger
        logger = logs.setup_logging(appconfig_instance.logs_file)

        # Initialize services
        email_repo, gmail_service, rule_engine = initialize_services()

        # Fetch and process emails
        fetch_and_process_emails(gmail_service, email_repo, rule_engine)

    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
    finally:
        # Ensure database connection is closed
            email_repo._conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    main()
