# import os
# import re
# import json
# import logging
# from dotenv import load_dotenv
# from playwright.async_api import async_playwright
# from tqdm import tqdm

# from eligibility import analyze_posts_batch
# from progress import tasks  # ✅ integrate progress tracking

# # 🔹 Old inline function
# def load_keywords(file_path="keywordsforjob.txt") -> list[str]:
#     with open(file_path, "r", encoding="utf-8") as f:
#         return [line.strip() for line in f if line.strip()]

# # Load environment variables
# load_dotenv()
# LI_AT = os.getenv("LINKEDIN_LI_AT")

# # Job role filters
# INCLUDE_ROLES = ["Java", "Backend", "Spring Boot", "SDE", "Software Engineer"]
# EXCLUDE_ROLES = ["Intern", "Manager", "Sales", "Support", "Web", "Internship"]

# # Logging configuration
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# def passes_job_role_filter(title):
#     """Filter job titles based on include/exclude roles."""
#     title_lower = title.lower()
#     if not any(kw.lower() in title_lower for kw in INCLUDE_ROLES):
#         return False
#     if any(bad_kw.lower() in title_lower for bad_kw in EXCLUDE_ROLES):
#         return False
#     return True

# def filter_jobs_by_experience(raw_jobs, max_experience):
#     """Filters jobs based on the maximum years of experience allowed."""
#     filtered_jobs = []
#     for job in raw_jobs:
#         description = job.get("description", "")
#         title = job.get("title", "")

#         years_of_experience = extract_years_of_experience(description) or extract_years_of_experience(title)

#         if years_of_experience is not None and years_of_experience <= max_experience:
#             filtered_jobs.append(job)
#         elif years_of_experience is None:
#             filtered_jobs.append(job)

#     return filtered_jobs

# def extract_years_of_experience(description):
#     """Extracts min years of experience from a string."""
#     if not description:
#         return None
#     match = re.search(r"(\d+)[+ -]?(?:to|-|–)?[ ]?(\d+)?[ ]?years?", description, re.IGNORECASE)
#     if match:
#         min_exp = int(match.group(1))
#         return min_exp
#     return None

# async def scrape_jobs(page, keyword, total_jobs, experience_levels, progress_bar, task_id=None, total=100):
#     """Scrape jobs for a given keyword using Playwright locators."""
#     raw_results = []

#     geo_id = "102713980"  # India
#     distance = 25
#     origin = "JOB_SEARCH_PAGE_JOB_FILTER"
#     refresh = "true"
#     hour = "r604800"

#     keyword_encoded = keyword.replace(" ", "%20")
#     search_url = (
#         f"https://www.linkedin.com/jobs/search/"
#         f"?distance={distance}"
#         f"&f_E={experience_levels}"
#         f"&f_TPR={hour}"
#         f"&geoId={geo_id}"
#         f"&keywords={keyword_encoded}"
#         f"&origin={origin}"
#         f"&refresh={refresh}"
#     )

#     logging.info(f"Scraping URL: {search_url}")

#     try:
#         await page.goto(search_url, timeout=180000, wait_until="networkidle")
#         await page.wait_for_selector('li[data-occludable-job-id]', timeout=60000)
#     except Exception as e:
#         logging.error(f"Error loading search page: {e}")
#         return raw_results

#     jobs_scraped = 0

#     while jobs_scraped < total_jobs:
#         try:
#             job_locator = page.locator('li[data-occludable-job-id]')
#             count = await job_locator.count()

#             for i in range(count):
#                 if jobs_scraped >= total_jobs:
#                     break

#                 job = job_locator.nth(i)

#                 try:
#                     await job.scroll_into_view_if_needed()
#                     await job.click(timeout=10000)
#                     await page.wait_for_selector("h1.t-24.t-bold.inline", timeout=10000)

#                     title = await page.locator("h1.t-24.t-bold.inline").first.inner_text()

#                     company = None
#                     if await page.locator(".job-details-jobs-unified-top-card__company-name a").count() > 0:
#                         company = await page.locator(".job-details-jobs-unified-top-card__company-name a").first.inner_text()

