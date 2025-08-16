# main.py (Streamlit entrypoint)
import subprocess
import sys
import time
import socket
import os
import streamlit as st
import atexit

FASTAPI_PORT = 8001
fastapi_process = None  # store background process


def is_port_in_use(port: int) -> bool:
    """Check if given port is already being used."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_fastapi():
    """Start FastAPI only if it's not already running."""
    global fastapi_process
    if is_port_in_use(FASTAPI_PORT):
        print("✅ FastAPI already running")
        return

    CREATE_NO_WINDOW = 0x08000000  # Hide terminal in Windows
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", str(FASTAPI_PORT)],
        creationflags=CREATE_NO_WINDOW
    )
    print(f"🚀 FastAPI started in background (PID={fastapi_process.pid})")
    time.sleep(2)  # give server time to boot


def stop_fastapi():
    """Stop FastAPI if this app started it."""
    global fastapi_process
    if fastapi_process and fastapi_process.poll() is None:
        fastapi_process.terminate()
        print("🛑 FastAPI stopped")


# ✅ Ensure FastAPI runs only once (per Streamlit session)
if "fastapi_started" not in st.session_state:
    start_fastapi()
    st.session_state.fastapi_started = True
    # register cleanup
    atexit.register(stop_fastapi)

import os
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from urllib.parse import unquote

import requests
import pandas as pd
import streamlit as st

from config import config
from utils import DataProcessor
from selenium_urlfix import LinkedInLinkResolver

# =========================
# Config / Logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard")

SCRAPE_API_URL = os.getenv("SCRAPE_API_URL", "http://127.0.0.1:8001/scrape-linkedin")

