
# import os
# import smtplib
# import csv
# import re
# import time
# import random
# import threading
# from datetime import datetime
# from email.message import EmailMessage
# from azure_llm import llm
# from prompt import email_prompt_template, resume_summary_prompt_template
# from tqdm import tqdm
# from config import config 
# # # 🔐 Email senders
# SENDER_EMAILS = [
#     {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
#     {"email": os.getenv("EMAIL_ID_2"), "password": os.getenv("EMAIL_PASS_2")},
#     {"email": os.getenv("EMAIL_ID_3"), "password": os.getenv("EMAIL_PASS_3")},
# ]
# # SENDER_EMAILS = [
# #     {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
# # ]

# RESUME_PATH = os.path.join("data", "resume.pdf")
# EMAIL_LOG_FILE = "data/email_log.csv"
# MAX_EMAILS_PER_SENDER = 70  # Daily limit per sender

# # 🧠 Generate structured resume summary via LLM
# def generate_resume_summary(resume_text):
#     prompt = resume_summary_prompt_template(resume_text)
#     return llm.invoke(prompt).content.strip()

# # 🧠 Generate personalized email content using summary
# def generate_email(post_text, resume_summary):
#     prompt = email_prompt_template(post_text=post_text,resume_summary_json=resume_summary)
#     return llm.invoke(prompt).content.strip()

# # 📜 Load email log to avoid duplicates
# def load_sent_emails():
#     if not os.path.exists(EMAIL_LOG_FILE):
#         return set()
#     with open(EMAIL_LOG_FILE, "r", encoding="utf-8") as f:
#         return set(email.strip().lower() for row in csv.reader(f) for email in row if "@" in email)

# # ✉️ Send one email
# def send_email(to_email, subject, body, sender):
#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = sender["email"]
#     msg["To"] = to_email

#     body = re.sub(r"\*\*Subject:\*\*.*\n?", "", body, flags=re.IGNORECASE)
#     msg.set_content(body)

     
#     with open(RESUME_PATH, "rb") as f:
#         msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="Resume.pdf")

#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#         smtp.login(sender["email"], sender["password"])
#         smtp.send_message(msg)

#     with open(EMAIL_LOG_FILE, "a", encoding="utf-8", newline="") as log:
#         writer = csv.writer(log)
#         writer.writerow([to_email.lower(), datetime.now().isoformat()])

# # 🧵 Worker to send emails per sender
# def email_worker(sender, posts, resume_summary, results):
#     sent = 0
#     skipped = 0
#     sent_emails = load_sent_emails()

#     bar = tqdm(posts, desc=f"📨 {sender['email'][:25]} Sending", ncols=80)

#     for post in bar:
#         email = post.get("Contact_Email", "").strip().lower()
#         if not email or email in sent_emails or "@" not in email:
#             skipped += 1
#             bar.set_postfix(sent=sent, skipped=skipped)
#             continue

#         subject = f"Application for {post.get('Role', 'Developer')}"
#         post_text = post.get("Job_Description", "")

#         try:
#             body = generate_email(post_text, resume_summary)
#             send_email(email, subject, body, sender)
#             sent += 1
#             bar.set_postfix(sent=sent, skipped=skipped)
#             delay = random.uniform(10, 20)
#             time.sleep(delay)
#         except Exception as e:
#             print(f"\n❌ Error sending to {email}: {e}")

#         if sent >= MAX_EMAILS_PER_SENDER:
#             print(f"\n⛔ {sender['email']} reached max daily quota.")
#             break

#     results[sender["email"]] = {"sent": sent, "skipped": skipped}

# # 📨 Main email batch dispatcher
# def send_emails_batch(post_list, resume_text):
#     print("\n📄 Generating structured resume summary using LLM...")
#     resume_summary = generate_resume_summary(resume_text)
#     total_posts = len(post_list)
#     num_senders = len(SENDER_EMAILS)
#     chunk_size = (total_posts + num_senders - 1) // num_senders
#     threads = []
#     results = {}

#     print(f"\n📨 Sending up to {total_posts} emails using {num_senders} parallel workers...\n")