#                     location = None
#                     if await page.locator(
#                         ".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"
#                     ).count() > 0:
#                         location = await page.locator(
#                             ".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"
#                         ).first.inner_text()

#                     date_posted = None
#                     try:
#                         if await page.locator(".tvm__text--positive").count() > 0:
#                             text = await page.locator(".tvm__text--positive").first.inner_text()
#                             date_posted = text.strip()
#                         elif await page.locator(".tvm__text--low-emphasis").count() > 0:
#                             all_low = await page.locator(".tvm__text--low-emphasis").all_inner_texts()
#                             for txt in all_low:
#                                 if "ago" in txt.lower():
#                                     date_posted = txt.strip()
#                                     break
#                     except Exception as e:
#                         logging.warning(f"Date posted not found: {e}")

#                     description = None
#                     if await page.locator(".jobs-description-content__text--stretch").count() > 0:
#                         description = await page.locator(".jobs-description-content__text--stretch").first.inner_text()

#                     job_url = None
#                     if await job.locator("a.job-card-container__link").count() > 0:
#                         job_url = await job.locator("a.job-card-container__link").first.get_attribute("href")

#                     raw_results.append({
#                         "title": title.strip() if title else None,
#                         "company": company.strip() if company else None,
#                         "location": location.strip() if location else None,
#                         "date_posted": date_posted.strip() if date_posted else None,
#                         "description": description.strip() if description else None,
#                         "job_url": "https://www.linkedin.com" + job_url
#                     })

#                     jobs_scraped += 1
#                     progress_bar.update(1)

#                     if task_id:
#                         percent = int((jobs_scraped / total) * 20)
#                         tasks[task_id]["progress"] = percent
#                         tasks[task_id]["status"] = f"Scraping {percent}%"

#                 except Exception as e:
#                     logging.error(f"Error scraping job card: {e}")

#             next_button = page.locator("button.jobs-search-pagination__button--next")
#             if await next_button.count() > 0:
#                 is_disabled = await next_button.get_attribute("disabled")
#                 if is_disabled:
#                     logging.info("Next button disabled, end of results.")
#                     break
#                 try:
#                     await next_button.click()
#                     await page.wait_for_timeout(2000)
#                 except Exception as e:
#                     logging.error(f"Error clicking next: {e}")
#                     break
#             else:
#                 break
#         except Exception as e:
#             logging.error(f"Error in loop: {e}")
#             break

#     return raw_results

# async def scrapJobsPost(max_exp: int, total_jobs: int, keywords: list[str], task_id=None):
#     """Main function to scrape LinkedIn job posts."""
#     experience_levels = "2%2C3%2C4"
#     jobs_per_keyword = max(1, total_jobs // len(keywords))

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
#         all_raw = []

#         with tqdm(total=total_jobs, desc="Scraping Progress", unit="job") as progress_bar:
#             for keyword in keywords:
#                 logging.info(f"🔍 Scraping keyword: {keyword}")
#                 raw = await scrape_jobs(page, keyword, jobs_per_keyword, experience_levels, progress_bar, task_id=task_id, total=total_jobs)
#                 all_raw.extend(raw)

#         await browser.close()

#     if task_id:
#         tasks[task_id]["progress"] = 20
#         tasks[task_id]["status"] = "Filtering jobs..."

#     filtered_jobs = filter_jobs_by_experience(all_raw, max_exp)
#     logging.info(f"✅ Jobs after experience filter: {len(filtered_jobs)}")

#     if task_id:
#         tasks[task_id]["progress"] = 30
#         tasks[task_id]["status"] = "Running eligibility check..."

#     temp_jobs = [{"Job_Description": post} for post in filtered_jobs]
#     processed_posts = await analyze_posts_batch(temp_jobs, max_exp, task_id=task_id)

#     final_jobs = []
#     i = 0
#     for post in processed_posts:
#         if post.get("Eligibility") == "Eligible":
#             final_jobs.append(filtered_jobs[i])
#         i += 1

#     os.makedirs("data", exist_ok=True)
#     with open("data/filtered_jobs.json", "w", encoding="utf-8") as f:
#         json.dump(final_jobs, f, ensure_ascii=False, indent=4)

