# import os
# import time
# import asyncio

# from config import DATA_DIR
# from scraper import collect_linkedin_posts
# from eligibility import load_resume_text, analyze_posts_batch
# from utils import save_jsonl, save_csv
# from mailer import send_emails_batch
# from filter import filter_eligible_posts

# os.makedirs(DATA_DIR, exist_ok=True)

# if __name__ == "__main__":
#     role_input = input("🔍 Enter job role: ").strip()
#     years_of_exp = int(input("🧠 Enter your years of experience (e.g., 2): ").strip())
#     total_posts = int(input("📦 Total posts to scrape: ").strip())
    
    
#     encoded_query = role_input.replace(" ", "%20")
#     # search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&origin=SWITCH_SEARCH_VERTICAL"
#     search_url = f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={encoded_query}&origin=FACETED_SEARCH&sid=WQq"
#     # Step 1: Scrape LinkedIn posts
#     all_posts = asyncio.run(collect_linkedin_posts(search_url, total_posts))
#     print(f"✅ Scraped {len(all_posts)} unique posts.\n")

#     # Step 2: Load resume
#     resume_text = load_resume_text()

#     # Step 3: Use LLM to extract structure + eligibility in 1 shot
#     print("🧠 Analyzing scraped posts using LLM...\n")
#     processed_posts = analyze_posts_batch(all_posts, resume_text, years_of_exp)

#     # Step 4: Filter eligible posts with valid email/apply links
#     eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

#     # Step 5: Save filtered posts
#     save_jsonl(eligible, f"{DATA_DIR}/eligible_posts.jsonl")
#     save_jsonl(mail_list, f"{DATA_DIR}/mail_sent_posts.jsonl")
#     save_jsonl(apply_list, f"{DATA_DIR}/only_apply_links.jsonl")
#     save_csv(apply_list, os.path.join(DATA_DIR, "apply_links.csv"))

#     # Step 6: Send emails
#     send_emails_batch(mail_list, resume_text)
# import os
# import time
# import asyncio

# from config import DATA_DIR
# from scraper import collect_linkedin_posts
# from eligibility import load_resume_text, analyze_posts_batch
# from utils import save_jsonl, save_csv
# from mailer import send_emails_batch
# from filter import filter_eligible_posts

# os.makedirs(DATA_DIR, exist_ok=True)


# def load_keywords(file_path="keywords.txt") -> list[str]:
#     with open(file_path, "r", encoding="utf-8") as f:
#         return [line.strip() for line in f if line.strip()]


# async def scrape_process_all_keywords(experience: int, total_posts: int):
#     keywords = load_keywords()
#     posts_per_keyword = total_posts // len(keywords)
#     all_posts = []

#     print(f"\n📥 Loaded {len(keywords)} keywords. Scraping {posts_per_keyword} posts per keyword...\n")

#     for keyword in keywords:
#         print(f"🔍 Scraping keyword: {keyword}")
#         encoded_query = keyword.replace(" ", "%20")
#         search_url = f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={encoded_query}&origin=FACETED_SEARCH"
        
#         posts = await collect_linkedin_posts(search_url, posts_per_keyword)

#         valid_posts = 0
#         for post in posts:
#             all_posts.append(post)
#             valid_posts += 1

#         print(f"✅ Scraped {valid_posts} valid posts for '{keyword}'\n")

#     print(f"\n📊 Total valid scraped posts: {len(all_posts)}\n")

#     # Step 2: Load resume
#     resume_text = load_resume_text()

#     # Step 3: Analyze posts with LLM
#     print("🧠 Analyzing scraped posts using LLM...\n")
#     processed_posts = analyze_posts_batch(all_posts, resume_text, experience)

#     # Step 4: Filter eligible posts
#     eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

#     # Step 5: Save results
#     save_jsonl(eligible, f"{DATA_DIR}/eligible_posts.jsonl")
#     save_jsonl(mail_list, f"{DATA_DIR}/mail_sent_posts.jsonl")
#     save_jsonl(apply_list, f"{DATA_DIR}/only_apply_links.jsonl")
#     save_csv(apply_list, os.path.join(DATA_DIR, "apply_links.csv"))

#     # Step 6: Send emails
#     send_emails_batch(mail_list, resume_text)


# if __name__ == "__main__":
#     years_of_exp = int(input("🧠 Enter your years of experience (e.g., 2): ").strip())
#     total_posts = int(input("📦 Total posts to scrape: ").strip())
#     asyncio.run(scrape_process_all_keywords(years_of_exp, total_posts))

import os
import time
import asyncio
import json
from config import DATA_DIR
from scraper import collect_linkedin_posts
from eligibility import load_resume_text, analyze_posts_batch
from utils import save_jsonl, save_csv
from mailer import send_emails_batch
from filter import filter_eligible_posts

os.makedirs(DATA_DIR, exist_ok=True)


def load_keywords(file_path="keywords.txt") -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


async def scrape_process_all_keywords(experience: int, total_posts: int):
    keywords = load_keywords()
    posts_per_keyword = total_posts // len(keywords)
    all_posts = []

    print(f"\n📥 Loaded {len(keywords)} keywords. Scraping {posts_per_keyword} posts per keyword...\n")

    for keyword in keywords:
        print(f"🔍 Scraping keyword: {keyword}")
        encoded_query = keyword.replace(" ", "%20")
        search_url = f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={encoded_query}&origin=FACETED_SEARCH"

        posts = await collect_linkedin_posts(search_url, posts_per_keyword)
        valid_posts = 0
        for post in posts:
            all_posts.append(post)
            valid_posts += 1

        print(f"✅ Scraped {valid_posts} valid posts for '{keyword}'\n")

    print(f"\n📊 Total valid scraped posts: {len(all_posts)}\n")

    # Step 2: Load resume
    resume_text = load_resume_text()

    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/all_linkedin_posts.jsonl", "w", encoding="utf-8") as f:
        for post in all_posts:
            f.write(json.dumps({"text": post}) + "\n")
            
    # Step 3: Analyze posts with LLM
    print("🧠 Analyzing scraped posts using LLM...\n")
    processed_posts = analyze_posts_batch(all_posts, resume_text, experience)

    # Step 4: Filter eligible posts
    eligible, mail_list, apply_list = filter_eligible_posts(processed_posts)

    # Step 5: Save results
    save_jsonl(eligible, f"{DATA_DIR}/eligible_posts.jsonl")
    save_jsonl(mail_list, f"{DATA_DIR}/mail_sent_posts.jsonl")
    save_jsonl(apply_list, f"{DATA_DIR}/only_apply_links.jsonl")
    save_csv(apply_list, os.path.join(DATA_DIR, "apply_links.csv"))

    # Step 6: Send emails
    send_emails_batch(mail_list, resume_text)


if __name__ == "__main__":
    years_of_exp = int(input("🧠 Enter your years of experience (e.g., 2): ").strip())
    total_posts = int(input("📦 Total posts to scrape: ").strip())
    asyncio.run(scrape_process_all_keywords(years_of_exp, total_posts))
