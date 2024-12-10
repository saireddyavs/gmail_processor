import base64
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import config
from src.models.email import Email
import os

logger = logging.getLogger("gmail_processor")

class GmailService:
    def __init__(self, credentials_path, token_path, scopes):
        self.service = self._get_authenticated_service(credentials_path, token_path, scopes)

    def _get_authenticated_service(self, credentials_path, token_path, scopes):
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes)
                creds = flow.run_local_server(port=0)
                
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, max_results=100):
        try:
            results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            emails = []
            for message in messages:
                raw_message = self.get_raw_message(message['id'])
                if raw_message:
                    email = Email.from_raw_message(raw_message)
                    emails.append(email)
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []


    def get_raw_message(self, message_id):
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, format='raw').execute()
            return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        except Exception as e:
            logger.error(f"Error getting raw message: {e}")
            return None

    def mark_as_read(self, message_id):
        try:
            self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
            logger.info(f"Marked message {message_id} as read.")
        except Exception as e:
            logger.error(f"Error marking message {message_id} as read: {e}")

    def mark_as_unread(self, message_id):
        try:
            self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()
            logger.info(f"Marked message {message_id} as unread.")
        except Exception as e:
            logger.error(f"Error marking message {message_id} as unread: {e}")


    def move_message(self, message_id, destination):
        try:
            self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': [destination]}).execute()
            logger.info(f"Moved message {message_id} to {destination}.")
        except Exception as e:
            logger.error(f"Error moving message {message_id} to {destination}: {e}")



def get_gmail_service(credential_file,token_file,scopes):
    return GmailService(credential_file,token_file,scopes)


