
from email.parser import BytesParser
from src.utils import parse_date_time
import logging


class Email:
    FIELD_MAPPING = {
        'From': 'sender',
        'To': 'receiver',
        'Subject': 'subject',
        'Message': 'message',
        'received_date': 'received_date'
    }

    def __init__(self, message_id, sender, receiver, subject, message, received_date, status=None):
        self.id = message_id
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.message = message
        self.received_date = received_date
        self.status = status  # Can be 'read', 'unread', etc.

    @classmethod
    def from_raw_message(cls, raw_message_bytes):
        try:
            # Parse the raw email bytes
            msg = BytesParser().parsebytes(raw_message_bytes)
            
            # Extract essential fields
            message_id = msg.get('Message-ID', None)
            sender = msg.get('From', None)
            receiver = msg.get('To', None)
            subject = msg.get('Subject', None)
            received_date = parse_date_time(msg.get('Date', None))
            
            # Extract message body
            message_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition', '')):
                        message_body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                message_body = msg.get_payload(decode=True).decode(errors='ignore')
            return cls(message_id, sender, receiver, subject, message_body, received_date)
        
        except Exception as e:
            logging.error(f"Failed to parse email: {e}")
            return None
        
    def get_field(self, field_name):
        mapped_field = self.FIELD_MAPPING.get(field_name, field_name)
        return getattr(self, mapped_field, None)

    def __repr__(self):
        return (
            f"<Email ID='{self.id}' From='{self.sender}' To='{self.receiver}' "
            f"Subject='{self.subject}' ReceivedDate='{self.received_date}'>"
        )
