import os
import json
import logging
from scraper import scrape_all_keywords_parallel
from job_scraper import filter_jobs_by_experience
from eligibility import load_resume_text, analyze_posts_batch
from mailer import send_emails_batch
from filter import filter_eligible_posts
from progress import init_task, tasks


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_keywords(file_path="keywordsforpost.txt") -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_jsonl(data_list, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

async def scrape_process_all_keywords(experience: int, total_posts: int, keywords: list[str], task_id=None):
    posts_per_keyword = max(1, total_posts // len(keywords))
    if task_id:
        init_task(task_id, total_posts=total_posts)
        tasks[task_id]["status"] = "Scraping started..."

    all_posts = await scrape_all_keywords_parallel(keywords, posts_per_keyword, 2, task_id=task_id)

    print(f"\n📊 Total valid scraped posts: {len(all_posts)} before filtering\n")

    if task_id:
        tasks[task_id]["progress"] = 20
        tasks[task_id]["status"] = "Scraping done, filtering..."

    os.makedirs("data", exist_ok=True)
    with open("data/all_linkedin_posts.jsonl", "w", encoding="utf-8") as f:
        for post in all_posts:
            f.write(json.dumps({"text": post}) + "\n")

    raw_jobs = [{"description": post, "title": ""} for post in all_posts]

    filtered_jobs = filter_jobs_by_experience(raw_jobs, max_experience=experience)
    print(f"✅ Jobs after experience filter: {len(filtered_jobs)}\n")

    resume_text = load_resume_text()

    print("🧠 Analyzing scraped posts using LLM...\n")
    processed_posts = await analyze_posts_batch(
        [job["description"] for job in filtered_jobs],
        experience,
        task_id=task_id
    )

    eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

    save_jsonl(eligible, "data/eligible_posts.jsonl")
    save_jsonl(mail_list, "data/mail_sent_posts.jsonl")
    save_jsonl(apply_list, "data/only_apply_links.jsonl")

    if task_id:
        tasks[task_id]["progress"] = 80
        tasks[task_id]["status"] = "Mailing started..."

    result = send_emails_batch(mail_list, resume_text, task_id=task_id)

    if task_id:
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "Pipeline completed ✅"
        tasks[task_id]["result"] = result   # ✅ Save stats for API response