st.set_page_config(
    page_title="LinkedIn Scraper Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Helpers - Jobs Viewer
# =========================
def convert_to_view_url(url: str) -> str:
    """Convert LinkedIn search URL (with currentJobId) to canonical /jobs/view/<id>/"""
    if not url or "/jobs/view/" in url:
        return url
    m = re.search(r"currentJobId=(\d+)", url)
    return f"https://www.linkedin.com/jobs/view/{m.group(1)}/" if m else url

def parse_time_ago(time_str: str):
    """Turn 'X hours ago' into datetime"""
    if not time_str:
        return None
    s = time_str.lower()
    now = datetime.now()
    try:
        if "just now" in s or "moment" in s:
            return now
        m = re.search(r"(\d+)\s*minute", s)
        if m:
            return now - timedelta(minutes=int(m.group(1)))
        h = re.search(r"(\d+)\s*hour", s)
        if h:
            return now - timedelta(hours=int(h.group(1)))
        d = re.search(r"(\d+)\s*day", s)
        if d:
            return now - timedelta(days=int(d.group(1)))
        w = re.search(r"(\d+)\s*week", s)
        if w:
            return now - timedelta(weeks=int(w.group(1)))
    except:
        return None
    return None

def get_time_category(time_str: str) -> str:
    dt = parse_time_ago(time_str)
    if not dt:
        return "older-job"
    age = datetime.now() - dt
    if age < timedelta(hours=24):
        return "recent-job"
    if age < timedelta(days=7):
        return "this-week-job"
    return "older-job"

def format_time_display(time_str: str) -> str:
    if not time_str:
        return "Unknown time"
    return time_str.replace("ago", "").strip() + " ago"

# @st.cache_data(show_spinner=False)
# def load_jobs_data(filtered_jobs_path: Path) -> List[Dict]:
#     """Load jobs, dedupe by URL, sort newest first"""
#     if not filtered_jobs_path.exists():
#         return []
#     try:
#         jobs = json.loads(filtered_jobs_path.read_text(encoding="utf-8"))
#         unique = {}
#         for j in jobs:
#             url = convert_to_view_url(j.get("job_url"))
#             if url and url not in unique:
#                 j["job_url"] = url
#                 jp = j.get("date_posted", "")
#                 j["formatted_time"] = format_time_display(jp)
#                 j["time_category"] = get_time_category(jp)
#                 unique[url] = j
#         return sorted(
#             unique.values(),
#             key=lambda x: parse_time_ago(x.get("date_posted", "")) or datetime.min,
#             reverse=True,
#         )
#     except Exception as e:
#         logger.exception("Error loading jobs")
#         st.error(f"Error loading jobs: {e}")
#         return []
@st.cache_data(show_spinner=False)
def load_jobs_data(filtered_jobs_path: Path) -> List[Dict]:
    """Load jobs, dedupe by URL, sort newest first"""
    if not filtered_jobs_path.exists():
        return []
    try:
        raw = filtered_jobs_path.read_text(encoding="utf-8").strip()
        if not raw:  # ✅ handle empty file
            logger.warning(f"⚠️ File is empty: {filtered_jobs_path}")
            return []
        jobs = json.loads(raw)  # safe JSON load

        # Deduplicate
        unique = {}
        for j in jobs:
            url = convert_to_view_url(j.get("job_url"))
            if url and url not in unique:
                j["job_url"] = url
                jp = j.get("date_posted", "")
                j["formatted_time"] = format_time_display(jp)
                j["time_category"] = get_time_category(jp)
                unique[url] = j
        return sorted(
            unique.values(),
            key=lambda x: parse_time_ago(x.get("date_posted", "")) or datetime.min,
            reverse=True,
        )
    except Exception as e:
        logger.exception("Error loading jobs")
        st.error(f"Error loading jobs: {e}")
        return []

def display_job_details(job: Dict) -> str:
    details = []
    if job.get("applicants"):
        details.append(f"👥 {job['applicants']}")
    if job.get("promoted"):
        details.append("⭐ Promoted by hirer")
    if job.get("response_info"):
        details.append(f"📩 {job['response_info']}")
    return " · ".join(details) if details else "No additional details"

def display_job_cards(jobs: List[Dict]):
    for job in jobs:
        color = (
            "#2ecc71" if job["time_category"] == "recent-job"
            else "#3498db" if job["time_category"] == "this-week-job"
            else "#95a5a6"
        )
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {color};
                padding: 1rem;
                margin: 0.8rem 0;
                background: #f8f9fa;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            ">
                <div style="font-weight:600; font-size:1.15rem; color:#0e5a8a;">
                    {job.get("title","No title")}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.9rem; margin-top:0.2rem;">
                    <span>{job.get("company","Unknown")}</span>
                    <span>⏱️ {job.get("formatted_time","Unknown")}</span>
                </div>
                <div style="color:#5f6b7a; margin:0.5rem 0;">📍 {job.get("location","Unknown")}</div>
                <div style="font-size:0.85rem; color:#738694;">{display_job_details(job)}</div>
                <a href="{job.get("job_url","#")}" target="_blank">
                    <button style="margin-top:0.5rem; background:#0e5a8a; color:white; border:none; padding:0.35rem 1rem; border-radius:0.3rem; cursor:pointer;">
                        🔍 View Job
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =========================
# Apply Links Viewer
# =========================
class DataLoader:
    def __init__(self):
        self.file_paths = config.get_file_paths()  # expects keys like: "apply_posts", "filtered_jobs", etc.
        self.data_processor = DataProcessor()

    def load_apply_links(self) -> List[Dict]:
        """Read JSONL posts and extract any apply links"""
        try:
            data = self.data_processor.file_manager.load_jsonl_safe(self.file_paths["apply_posts"])
            valid = []
            for item in data:
                raw = item.get("Apply_Link") or item.get("link") or item.get("url") or item.get("apply_link")
                if raw and raw != "Not Provided":
                    valid.append(
                        {
                            "original_link": raw,
                            "role": item.get("Role", "Unknown"),
                            "company": item.get("Company", "Unknown"),
                            "eligibility": item.get("Eligibility", "Unknown"),
                            "post_index": item.get("Post_Index", 0),
                        }
                    )
            return valid
        except Exception as e:
            logger.exception("Error loading apply links")
            st.error(f"Error loading apply links: {e}")
            return []

@st.cache_data(show_spinner=False)
def check_link_validity(url: str, timeout: int = 6) -> bool:
    try:
        r = requests.get(url, allow_redirects=True, timeout=timeout)
        return r.status_code in (200, 301, 302, 405)
    except Exception:
        return False

def show_apply_links(data_loader: DataLoader):
    st.header("Apply Links Viewer")

    # Button to load links
    if st.button("📥 Load Apply Links", key="load_apply_links"):
        links_data = data_loader.load_apply_links()

        if not links_data:
            st.warning("No apply links found. Run the main application first to generate data.")
            return

        st.success(f"Found {len(links_data)} apply links")
        resolver = LinkedInLinkResolver()

        progress_bar = st.progress(0, text="Processing links...")
        total = len(links_data)

        for idx, item in enumerate(links_data, start=1):
            with st.expander(f"{item['role']} at {item['company']}", expanded=False):
                st.write(f"**Eligibility:** {item['eligibility']}")

                raw_links = item['original_link']

                # Normalize and deduplicate
                if isinstance(raw_links, str):
                    links = list(set([unquote(link.strip()) for link in raw_links.replace('\n', ',').split(',') if link.strip()]))
                elif isinstance(raw_links, list):
                    links = list(set([unquote(link.strip()) for link in raw_links if isinstance(link, str) and link.strip()]))
                else:
                    links = []

                valid_links = []
                for link in links:
                    if link.startswith("http") and check_link_validity(link):
                        valid_links.append(link)

                if not valid_links:
                    st.warning("⚠️ No valid links found for this post.")
                else:
                    st.markdown("**Apply Link(s):**")
                    for link in valid_links:
                        resolved_link = resolver.resolve_url(link)
                        st.markdown(f"- [🔗 {resolved_link}]({resolved_link})", unsafe_allow_html=True)

            # Update progress bar
            progress = idx / total
            progress_bar.progress(progress, text=f"{int(progress * 100)}% processed")

        progress_bar.empty()
        st.success("✅ All apply links processed.")
    else:
        st.info("Click the **Load Apply Links** button to view data.")


# =========================
# Analytics & System Status
# =========================
def show_analytics(dp: DataProcessor):
    try:
        stats = dp.get_data_statistics()
        st.subheader("📊 Overview")
        metrics = stats.get("summary", {})
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Posts", metrics.get("total_posts", 0))
        c2.metric("Eligible Posts", metrics.get("eligible_posts", 0))
        c3.metric("Email Contacts", metrics.get("posts_with_emails", 0))
        c4.metric("Apply Links", metrics.get("posts_with_apply_links", 0))
        c5.metric("Emails Sent", metrics.get("emails_sent", 0))

        st.subheader("📁 Data Files")
        files = stats.get("files", {})
        table = []
        for k, info in files.items():
            table.append(
                {
                    "File": k.replace("_", " ").title(),
                    "Records": info.get("count", 0),
                    "Size (KB)": round((info.get("file_size", 0) or 0) / 1024, 2),
                    "Status": "✅ Available" if info.get("file_exists") else "❌ Missing",
                }
            )
        if table:
            st.dataframe(pd.DataFrame(table), use_container_width=True)
    except Exception as e:
        logger.exception("Analytics failed")
        st.error(f"Error loading analytics: {e}")

def get_dir_size_kb(directory: str) -> float:
    if not os.path.exists(directory):
        return 0.0
    total = 0
    for f in os.listdir(directory):
        p = os.path.join(directory, f)
        if os.path.isfile(p):
            total += os.path.getsize(p)
    return total / 1024

def show_system_status():
    st.subheader("💻 System Information")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Configuration Status:**")
        checks = [
            ("Resume File", os.path.exists(config.resume_path)),
            ("LinkedIn Cookie", bool(config.linkedin_cookie)),
            ("Email Accounts", len(config.email_accounts) > 0),
            ("Azure OpenAI", bool(getattr(config.ai, "api_key", None))),
            ("Data Directory", os.path.exists(config.data_dir)),
            ("Logs Directory", os.path.exists(config.logs_dir)),
        ]
        for name, status in checks:
            st.write(("✅" if status else "❌") + f" {name}")
    with c2:
        st.write("**File System:**")
        try:
            st.write(f"📁 Data Directory: {get_dir_size_kb(config.data_dir):.1f} KB")
            st.write(f"📋 Logs Directory: {get_dir_size_kb(config.logs_dir):.1f} KB")
        except Exception as e:
            st.write(f"❌ Error checking directories: {e}")

# =========================
# Main
# =========================
def main():
    st.title("💼 LinkedIn Jobs Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%b %d, %Y %I:%M %p')}")

    # Init helpers
    dp = DataProcessor()
    loader = DataLoader()
    file_paths = config.get_file_paths()
    filtered_jobs_path = Path(file_paths.get("filtered_jobs", "data/filtered_jobs.json"))

    # Sidebar: Scraping Controls + Stats
    with st.sidebar:
        st.header("⚙️ Scraping Controls")
        exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=2, step=1)
        total_posts = st.number_input("Total Posts", min_value=1, max_value=500, value=25, step=1)
        mode = st.selectbox("Scrape Mode", ["jobsData", "postData"])
        if st.button("🚀 Start Scraping", use_container_width=True):
            payload = {"experience": exp, "total_posts": int(total_posts), "mode": mode}
            try:
                with st.spinner("Scraping in progress..."):
                    res = requests.post(SCRAPE_API_URL, json=payload, timeout=180)
                if res.status_code == 200:
                    st.session_state["last_scrape_result"] = res.json()
                    st.success("✅ Scraping triggered/completed.")
                else:
                    st.error(f"❌ Scrape failed (HTTP {res.status_code})")
            except Exception as e:
                st.error(f"Error: {e}")
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Clear all cached data functions
            st.cache_data.clear()
            # Force rerun the whole app
            st.rerun()

        st.markdown("---")
        st.subheader("📈 Quick Stats")
        try:
            stats = dp.get_data_statistics()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Posts", stats["summary"]["total_posts"])
                st.metric("Eligible", stats["summary"]["eligible_posts"])
            with col2:
                st.metric("Emails", stats["summary"]["posts_with_emails"])
                st.metric("Apply Links", stats["summary"]["posts_with_apply_links"])
            if "last_scrape_result" in st.session_state:
                with st.expander("Last Scrape Result"):
                    st.json(st.session_state["last_scrape_result"])
        except Exception as e:
            st.info("Run scraper once to populate stats.")
            logger.debug(e)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💼 Jobs Data", "🔗 Apply Links", "📊 Analytics", "🧰 System Status"])

    with tab1:
        jobs = load_jobs_data(filtered_jobs_path)
        if jobs:
            recent = [j for j in jobs if j["time_category"] == "recent-job"]
            week = [j for j in jobs if j["time_category"] == "this-week-job"]
            older = [j for j in jobs if j["time_category"] == "older-job"]

            if recent:
                st.markdown(f"### 🆕 Last 24 Hours ({len(recent)})")
                display_job_cards(recent)
            if week:
                st.markdown(f"### 🗓 This Week ({len(week)})")
                display_job_cards(week)
            if older:
                st.markdown(f"### 📅 Older ({len(older)})")
                display_job_cards(older)
        else:
            st.info("No jobs found. Click **Start Scraping** to generate data.")

    with tab2:
        show_apply_links(loader)

    with tab3:
        show_analytics(dp)

    with tab4:
        show_system_status()


if __name__ == "__main__":
    main()
