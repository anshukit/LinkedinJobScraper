import os
import json
import csv
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)
from config import DATA_DIR

def load_keywords(file_path) -> list[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Keyword file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
class DataValidator:
    @staticmethod
    def validate_post_data(post: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = {
            "Post_Index": 1,
            "Is_Job_Post": False,
            "Role": "Not Provided",
            "Company": "Not Provided",
            "Apply_Link": "Not Provided",
            "Contact_Email": "Not Provided",
            "Eligibility": "Not Eligible",
            "Job_Description": ""
        }
        for field, default in required_fields.items():
            if field not in post or post[field] is None:
                post[field] = default

        post["Is_Job_Post"] = bool(post.get("Is_Job_Post", False))
        post["Post_Index"] = int(post.get("Post_Index", 1))

        for field in ["Role", "Company", "Apply_Link", "Contact_Email", "Job_Description"]:
            if isinstance(post.get(field), str):
                post[field] = post[field].strip()
                if not post[field] or post[field].lower() in ["none", "null", "n/a", ""]:
                    post[field] = "Not Provided"

        email = post.get("Contact_Email", "")
        if email != "Not Provided" and not DataValidator.is_valid_email(email):
            logger.warning(f"Invalid email format: {email}")
            post["Contact_Email"] = "Not Provided"

        url = post.get("Apply_Link", "")
        if url != "Not Provided" and not DataValidator.is_valid_url(url):
            logger.warning(f"Invalid URL format: {url}")
            post["Apply_Link"] = "Not Provided"

        return post

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email or email == "Not Provided":
            return False
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()))

    @staticmethod
    def is_valid_url(url: str) -> bool:
        if not url or url == "Not Provided":
            return False
        return bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', url.strip()))


class FileManager:
    def __init__(self):
        self.file_paths = config.get_file_paths()

    def ensure_directory_exists(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def load_json_safe(file_path):
        """Load JSON safely, return [] if file is empty or invalid."""
        if not os.path.exists(file_path):
            logging.warning(f"⚠️ File not found: {file_path}")
            return []

        if os.path.getsize(file_path) == 0:
            logging.warning(f"⚠️ File is empty: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"❌ Error loading jobs from {file_path}: {e}")
            return []

    # def save_jsonl_safe(self, data_list: List[Dict[str, Any]], file_path: str) -> bool:
    #     """Overwrite JSONL file directly (no backups)."""
    #     try:
    #         self.ensure_directory_exists(file_path)
    #         validated_data = [
    #             DataValidator.validate_post_data(item.copy())
    #             for item in data_list if isinstance(item, dict)
    #         ]
    #         with open(file_path, "w", encoding="utf-8") as f:
    #             for item in validated_data:
    #                 f.write(json.dumps(item, ensure_ascii=False) + "\n")
    #         logger.info(f"Saved {len(validated_data)} items to {file_path}")
    #         return True
    #     except Exception as e:
    #         logger.error(f"Error saving JSONL file {file_path}: {e}")
    #         return False

    def save_csv_safe(self, data_list: List[Dict[str, Any]], file_path: str,
                      fieldnames: List[str] = None) -> bool:
        """Overwrite CSV file directly (no backups)."""
        try:
            self.ensure_directory_exists(file_path)
            if not data_list:
                logger.warning("No data to save to CSV")
                return False

            if not fieldnames:
                fieldnames = ["Role", "Company", "Location", "Apply_Link", "Contact_Email", "Eligibility"]

            valid_data = [
                item for item in data_list
                if isinstance(item, dict) and (
                    DataValidator.is_valid_url(item.get("Apply_Link", "")) or
                    DataValidator.is_valid_email(item.get("Contact_Email", ""))
                )
            ]
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for item in valid_data:
                    writer.writerow({field: item.get(field, "Not Provided") for field in fieldnames})
            logger.info(f"Saved {len(valid_data)} items to CSV: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV file {file_path}: {e}")
            return False

    def load_jsonl_safe(self, file_path: str) -> List[Dict[str, Any]]:
        """Load JSONL file safely."""
        data = []
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return data
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        item = json.loads(line.strip())
                        if isinstance(item, dict):
                            data.append(item)
                    except json.JSONDecodeError:
                        logger.error(f"JSON decode error at line {line_num}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []


class DataProcessor:
    def __init__(self):
        self.file_manager = FileManager()

    def get_data_statistics(self) -> Dict[str, Any]:
        stats = {
            "files": {},
            "summary": {
                "total_posts": 0,
                "eligible_posts": 0,
                "posts_with_emails": 0,
                "posts_with_apply_links": 0,
                "emails_sent": 0
            }
        }
        paths = config.get_file_paths()
        for file_type, file_path in paths.items():
            if file_path.endswith(".jsonl"):
                data = self.file_manager.load_jsonl_safe(file_path)
                stats["files"][file_type] = {
                    "count": len(data),
                    "file_exists": os.path.exists(file_path),
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
                if file_type == "all_posts":
                    stats["summary"]["total_posts"] = len(data)
                elif file_type == "eligible_posts":
                    stats["summary"]["eligible_posts"] = len(data)
                elif file_type == "mail_posts":
                    stats["summary"]["posts_with_emails"] = len(data)
                elif file_type == "apply_posts":
                    stats["summary"]["posts_with_apply_links"] = len(data)

        email_log = paths.get("email_log")
        if email_log and os.path.exists(email_log):
            try:
                with open(email_log, "r", encoding="utf-8") as f:
                    stats["summary"]["emails_sent"] = sum(1 for _ in f)
            except Exception as e:
                logger.error(f"Email log error: {e}")
        return stats


# --- Global Instances and Helper Functions ---
file_manager = FileManager()
data_processor = DataProcessor()

def save_jsonl(data_list: List[Dict[str, Any]], file_path: str) -> None:
    file_manager.save_jsonl_safe(data_list, file_path)

def save_csv(data_list: List[Dict[str, Any]], file_path: str) -> None:
    file_manager.save_csv_safe(data_list, file_path)

def clean_json(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None

def validate_data_integrity() -> Dict[str, Any]:
    return data_processor.get_data_statistics()



