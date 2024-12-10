import sqlite3
from config import config
from src.models.email import Email
import logging

logger = logging.getLogger("gmail_processor")

class EmailRepository:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def create_table(self):
        try:
            self._cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    receiver TEXT,
                    subject TEXT,
                    message TEXT,
                    received_date DATETIME,
                    status TEXT
                )
            ''')
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating emails table: {e}")
            raise

    def save(self, email):
        try:
            self._cursor.execute('''
                INSERT OR REPLACE INTO emails 
                (id, sender, receiver, subject, message, received_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email.id, email.sender, email.receiver, email.subject, email.message, email.received_date, email.status))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving email: {e}")
            raise

    def get_all(self):
        try:
            self._cursor.execute('SELECT id, sender, receiver, subject, message, received_date, status FROM emails')
            return [Email(*row) for row in self._cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching all emails: {e}")
            return []

    def get_by_id(self, email_id):
        try:
            self._cursor.execute('SELECT id, sender, receiver, subject, message, received_date, status FROM emails WHERE id = ?', (email_id,))
            row = self._cursor.fetchone()
            return Email(*row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error fetching email by ID: {e}")
            return None

    def update_status(self, email_id, status):
        try:
            self._cursor.execute("UPDATE emails SET status = ? WHERE id = ?", (status, email_id))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating status for email ID {email_id}: {e}")
            raise

    def delete_by_id(self, email_id):
        try:
            self._cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error deleting email by ID {email_id}: {e}")
            raise

    def delete_all(self):
        try:
            self._cursor.execute("DELETE FROM emails")
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("Error deleting all emails: {e}")
            raise


def get_email_repository():
    try:
        conn = sqlite3.connect(config.DATABASE_FILE)
        conn.row_factory = sqlite3.Row  # Allow column-based access for debugging
        return EmailRepository(conn)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to the database: {e}")
        raise
