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
from prompt import email_prompt_template
from tqdm import tqdm

# # 🔐 Email senders
# SENDER_EMAILS = [
#     {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
#     {"email": os.getenv("EMAIL_ID_2"), "password": os.getenv("EMAIL_PASS_2")},
#     {"email": os.getenv("EMAIL_ID_3"), "password": os.getenv("EMAIL_PASS_3")},
# ]
SENDER_EMAILS = [
    {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
]

RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")
EMAIL_LOG_FILE = "data/email_log.csv"
MAX_EMAILS_PER_SENDER = 70  # Daily limit per sender

# 🧠 Generate personalized email content
def generate_email(post_text, resume_text):
    prompt = email_prompt_template(post_text=post_text, resume_text=resume_text)
    return llm.invoke(prompt).content.strip()

# 📜 Load email log to avoid duplicates
def load_sent_emails():
    if not os.path.exists(EMAIL_LOG_FILE):
        return set()
    with open(EMAIL_LOG_FILE, "r", encoding="utf-8") as f:
        return set(email.strip().lower() for row in csv.reader(f) for email in row if "@" in email)

# ✉️ Send one email
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

def email_worker(sender, posts, resume_text, results):
    sent = 0
    skipped = 0
    sent_emails = load_sent_emails()

    bar = tqdm(posts, desc=f"📨 {sender['email'][:25]} Sending", ncols=80)

    for post in bar:
        email = post.get("Contact_Email", "").strip().lower()
        if not email or email in sent_emails or "@" not in email:
            skipped += 1
            bar.set_postfix(sent=sent, skipped=skipped)
            continue

        subject = f"Application for {post.get('Role', 'Developer')}"
        post_text = post.get("Job_Description", "")

        try:
            body = generate_email(post_text, resume_text)
            send_email(email, subject, body, sender)
            sent += 1
            bar.set_postfix(sent=sent, skipped=skipped)
            delay = random.uniform(10, 20)
            time.sleep(delay)
        except Exception as e:
            print(f"\n❌ Error sending to {email}: {e}")

        if sent >= MAX_EMAILS_PER_SENDER:
            print(f"\n⛔ {sender['email']} reached max daily quota.")
            break

    results[sender["email"]] = {"sent": sent, "skipped": skipped}

# # 🔄 Worker to send emails from one sender
# def email_worker(sender, posts, resume_text, results):
#     sent = 0
#     skipped = 0
#     sent_emails = load_sent_emails()

#     for post in posts:
#         email = post.get("Contact_Email", "").strip().lower()
#         if not email or email in sent_emails or "@" not in email:
#             skipped += 1
#             continue

#         subject = f"Application for {post.get('Role', 'Developer')}"
#         post_text = post.get("Job_Description", "")

#         try:
#             body = generate_email(post_text, resume_text)
#             send_email(email, subject, body, sender)
#             print(f"✅ Sent to {email} via {sender['email']}")
#             sent += 1
#             delay = random.uniform(10, 20)
#             time.sleep(delay)
#         except Exception as e:
#             print(f"❌ Error sending to {email}: {e}")

#         if sent >= MAX_EMAILS_PER_SENDER:
#             print(f"⛔ {sender['email']} reached max daily quota.")
#             break

#     results[sender["email"]] = {"sent": sent, "skipped": skipped}

# 📤 Main function to pre-split and send
def send_emails_batch(post_list, resume_text):
    total_posts = len(post_list)
    num_senders = len(SENDER_EMAILS)
    chunk_size = (total_posts + num_senders - 1) // num_senders
    threads = []
    results = {}

    print(f"\n📨 Sending up to {total_posts} emails using {num_senders} parallel workers...\n")

    for i, sender in enumerate(SENDER_EMAILS):
        chunk = post_list[i * chunk_size:(i + 1) * chunk_size]
        thread = threading.Thread(target=email_worker, args=(sender, chunk, resume_text, results))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    total_sent = sum(r["sent"] for r in results.values())
    total_skipped = sum(r["skipped"] for r in results.values())

    print(f"\n📊 Summary:")
    print(f"   Total Attempted: {total_posts}")
    print(f"   Sent: {total_sent}")
    print(f"   Skipped: {total_skipped}")
    print(f"   Per Sender Usage: {results}")



# import os
# import smtplib
# import csv
# import re
# import time
# import random
# from datetime import datetime
# from email.message import EmailMessage
# from azure_llm import llm
# from prompt import email_prompt_template

# # 🔐 Gmail sender accounts (rotate)
# SENDER_EMAILS = [
#     {"email": os.getenv("EMAIL_ID_1"), "password": os.getenv("EMAIL_PASS_1")},
#     {"email": os.getenv("EMAIL_ID_2"), "password": os.getenv("EMAIL_PASS_2")},
#     {"email": os.getenv("EMAIL_ID_3"), "password": os.getenv("EMAIL_PASS_3")},
# ]

# RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")
# EMAIL_LOG_FILE = "data/email_log.csv"
# MAX_EMAILS_PER_SENDER = 70
# EMAILS_PER_ROTATION = 2

# # 🧠 Generate personalized email from post text + resume
# def generate_email(post_text, resume_text):
#     prompt = email_prompt_template(post_text=post_text, resume_text=resume_text)
#     return llm.invoke(prompt).content.strip()

# # 📜 Already sent email addresses
# def load_sent_emails(log_path=EMAIL_LOG_FILE):
#     if not os.path.exists(log_path):
#         return set()
#     with open(log_path, "r", encoding="utf-8") as f:
#         return set(
#             email.strip().lower()
#             for row in csv.reader(f)
#             for email in row
#             if "@" in email
#         )

# # ✉️ Send one email with resume
# def send_email(to_email, subject, body, sender):
#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = sender["email"]
#     msg["To"] = to_email

#     # Remove subject line if included in body
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

# # 📤 Batch email sender with sender rotation
# def send_emails_batch(post_list, resume_text):
#     limit = 200
#     batch_size = 6
#     sent_emails = load_sent_emails()
#     sender_usage = {s["email"]: 0 for s in SENDER_EMAILS}
#     sender_index = 0
#     sender_use_count = 0
#     sent_count = 0
#     skipped_count = 0
#     total_eligible = 0

#     print(f"\n📨 Sending up to {limit} emails using rotating senders...\n")

#     for idx, post in enumerate(post_list):
#         if sent_count >= limit:
#             break

#         email = post.get("Contact_Email", "").strip().lower()
#         if not email or email in sent_emails or "@" not in email:
#             skipped_count += 1
#             continue

#         total_eligible += 1
#         post_text = post.get("Job_Description", "")
#         subject = f"Application for {post.get('Role', 'Developer')}"

#         # Rotate after EMAILS_PER_ROTATION
#         if sender_use_count >= EMAILS_PER_ROTATION:
#             sender_index = (sender_index + 1) % len(SENDER_EMAILS)
#             sender_use_count = 0

#         # Skip senders who hit quota
#         attempts = 0
#         while sender_usage[SENDER_EMAILS[sender_index]["email"]] >= MAX_EMAILS_PER_SENDER and attempts < len(SENDER_EMAILS):
#             sender_index = (sender_index + 1) % len(SENDER_EMAILS)
#             attempts += 1

#         if attempts == len(SENDER_EMAILS):
#             print("🚫 All sender accounts have reached their daily quota.")
#             break

#         sender = SENDER_EMAILS[sender_index]

#         try:
#             body = generate_email(post_text, resume_text)
#             send_email(email, subject, body, sender)
#             print(f"✅ Sent to {email} via {sender['email']}")
#             sent_count += 1
#             sender_use_count += 1
#             sender_usage[sender["email"]] += 1

#             # Short delay between sends
#             delay = random.uniform(10, 30)
#             print(f"🕒 Waiting {delay:.1f}s...\n")
#             time.sleep(delay)

#         except Exception as e:
#             print(f"❌ Error sending to {email}: {e}")

#         # Longer delay between batches
#         if sent_count % batch_size == 0 and sent_count > 0:
#             batch_wait = random.randint(60, 120)
#             print(f"⏳ Batch done. Sleeping for {batch_wait}s...\n")
#             time.sleep(batch_wait)

#     print(f"\n📊 Summary:")
#     print(f"   Total Posts: {len(post_list)}")
#     print(f"   Eligible: {total_eligible}")
#     print(f"   Sent: {sent_count}")
#     print(f"   Skipped: {skipped_count}")
#     print(f"   Per Sender Usage: {sender_usage}")