#     if task_id:
#         tasks[task_id]["progress"] = 100
#         tasks[task_id]["status"] = "Jobs pipeline completed ✅"

#     logging.info(f"✅ Jobs saved: {len(final_jobs)} → data/filtered_jobs.json")
import os
import re
import json
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from tqdm import tqdm
import asyncio

from eligibility import analyze_posts_batch
from progress import tasks, init_task  # ✅ init_task added

# Load environment variables
load_dotenv()
LI_AT = os.getenv("LINKEDIN_LI_AT")

# Job role filters
INCLUDE_ROLES = ["Java", "Backend", "Spring Boot", "SDE", "Software Engineer"]
EXCLUDE_ROLES = ["Intern", "Manager", "Sales", "Support", "Web", "Internship"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def passes_job_role_filter(title):
    title_lower = title.lower()
    if not any(kw.lower() in title_lower for kw in INCLUDE_ROLES):
        return False
    if any(bad_kw.lower() in title_lower for bad_kw in EXCLUDE_ROLES):
        return False
    return True

def filter_jobs_by_experience(raw_jobs, max_experience):
    """Filters jobs based on the maximum years of experience allowed."""
    filtered_jobs = []
    for job in raw_jobs:
        description = job.get("description", "")
        title = job.get("title", "")

        years_of_experience = extract_years_of_experience(description) or extract_years_of_experience(title)

        if years_of_experience is not None and years_of_experience <= max_experience:
            filtered_jobs.append(job)
        elif years_of_experience is None:
            filtered_jobs.append(job)

    return filtered_jobs

def extract_years_of_experience(description):
    """Extracts min years of experience from a string."""
    if not description:
        return None
    match = re.search(r"(\d+)[+ -]?(?:to|-|–)?[ ]?(\d+)?[ ]?years?", description, re.IGNORECASE)
    if match:
        min_exp = int(match.group(1))
        return min_exp
#     return None

async def scrape_jobs(page, keyword, jobs_per_keyword, experience_levels, progress_bar, task_id=None, total=100):
    raw_results = []

    geo_id = "102713980"  # India
    distance = 25
    origin = "JOB_SEARCH_PAGE_JOB_FILTER"
    refresh = "true"
    hour = "r604800"

    keyword_encoded = keyword.replace(" ", "%20")
    search_url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?distance={distance}&f_E={experience_levels}&f_TPR={hour}"
        f"&geoId={geo_id}&keywords={keyword_encoded}&origin={origin}&refresh={refresh}"
    )

    logging.info(f"Scraping URL: {search_url}")

    try:
        await page.goto(search_url, timeout=100000, wait_until="networkidle")
        await page.wait_for_selector('li[data-occludable-job-id]', timeout=50000)
    except Exception as e:
        logging.error(f"Error loading search page: {e}")
        return raw_results

    jobs_scraped = 0

    while jobs_scraped < jobs_per_keyword:
        try:
            job_locator = page.locator('li[data-occludable-job-id]')
            count = await job_locator.count()

            for i in range(count):
                if jobs_scraped >= jobs_per_keyword:
                    break

                job = job_locator.nth(i)
                try:
                    await job.scroll_into_view_if_needed()
                    await job.click(timeout=8000)
                    await page.wait_for_selector("h1.t-24.t-bold.inline", timeout=8000)

                    title = await page.locator("h1.t-24.t-bold.inline").first.inner_text()
                    company = None
                    if await page.locator(".job-details-jobs-unified-top-card__company-name a").count() > 0:
                        company = await page.locator(".job-details-jobs-unified-top-card__company-name a").first.inner_text()

                    location = None
                    if await page.locator(
                        ".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"
                    ).count() > 0:
                        location = await page.locator(
                            ".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"
                        ).first.inner_text()

                    description = None
                    if await page.locator(".jobs-description-content__text--stretch").count() > 0:
                        description = await page.locator(".jobs-description-content__text--stretch").first.inner_text()

                    job_url = None
                    if await job.locator("a.job-card-container__link").count() > 0:
                        job_url = await job.locator("a.job-card-container__link").first.get_attribute("href")
                    date_posted = None
                    try:
                        if await page.locator(".tvm__text--positive").count() > 0:
                            text = await page.locator(".tvm__text--positive").first.inner_text()
                            date_posted = text.strip()
                        elif await page.locator(".tvm__text--low-emphasis").count() > 0:
                            all_low = await page.locator(".tvm__text--low-emphasis").all_inner_texts()
                            for txt in all_low:
                                if "ago" in txt.lower():
                                    date_posted = txt.strip()
                                    break
                    except Exception as e:
                        logging.warning(f"Date posted not found: {e}")
                    raw_results.append({
                        "title": title.strip() if title else None,
                        "date_posted": date_posted.strip() if date_posted else None,
                        "company": company.strip() if company else None,
                        "location": location.strip() if location else None,
                        "description": description.strip() if description else None,
                        "job_url": "https://www.linkedin.com" + job_url if job_url else None
                    })

                    jobs_scraped += 1
                    progress_bar.update(1)

                    if task_id and tasks.get(task_id):
                        tasks[task_id]["scraped"] += 1
                        done = tasks[task_id]["scraped"]
                        total_posts = tasks[task_id]["total_posts"] or 1
                        percent = int((done / total_posts) * 20)
                        tasks[task_id]["progress"] = percent
                        tasks[task_id]["status"] = f"Scraping {int((done/total_posts)*100)}%"


                except Exception as e:
                    logging.error(f"Error scraping job card: {e}")

            next_button = page.locator("button.jobs-search-pagination__button--next")
            if await next_button.count() > 0:
                if await next_button.get_attribute("disabled"):
                    break
                await next_button.click()
                await page.wait_for_timeout(1000)
            else:
                break
        except Exception as e:
            logging.error(f"Error in loop: {e}")
            break

    return raw_results

