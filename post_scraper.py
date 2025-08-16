# import os
# import sys
# import json
# import logging
# from job_scraper import filter_jobs_by_experience
# from config import DATA_DIR
# from scraper import scrape_all_keywords_parallel
# from eligibility import load_resume_text, analyze_posts_batch
# from utils import POST_KEYWORDS_FILE, load_keywords, save_jsonl
# from mailer import send_emails_batch
# from filter import filter_eligible_posts
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# os.makedirs(DATA_DIR, exist_ok=True)


# async def scrape_process_all_keywords(experience: int, total_posts: int):
#     keywords = load_keywords(POST_KEYWORDS_FILE)
#     posts_per_keyword = max(1, total_posts // len(keywords))

#     print(f"\n📥 Loaded {len(keywords)} keywords. Scraping {posts_per_keyword} posts per keyword with concurrency limit 3...\n")

#     # Parallel scrape with concurrency limit 3
#     all_posts = await scrape_all_keywords_parallel(keywords, posts_per_keyword, 2)
#     print(f"\n📊 Total valid scraped posts: {len(all_posts)} before filtering\n")


#     os.makedirs(DATA_DIR, exist_ok=True)
#     with open(f"{DATA_DIR}/all_linkedin_posts.jsonl", "w", encoding="utf-8") as f:
#         for post in all_posts:
#             f.write(json.dumps({"text": post}) + "\n")
            
            
#      # Convert scraped text to dict with "description" field so our filter works
#     raw_jobs = [{"description": post, "title": ""} for post in all_posts]
        
#     # Filter based on experience
#     filtered_jobs = filter_jobs_by_experience(raw_jobs, max_experience=experience)
#     print(f"✅ Jobs after experience filter: {len(filtered_jobs)}\n")
#     # Load resume
#     resume_text = load_resume_text()
    
#     print("🧠 Analyzing scraped posts using LLM...\n")
#     # Pass only the filtered job descriptions to analysis
#     processed_posts = await analyze_posts_batch(
#         [job["description"] for job in filtered_jobs],
#         experience
#     )

#     eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

#     save_jsonl(eligible, f"{DATA_DIR}/eligible_posts.jsonl")
#     save_jsonl(mail_list, f"{DATA_DIR}/mail_sent_posts.jsonl")
#     save_jsonl(apply_list, f"{DATA_DIR}/only_apply_links.jsonl")

#     send_emails_batch(mail_list, resume_text)
import os
import json
import logging

from job_scraper import filter_jobs_by_experience
from scraper import scrape_all_keywords_parallel
from eligibility import load_resume_text, analyze_posts_batch
from mailer import send_emails_batch
from filter import filter_eligible_posts

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 Old inline function
def load_keywords(file_path="keywordsforpost.txt") -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_jsonl(data_list, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

async def scrape_process_all_keywords(experience: int, total_posts: int):
    keywords = load_keywords("keywords.txt")   # direct txt file
    posts_per_keyword = max(1, total_posts // len(keywords))

    print(f"\n📥 Loaded {len(keywords)} keywords. Scraping {posts_per_keyword} posts per keyword with concurrency limit 3...\n")

    # Parallel scrape with concurrency limit 3
    all_posts = await scrape_all_keywords_parallel(keywords, posts_per_keyword, 2)
    print(f"\n📊 Total valid scraped posts: {len(all_posts)} before filtering\n")

    # Save raw posts
    os.makedirs("data", exist_ok=True)
    with open("data/all_linkedin_posts.jsonl", "w", encoding="utf-8") as f:
        for post in all_posts:
            f.write(json.dumps({"text": post}) + "\n")

    # Convert scraped text to dict with "description" field
    raw_jobs = [{"description": post, "title": ""} for post in all_posts]

    # Filter based on experience
    filtered_jobs = filter_jobs_by_experience(raw_jobs, max_experience=experience)
    print(f"✅ Jobs after experience filter: {len(filtered_jobs)}\n")

    # Load resume
    resume_text = load_resume_text()

    print("🧠 Analyzing scraped posts using LLM...\n")
    processed_posts = await analyze_posts_batch(
        [job["description"] for job in filtered_jobs],
        experience
    )

    # Split eligible/apply/mail
    eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

    # Save results
    save_jsonl(eligible, "data/eligible_posts.jsonl")
    save_jsonl(mail_list, "data/mail_sent_posts.jsonl")
    save_jsonl(apply_list, "data/only_apply_links.jsonl")

    # Send emails
    send_emails_batch(mail_list, resume_text)
