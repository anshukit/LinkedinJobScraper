DATA_DIR = "data"

BATCH_SIZE = 100
DELAY_SEC = 10  # Delay between scraping batches
EMAIL_LIMIT = 100
EMAIL_BATCH_SIZE = 10
EMAIL_BATCH_DELAY = 5  # Delay between email batches in seconds

import os
from typing import Dict

class Config:
    def __init__(self):
        self.data_dir = "data"
        self.logs_dir = "logs"
        self.resume_path = os.getenv("RESUME_PATH", "resume.pdf")
        self.linkedin_cookie = os.getenv("LINKEDIN_LI_AT", "")
        self.email_accounts = os.getenv("EMAIL_ACCOUNTS", "").split(",")
        
        # AI config (if needed)
        class AI:
            def __init__(self):
                self.api_key = os.getenv("AZURE_OPENAI_KEY", "")
                self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
                self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        self.ai = AI()

        # App constants
        self.batch_size = 100
        self.delay_sec = 10
        self.email_limit = 100
        self.email_batch_size = 10
        self.email_batch_delay = 5

    def get_file_paths(self) -> Dict[str, str]:
        """Get all data file paths"""
        return {
            "all_posts": os.path.join(self.data_dir, "all_linkedin_posts.jsonl"),
            "eligible_posts": os.path.join(self.data_dir, "eligible_posts.jsonl"),
            "mail_posts": os.path.join(self.data_dir, "mail_sent_posts.jsonl"),
            "apply_posts": os.path.join(self.data_dir, "only_apply_links.jsonl"),
            "apply_csv": os.path.join(self.data_dir, "apply_links.csv"),
            "email_log": os.path.join(self.data_dir, "email_log.csv"),
            "scraping_log": os.path.join(self.logs_dir, "scraping.log"),
            "email_sending_log": os.path.join(self.logs_dir, "email_sending.log")
        }

# Global configuration instance
config = Config()
