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



# import os
# import re
# from dotenv import load_dotenv
# from playwright.async_api import async_playwright, TimeoutError
# from config import DATA_DIR
# from tqdm import tqdm
# import asyncio

# load_dotenv()
# LI_AT = os.getenv("LINKEDIN_LI_AT")


# async def scrape_linkedin_posts(search_url, max_posts):
#     posts_data = []
#     retries = 3

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context()

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
#         print(f"\n🔄 Scraping up to {max_posts} posts from LinkedIn...")
#         try:
#             await page.goto(search_url, timeout=60000)

#             for attempt in range(1, retries + 1):
#                 try:
#                     await page.wait_for_selector("div.feed-shared-update-v2", timeout=60000)
#                     break
#                 except TimeoutError:
#                     print(f"⚠️ Retry {attempt}/{retries} for wait_for_selector failed.")
#                     if attempt == retries:
#                         print("❌ Failed to load or find content on page.")
#                         return []
#                     await asyncio.sleep(3)

#             collected = set()
#             last_count = 0
#             stable_scrolls = 0

#             progress_bar = tqdm(total=max_posts, desc="📈 Scraping Progress", ncols=80)

#             while len(posts_data) < max_posts:
#                 posts = await page.query_selector_all("div.feed-shared-update-v2")

#                 for post in posts:
#                     html = await post.inner_html()
#                     if html in collected:
#                         continue

#                     try:
#                         see_more = await post.query_selector('button[aria-label="See more"]')
#                         if see_more:
#                             await see_more.click()
#                             await page.wait_for_timeout(200)
#                     except:
#                         pass

#                     text = await post.inner_text()
#                     start = text.find("Follow")
#                     end = text.rfind("Like")
#                     if start != -1 and end != -1 and end > start:
#                         content = text[start + 6:end].strip()
#                         content = re.sub(r'#\w+', '', content)
#                         content = re.sub(r'\bhashtag\b', '', content, flags=re.IGNORECASE)
#                         content = re.sub(r'\s{2,}', ' ', content).strip()
#                     else:
#                         content = "[❌ Could not extract clean content]"

#                     if content not in collected:
#                         posts_data.append(content)
#                         collected.add(html)
#                         progress_bar.update(1)

#                     if len(posts_data) >= max_posts:
#                         break

#                 await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#                 await page.wait_for_timeout(3000)

#                 if len(posts_data) == last_count:
#                     stable_scrolls += 1
#                 else:
#                     stable_scrolls = 0
#                     last_count = len(posts_data)

#                 if stable_scrolls >= 5:
#                     print("⛔ No new posts loaded after multiple scrolls. Stopping.")
#                     break

#             progress_bar.close()
#             await browser.close()


#             return posts_data

#         except Exception as e:
#             print(f"❌ Scraping error: {e}")
#             return []


# async def collect_linkedin_posts(search_url, total_posts):
#     return await scrape_linkedin_posts(search_url, total_posts)

# import os
# import re
# from dotenv import load_dotenv
# from playwright.async_api import async_playwright, TimeoutError
# from tqdm import tqdm
# import asyncio

# load_dotenv()
# LI_AT = os.getenv("LINKEDIN_LI_AT")

# async def scrape_posts_on_page(page, search_url, max_posts):
#     posts_data = []
#     retries = 3
#     await page.goto(search_url, timeout=120000,wait_until="networkidle")

#     for attempt in range(1, retries + 1):
#         try:
#             await page.wait_for_selector("div.feed-shared-update-v2", timeout=120000)
#             break
#         except TimeoutError:
#             if attempt == retries:
#                 print("❌ Failed to load or find content on page.")
#                 return []
#             await asyncio.sleep(3)

#     collected = set()
#     last_count = 0
#     stable_scrolls = 0

#     progress_bar = tqdm(total=max_posts, desc=f"Scraping: {search_url}", ncols=80)

#     while len(posts_data) < max_posts:
#         posts = await page.query_selector_all("div.feed-shared-update-v2")

#         for post in posts:
#             html = await post.inner_html()
#             if html in collected:
#                 continue