async def scrapJobsPost(max_exp: int, total_jobs: int, keywords: list[str], task_id=None):
    experience_levels = "2%2C3%2C4"
    jobs_per_keyword = max(1, total_jobs // len(keywords))

    if task_id:
        init_task(task_id, total_posts=total_jobs)
        tasks[task_id]["status"] = "Jobs scraping started..."

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{
            "name": "li_at", "value": LI_AT, "domain": ".linkedin.com",
            "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"
        }])

        progress_bar = tqdm(total=total_jobs, desc="Jobs Scraping Progress", unit="job")
        semaphore = asyncio.Semaphore(3)

        async def scrape_keyword(keyword):
            async with semaphore:
                page = await context.new_page()
                try:
                    return await scrape_jobs(page, keyword, jobs_per_keyword, experience_levels, progress_bar, task_id, total_jobs)
                finally:
                    await page.close()

        tasks_list = [scrape_keyword(k) for k in keywords]
        results = await asyncio.gather(*tasks_list)

        await browser.close()
        progress_bar.close()

    all_raw = [job for sublist in results for job in sublist]

    if task_id:
        tasks[task_id]["progress"] = 20
        tasks[task_id]["status"] = "Filtering jobs..."

    filtered_jobs = filter_jobs_by_experience(all_raw, max_exp)
    logging.info(f"✅ Jobs after experience filter: {len(filtered_jobs)}")

    if task_id:
        tasks[task_id]["progress"] = 30
        tasks[task_id]["status"] = "Running eligibility check..."

    temp_jobs = [{"Job_Description": post.get("description", "")} for post in filtered_jobs]
    processed_posts = await analyze_posts_batch(temp_jobs, max_exp, task_id=task_id)

    final_jobs = []
    for i, post in enumerate(processed_posts):
        if post.get("Eligibility") == "Eligible":
            final_jobs.append(filtered_jobs[i])

    os.makedirs("data", exist_ok=True)
    with open("data/filtered_jobs.json", "w", encoding="utf-8") as f:
        json.dump(final_jobs, f, ensure_ascii=False, indent=4)

    if task_id:
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "Jobs pipeline completed ✅"

    logging.info(f"✅ Jobs saved: {len(final_jobs)} → data/filtered_jobs.json")
