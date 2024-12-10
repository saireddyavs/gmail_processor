import logging


logger = logging.getLogger("gmail_processor")



def log_error_for_exception(context, exception):
    logger.error(f"Error in {context}: {exception}")
    