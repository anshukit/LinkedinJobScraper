import streamlit as st
import pandas as pd
import logging
import os
from datetime import datetime
from typing import List, Dict
from config import config
from utils import validate_data_integrity, DataProcessor
from urllib.parse import unquote
import requests
from app import LinkedInLinkResolver
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="LinkedIn Job Application Dashboard",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DataLoader:
    def __init__(self):
        self.file_paths = config.get_file_paths()
        self.data_processor = DataProcessor()

    def load_apply_links(self) -> List[Dict]:
        try:
            data = self.data_processor.file_manager.load_jsonl_safe(self.file_paths["apply_posts"])
            valid_links = [
                {
                    'original_link': item.get('Apply_Link') or item.get('link') or item.get('url') or item.get('apply_link'),
                    'role': item.get('Role', 'Unknown'),
                    'company': item.get('Company', 'Unknown'),
                    'eligibility': item.get('Eligibility', 'Unknown'),
                    'post_index': item.get('Post_Index', 0)
                }
                for item in data
                if (item.get('Apply_Link') or item.get('link') or item.get('url') or item.get('apply_link')) not in [None, "Not Provided"]
            ]
            return valid_links
        except Exception as e:
            logger.error(f"Error loading apply links: {e}")
            return []

    def get_data_stats(self) -> Dict:
        return self.data_processor.get_data_statistics()


@st.cache_data(show_spinner=False)
def check_link_validity(url: str, timeout: int = 5) -> bool:
    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        return response.status_code in [200, 301, 302, 405]
    except Exception:
        return False
def show_apply_links(data_loader: DataLoader):
    st.header("Apply Links Viewer")
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

    progress_bar.empty()  # Remove the bar after completion
    st.success("✅ All apply links processed.")

# def show_apply_links(data_loader: DataLoader):
#     st.header("Apply Links Viewer")
#     links_data = data_loader.load_apply_links()

#     if not links_data:
#         st.warning("No apply links found. Run the main application first to generate data.")
#         return

#     st.success(f"Found {len(links_data)} apply links")
#     resolver = LinkedInLinkResolver()
#     for item in links_data:
#         with st.expander(f"{item['role']} at {item['company']}", expanded=False):
#             st.write(f"**Eligibility:** {item['eligibility']}")

#             raw_links = item['original_link']

#             # Normalize and deduplicate
#             if isinstance(raw_links, str):
#                 links = list(set([unquote(link.strip()) for link in raw_links.replace('\n', ',').split(',') if link.strip()]))
#             elif isinstance(raw_links, list):
#                 links = list(set([unquote(link.strip()) for link in raw_links if isinstance(link, str) and link.strip()]))
#             else:
#                 links = []

#             valid_links = []
#             for link in links:
#                 if link.startswith("http") and check_link_validity(link):
#                     valid_links.append(link)

#             if not valid_links:
#                 st.warning("⚠️ No valid links found for this post.")
#                 continue
            
#             # Display full clickable links
#             st.markdown("**Apply Link(s):**")
#             for idx, link in enumerate(valid_links, 1):
#                 link = resolver.resolve_url(link)
#                 st.markdown(f"- [🔗 {link}]({link})", unsafe_allow_html=True)

def show_analytics(data_loader: DataLoader):
    try:
        stats = data_loader.get_data_stats()
        st.subheader("📊 Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts Scraped", stats["summary"]["total_posts"])
        with col2:
            st.metric("Eligible Posts", stats["summary"]["eligible_posts"])
        with col3:
            st.metric("Email Contacts", stats["summary"]["posts_with_emails"])
        with col4:
            st.metric("Apply Links", stats["summary"]["posts_with_apply_links"])

        st.subheader("📁 Data Files")
        file_data = [
            {
                "File Type": file_type.replace("_", " ").title(),
                "Records": info["count"],
                "Size (KB)": round(info["file_size"] / 1024, 2),
                "Status": "✅ Available" if info["file_exists"] else "❌ Missing"
            }
            for file_type, info in stats["files"].items()
        ]
        if file_data:
            df = pd.DataFrame(file_data)
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def show_system_status():
    st.subheader("💻 System Information")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Configuration Status:**")
        checks = [
            ("Resume File", os.path.exists(config.resume_path)),
            ("LinkedIn Cookie", bool(config.linkedin_cookie)),
            ("Email Accounts", len(config.email_accounts) > 0),
            ("Azure OpenAI", bool(config.ai.api_key)),
            ("Data Directory", os.path.exists(config.data_dir)),
            ("Logs Directory", os.path.exists(config.logs_dir))
        ]
        for name, status in checks:
            icon = "✅" if status else "❌"
            st.write(f"{icon} {name}")

    with col2:
        st.write("**File System:**")
        try:
            data_size = get_dir_size_kb(config.data_dir)
            logs_size = get_dir_size_kb(config.logs_dir)
            st.write(f"📁 Data Directory: {data_size:.1f} KB")
            st.write(f"📋 Logs Directory: {logs_size:.1f} KB")
        except Exception as e:
            st.write(f"❌ Error checking directories: {e}")

def get_dir_size_kb(directory):
    if not os.path.exists(directory):
        return 0
    return sum(
        os.path.getsize(os.path.join(directory, f))
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ) / 1024

def main():
    st.title("🔗 LinkedIn Job Application Dashboard")
    st.markdown("---")

    data_loader = DataLoader()

    with st.sidebar:
        st.header("📊 Dashboard Controls")
        with st.expander("📈 Data Statistics", expanded=True):
            try:
                stats = data_loader.get_data_stats()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Posts", stats["summary"]["total_posts"])
                    st.metric("Eligible Posts", stats["summary"]["eligible_posts"])
                with col2:
                    st.metric("Email Contacts", stats["summary"]["posts_with_emails"])
                    st.metric("Apply Links", stats["summary"]["posts_with_apply_links"])
                st.metric("Emails Sent", stats["summary"]["emails_sent"])
            except Exception as e:
                st.error(f"Error loading statistics: {e}")

        if st.button("🔄 Refresh Data", key="refresh_button"):
            st.rerun()

        with st.expander("⚙️ Settings"):
            st.slider("Concurrent Workers", 1, 20, 10, help="Currently unused")
            st.checkbox("Show Failed Links", value=True, help="Currently unused")
            st.checkbox("Auto Refresh", value=False, help="Currently unused")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔗 Link Viewer", "📊 Analytics", "⚙️ System Status"])
    with tab1:
        show_apply_links(data_loader)
    with tab2:
        show_analytics(data_loader)
    with tab3:
        show_system_status()

if __name__ == "__main__":
    main()