#             try:
#                 see_more = await post.query_selector('button[aria-label="See more"]')
#                 if see_more:
#                     await see_more.click()
#                     await page.wait_for_timeout(200)
#             except:
#                 pass

#             text = await post.inner_text()
#             start = text.find("Follow")
#             end = text.rfind("Like")
#             if start != -1 and end != -1 and end > start:
#                 content = text[start + 6:end].strip()
#                 content = re.sub(r'#\w+', '', content)
#                 content = re.sub(r'\bhashtag\b', '', content, flags=re.IGNORECASE)
#                 content = re.sub(r'\s{2,}', ' ', content).strip()
#             else:
#                 content = "[❌ Could not extract clean content]"

#             if content not in collected:
#                 posts_data.append(content)
#                 collected.add(html)
#                 progress_bar.update(1)

#             if len(posts_data) >= max_posts:
#                 break

#         await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#         await page.wait_for_timeout(3000)

#         if len(posts_data) == last_count:
#             stable_scrolls += 1
#         else:
#             stable_scrolls = 0
#             last_count = len(posts_data)

#         if stable_scrolls >= 5:
#             print("⛔ No new posts loaded after multiple scrolls. Stopping.")
#             break

#     progress_bar.close()
#     return posts_data
# from asyncio import Semaphore

# async def scrape_all_keywords_parallel(keywords: list[str], posts_per_keyword: int, max_concurrent_tabs: int = 2):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context()

#         await context.add_cookies([{
#             "name": "li_at",
#             "value": LI_AT,
#             "domain": ".linkedin.com",
#             "path": "/",
#             "httpOnly": True,
#             "secure": True,
#             "sameSite": "Lax"
#         }])

#         semaphore = Semaphore(max_concurrent_tabs)

#         async def scrape_keyword(keyword):
#             async with semaphore:
#                 encoded_query = keyword.replace(" ", "%20")
#                 search_url = f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={encoded_query}&origin=FACETED_SEARCH"
#                 page = await context.new_page()
#                 try:
#                     posts = await scrape_posts_on_page(page, search_url, posts_per_keyword)
#                 finally:
#                     await page.close()
#                 return posts

#         tasks = [scrape_keyword(k) for k in keywords]
#         results = await asyncio.gather(*tasks)

#         await browser.close()

#         all_posts = [post for sublist in results for post in sublist]
#         return all_posts


import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError
from tqdm import tqdm
import asyncio

load_dotenv()
LI_AT = os.getenv("LINKEDIN_LI_AT")

async def scrape_posts_on_page(page, search_url, max_posts, progress_bar):
    posts_data = []
    retries = 3
    await page.goto(search_url, timeout=120000, wait_until="networkidle")

    for attempt in range(1, retries + 1):
        try:
            await page.wait_for_selector("div.feed-shared-update-v2", timeout=120000)
            break
        except TimeoutError:
            if attempt == retries:
                print("❌ Failed to load or find content on page.")
                return []
            await asyncio.sleep(3)

    collected = set()
    last_count = 0
    stable_scrolls = 0

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
                progress_bar.update(1)  # Update shared progress bar

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

    return posts_data


async def scrape_all_keywords_parallel(keywords: list[str], posts_per_keyword: int, max_concurrent_tabs):
    total_posts = posts_per_keyword * len(keywords)
    progress_bar = tqdm(total=total_posts, desc="Total Scraping Progress", ncols=80)

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

        semaphore = asyncio.Semaphore(max_concurrent_tabs)

        async def scrape_keyword(keyword):
            async with semaphore:
                encoded_query = keyword.replace(" ", "%20")
                search_url = f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={encoded_query}&origin=FACETED_SEARCH"
                page = await context.new_page()
                try:
                    posts = await scrape_posts_on_page(page, search_url, posts_per_keyword, progress_bar)
                finally:
                    await page.close()
                return posts

        tasks = [scrape_keyword(k) for k in keywords]
        results = await asyncio.gather(*tasks)

        await browser.close()
        progress_bar.close()

        all_posts = [post for sublist in results for post in sublist]
        return all_posts


# Deprecated single-URL scraper placeholder
async def collect_linkedin_posts(search_url, total_posts):
    pass
