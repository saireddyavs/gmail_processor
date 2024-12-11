import logging
import os

logger = logging.getLogger("gmail_processor")



def log_error_for_exception(context, exception):
    logger.error(f"Error in {context}: {exception}")
  
  

def setup_logging(logs_file):
    """Setup logger for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger("gmail_processor")
    logger.setLevel(logging.DEBUG)

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(logs_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Create a stream handler to print logs to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Customize the console format
    stream_handler.setFormatter(stream_formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info("Logger is set up and working.")
    return logger

    