# import os
# import json
# import re
# from dotenv import load_dotenv
# from playwright.async_api import async_playwright
# from config import DATA_DIR
# from tqdm import tqdm

# load_dotenv()
# LI_AT = os.getenv("LINKEDIN_LI_AT")


# async def scrape_linkedin_posts(search_url, max_posts):
#     posts_data = []

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context()

#         # Set LinkedIn session cookie
#         await context.add_cookies([{
#             "name": "li_at",
#             "value": LI_AT,
#             "domain": ".linkedin.com",
#             "path": "/",
#             "httpOnly": True,
#             "secure": True,
#             "sameSite": "Lax"
#         }])

#         page = await context.new_page()
#         await page.goto(search_url)
#         await page.wait_for_selector("div.feed-shared-update-v2", timeout=60000)

#         collected = set()
#         last_count = 0
#         stable_scrolls = 0

#         # ✅ Initialize progress bar
#         progress_bar = tqdm(total=max_posts, desc="📈 Scraping Progress", ncols=80)

#         while len(posts_data) < max_posts:
#             posts = await page.query_selector_all("div.feed-shared-update-v2")

#             for post in posts:
#                 html = await post.inner_html()
#                 if html in collected:
#                     continue

#                 try:
#                     see_more = await post.query_selector('button[aria-label="See more"]')
#                     if see_more:
#                         await see_more.click()
#                         await page.wait_for_timeout(200)
#                 except:
#                     pass

#                 text = await post.inner_text()
#                 start = text.find("Follow")
#                 end = text.rfind("Like")
#                 if start != -1 and end != -1 and end > start:
#                     content = text[start + 6:end].strip()
#                     content = re.sub(r'#\w+', '', content)
#                     content = re.sub(r'\bhashtag\b', '', content, flags=re.IGNORECASE)
#                     content = re.sub(r'\s{2,}', ' ', content).strip()
#                 else:
#                     content = "[❌ Could not extract clean content]"

#                 if content not in collected:
#                     posts_data.append(content)
#                     collected.add(html)
#                     progress_bar.update(1)  # ✅ Update progress bar

#                 if len(posts_data) >= max_posts:
#                     break

#             await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#             await page.wait_for_timeout(3000)

#             # Stop if no new posts after 5 scrolls
#             if len(posts_data) == last_count:
#                 stable_scrolls += 1
#             else:
#                 stable_scrolls = 0
#                 last_count = len(posts_data)

#             if stable_scrolls >= 5:
#                 print("⛔ No new posts loaded after multiple scrolls. Stopping.")
#                 break

#         progress_bar.close()  # ✅ Close progress bar
#         await browser.close()

#     # Save to file
#     os.makedirs(DATA_DIR, exist_ok=True)
#     with open(f"{DATA_DIR}/all_linkedin_posts.jsonl", "w", encoding="utf-8") as f:
#         for post in posts_data:
#             f.write(json.dumps({"text": post}) + "\n")

#     return posts_data
# # Async wrapper for scraping
# async def collect_linkedin_posts(search_url, total_posts):
#     print(f"\n🔄 Scraping up to {total_posts} posts from LinkedIn...")
#     posts = await scrape_linkedin_posts(search_url, total_posts)
#     print(f"✅ Scraped {len(posts)} unique posts.\n")
#     return posts



import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError
from config import DATA_DIR
from tqdm import tqdm
import asyncio

load_dotenv()
LI_AT = os.getenv("LINKEDIN_LI_AT")


async def scrape_linkedin_posts(search_url, max_posts):
    posts_data = []
    retries = 3

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        await context.add_cookies([{
            "name": "li_at",
            "value": LI_AT,
            "domain": ".linkedin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }])

        page = await context.new_page()
        print(f"\n🔄 Scraping up to {max_posts} posts from LinkedIn...")
        try:
            await page.goto(search_url, timeout=60000)

            for attempt in range(1, retries + 1):
                try:
                    await page.wait_for_selector("div.feed-shared-update-v2", timeout=60000)
                    break
                except TimeoutError:
                    print(f"⚠️ Retry {attempt}/{retries} for wait_for_selector failed.")
                    if attempt == retries:
                        print("❌ Failed to load or find content on page.")
                        return []
                    await asyncio.sleep(3)

            collected = set()
            last_count = 0
            stable_scrolls = 0

            progress_bar = tqdm(total=max_posts, desc="📈 Scraping Progress", ncols=80)

            while len(posts_data) < max_posts:
                posts = await page.query_selector_all("div.feed-shared-update-v2")

                for post in posts:
                    html = await post.inner_html()
                    if html in collected:
                        continue

                    try:
                        see_more = await post.query_selector('button[aria-label="See more"]')
                        if see_more:
                            await see_more.click()
                            await page.wait_for_timeout(200)
                    except:
                        pass

                    text = await post.inner_text()
                    start = text.find("Follow")
                    end = text.rfind("Like")
                    if start != -1 and end != -1 and end > start:
                        content = text[start + 6:end].strip()
                        content = re.sub(r'#\w+', '', content)
                        content = re.sub(r'\bhashtag\b', '', content, flags=re.IGNORECASE)
                        content = re.sub(r'\s{2,}', ' ', content).strip()
                    else:
                        content = "[❌ Could not extract clean content]"

                    if content not in collected:
                        posts_data.append(content)
                        collected.add(html)
                        progress_bar.update(1)

                    if len(posts_data) >= max_posts:
                        break

                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)

                if len(posts_data) == last_count:
                    stable_scrolls += 1
                else:
                    stable_scrolls = 0
                    last_count = len(posts_data)

                if stable_scrolls >= 5:
                    print("⛔ No new posts loaded after multiple scrolls. Stopping.")
                    break

            progress_bar.close()
            await browser.close()


            return posts_data

        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return []


async def collect_linkedin_posts(search_url, total_posts):
    return await scrape_linkedin_posts(search_url, total_posts)
