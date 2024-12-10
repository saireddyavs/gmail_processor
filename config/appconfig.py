
from config import config

class AppConfig:
    def __init__(self):
        self.database_file = config.DATABASE_FILE
        self.rules_file = config.RULES_FILE
        self.scopes = config.SCOPES
        self.credentials_file = config.CREDENTIALS_FILE
        self.token_file = config.TOKEN_FILE
        self.logs_file = config.LOGS_FILE
