import base64
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.models.email import Email
import os

logger = logging.getLogger("gmail_processor")

class GmailService:
    def __init__(self, credentials_path, token_path, scopes):
        logger.info("Initializing GmailService...")
        self.service = self._get_authenticated_service(credentials_path, token_path, scopes)

    def _get_authenticated_service(self, credentials_path, token_path, scopes):
        logger.info("Authenticating Gmail service...")
        creds = None
        if os.path.exists(token_path):
            logger.info("Token file found. Loading credentials...")
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                logger.info("Credentials not found or invalid. Starting authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes)
                creds = flow.run_local_server(port=0)
            logger.info("Saving credentials to token file.")
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        logger.info("Authentication successful.")
        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, max_results=100):
        logger.info(f"Fetching up to {max_results} emails...")
        try:
            results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            emails = []
            for message in messages:
                logger.debug(f"Processing message ID: {message['id']}")
                raw_message = self.get_raw_message(message['id'])
                if raw_message:
                    email = Email.from_raw_message(raw_message, message['id'])
                    logger.debug(f"Parsed email: {email}")
                    emails.append(email)
            logger.info(f"Fetched {len(emails)} emails successfully.")
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def get_raw_message(self, message_id):
        logger.info(f"Fetching raw message for ID: {message_id}")
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, format='raw').execute()
            return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        except Exception as e:
            logger.error(f"Error fetching raw message for ID {message_id}: {e}")
            return None

    def mark_as_read(self, message_id):
        logger.info(f"Marking message {message_id} as read...")
        try:
            self.service.users().messages().modify(
                userId='me', 
                id=message_id, 
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Message {message_id} marked as read.")
        except Exception as e:
            logger.error(f"Error marking message {message_id} as read: {e}")
            raise e

    def mark_as_unread(self, message_id):
        logger.info(f"Marking message {message_id} as unread...")
        try:
            self.service.users().messages().modify(
                userId='me', 
                id=message_id, 
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Message {message_id} marked as unread.")
        except Exception as e:
            logger.error(f"Error marking message {message_id} as unread: {e}")
    
    def move_message(self, message_id, destination_name):
        logger.info(f"Moving message {message_id} to label '{destination_name}'...")
        label_id = self.get_label_id(destination_name)
        if not label_id:
            logger.error(f"Label '{destination_name}' not found. Unable to move message {message_id}.")
            return
        try:
            self.service.users().messages().modify(
                userId='me', 
                id=message_id, 
                body={'addLabelIds': [label_id]}
            ).execute()
            logger.info(f"Message {message_id} moved to label '{destination_name}'.")
        except Exception as e:
            logger.error(f"Error moving message {message_id} to label '{destination_name}': {e}")
            raise e

    def get_label_id(self, label_name):
        logger.info(f"Fetching label ID for label name: '{label_name}'...")
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    logger.debug(f"Found label '{label_name}' with ID: {label['id']}")
                    return label['id']
            logger.warning(f"Label '{label_name}' not found.")
            return None
        except Exception as e:
            logger.error(f"Error fetching labels: {e}")
            raise e


def get_gmail_service(credential_file, token_file, scopes):
    logger.info("Creating GmailService instance...")
    return GmailService(credential_file, token_file, scopes)
