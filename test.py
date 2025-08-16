# test_keywords.py
import os
from utils import JOB_KEYWORDS_FILE, POST_KEYWORDS_FILE, load_keywords

print("\n=== 🔍 Testing Keyword Files ===\n")

# --- Test Job Keywords ---
print(f"📂 JOB_KEYWORDS_FILE → {JOB_KEYWORDS_FILE}")
try:
    job_keywords = load_keywords(JOB_KEYWORDS_FILE)
    print(f"✅ Loaded {len(job_keywords)} job keywords:")
    for kw in job_keywords:
        print("   -", kw)
except Exception as e:
    print(f"❌ Error loading job keywords: {e}")

print("\n" + "-"*50 + "\n")

# --- Test Post Keywords ---
print(f"📂 POST_KEYWORDS_FILE → {POST_KEYWORDS_FILE}")
try:
    post_keywords = load_keywords(POST_KEYWORDS_FILE)
    print(f"✅ Loaded {len(post_keywords)} post keywords:")
    for kw in post_keywords:
        print("   -", kw)
except Exception as e:
    print(f"❌ Error loading post keywords: {e}")