#     for i, sender in enumerate(SENDER_EMAILS):
#         chunk = post_list[i * chunk_size:(i + 1) * chunk_size]
#         thread = threading.Thread(target=email_worker, args=(sender, chunk, resume_summary, results))
#         thread.start()
#         threads.append(thread)

#     for t in threads:
#         t.join()

#     total_sent = sum(r["sent"] for r in results.values())
#     total_skipped = sum(r["skipped"] for r in results.values())

#     print(f"\n📊 Summary:")
#     print(f"   Total Attempted: {total_posts}")
#     print(f"   Sent: {total_sent}")
#     print(f"   Skipped: {total_skipped}")
#     print(f"   Per Sender Usage: {results}")

import os
import smtplib
import csv
import re
import time
import random
import threading
from datetime import datetime
from email.message import EmailMessage
from azure_llm import llm
from prompt import email_prompt_template, resume_summary_prompt_template
from progress import tasks


SENDER_EMAILS = [
    {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
    {"email": os.getenv("EMAIL_ID_2"), "password": os.getenv("EMAIL_PASS_2")},
    {"email": os.getenv("EMAIL_ID_3"), "password": os.getenv("EMAIL_PASS_3")},
]

RESUME_PATH = os.path.join("data", "resume.pdf")
EMAIL_LOG_FILE = "data/email_log.csv"
MAX_EMAILS_PER_SENDER = 70

def generate_resume_summary(resume_text):
    prompt = resume_summary_prompt_template(resume_text)
    return llm.invoke(prompt).content.strip()

def generate_email(post_text, resume_summary):
    prompt = email_prompt_template(post_text=post_text,resume_summary_json=resume_summary)
    return llm.invoke(prompt).content.strip()

def load_sent_emails():
    if not os.path.exists(EMAIL_LOG_FILE):
        return set()
    with open(EMAIL_LOG_FILE, "r", encoding="utf-8") as f:
        return set(email.strip().lower() for row in csv.reader(f) for email in row if "@" in email)

def send_email(to_email, subject, body, sender):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender["email"]
    msg["To"] = to_email
    body = re.sub(r"\*\*Subject:\*\*.*\n?", "", body, flags=re.IGNORECASE)
    msg.set_content(body)
    with open(RESUME_PATH, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="Resume.pdf")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender["email"], sender["password"])
        smtp.send_message(msg)
    with open(EMAIL_LOG_FILE, "a", encoding="utf-8", newline="") as log:
        writer = csv.writer(log)
        writer.writerow([to_email.lower(), datetime.now().isoformat()])

def email_worker(sender, posts, resume_summary, results, task_id=None, total_tasks=1):
    sent = 0
    skipped = 0
    sent_emails = load_sent_emails()
    total = len(posts)

    for idx, post in enumerate(posts, start=1):
        email = post.get("Contact_Email", "").strip().lower()
        if not email or email in sent_emails or "@" not in email:
            skipped += 1
            continue

        subject = f"Application for {post.get('Role', 'Developer')}"
        post_text = post.get("Job_Description", "")

        try:
            body = generate_email(post_text, resume_summary)
            send_email(email, subject, body, sender)
            sent += 1
        except Exception as e:
            print(f"\n❌ Error sending to {email}: {e}")

        if task_id:
            percent = int((idx / total) * 100)
            tasks[task_id]["progress"] = 80 + int(20 * (percent / 100))
            tasks[task_id]["status"] = f"Mailing {percent}%"

        if sent >= MAX_EMAILS_PER_SENDER:
            break

    results[sender["email"]] = {"sent": sent, "skipped": skipped}

def send_emails_batch(post_list, resume_text, task_id=None):
    resume_summary = generate_resume_summary(resume_text)
    total_posts = len(post_list)
    num_senders = len(SENDER_EMAILS)
    chunk_size = (total_posts + num_senders - 1) // num_senders
    threads = []
    results = {}

    for i, sender in enumerate(SENDER_EMAILS):
        chunk = post_list[i * chunk_size:(i + 1) * chunk_size]
        thread = threading.Thread(target=email_worker, args=(sender, chunk, resume_summary, results, task_id, total_posts))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    return results
