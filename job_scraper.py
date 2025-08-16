# import os
# import re
# import json
# import logging
# from dotenv import load_dotenv
# from playwright.async_api import async_playwright
# from tqdm import tqdm

# from utils import load_keywords 

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
#     """
#     Filters jobs based on the maximum years of experience allowed.
#     """
#     filtered_jobs = []
#     for job in raw_jobs:
#         description = job.get("description", "")
#         title = job.get("title", "")

#         # Extract years of experience from the description or title
#         years_of_experience = extract_years_of_experience(description) or extract_years_of_experience(title)

#         # Include the job if the years of experience is within the limit
#         if years_of_experience is not None and years_of_experience <= max_experience:
#             filtered_jobs.append(job)
#         elif years_of_experience is None:  # If no experience requirement is found, include the job
#             filtered_jobs.append(job)

#     return filtered_jobs
# def extract_years_of_experience(description):
#     """
#     Extracts the years of experience from a job description or title.
#     Returns the minimum years of experience found, or None if not found.
#     """
#     if not description:
#         return None

#     # Regular expression to find patterns like "1-2 years", "3+ years", "2 years"
#     match = re.search(r"(\d+)[+ -]?(?:to|-|–)?[ ]?(\d+)?[ ]?years?", description, re.IGNORECASE)
#     if match:
#         min_exp = int(match.group(1))
#         max_exp = int(match.group(2)) if match.group(2) else None
#         return min_exp  # Return the minimum years of experience
#     return None

# async def scrape_jobs(page, keyword, total_jobs, experience_levels, progress_bar):
#     """Scrape jobs for a given keyword."""
#     raw_results = []

#     # LinkedIn search parameters
#     geo_id = "102713980"  # GeoId for India
#     distance = 25  # Search radius in miles
#     origin = "JOB_SEARCH_PAGE_JOB_FILTER"
#     refresh = "true"
#     hour = "r86400"

#     # Replace spaces in the keyword with %20 for URL encoding
#     keyword_encoded = keyword.replace(" ", "%20")

#     # Construct the search URL
#     search_url = (
#         f"https://www.linkedin.com/jobs/search/"
#         f"?distance={distance}"  # Search radius
#         f"&f_E={experience_levels}"  # Dynamic experience levels
#         f"&f_TPR={hour}"
#         f"&geoId={geo_id}"  # Geographic location
#         f"&keywords={keyword_encoded}"  # Search keyword
#         f"&origin={origin}"  # Origin of the search
#         f"&refresh={refresh}"  # Refresh flag
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
#             # Select all job cards within the list
#             job_cards = await page.query_selector_all('li[data-occludable-job-id]')
#             for job in job_cards:
#                 if jobs_scraped >= total_jobs:
#                     break

#                 try:
#                     # Scroll to the specific job card to ensure it is loaded
#                     await job.scroll_into_view_if_needed()
#                     await page.wait_for_timeout(500)  # Reduced delay

#                     # Click on the job card to load details in the right pane
#                     await job.click()
#                     await page.wait_for_timeout(1000)  # Reduced delay

#                     # Extract job details
#                     job_url_element = await job.query_selector("a.job-card-container__link")
#                     job_url = await job_url_element.evaluate("el => el.href") if job_url_element else None

#                     title_element = await page.query_selector("h1.t-24.t-bold.inline")
#                     title = await title_element.evaluate("el => el.innerText.trim()") if title_element else None

#                     if title and not passes_job_role_filter(title):
#                         progress_bar.update(1)
#                         continue

#                     company_element = await page.query_selector(".job-details-jobs-unified-top-card__company-name a")
#                     company = await company_element.evaluate("el => el.innerText.trim()") if company_element else None

#                     location_element = await page.query_selector(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis")
#                     location = await location_element.evaluate("el => el.innerText.trim()") if location_element else None

#                     date_posted_element = await page.query_selector(".tvm__text--positive > strong > span")
#                     date_posted = await date_posted_element.evaluate("el => el.innerText.trim()") if date_posted_element else "1 day ago"

#                     description_element = await page.query_selector(".jobs-description-content__text--stretch")
#                     description = await description_element.evaluate("el => el.innerText.trim()") if description_element else None

#                     raw_results.append({
#                         "title": title,
#                         "company": company,
#                         "location": location,
#                         "date_posted": date_posted,
#                         "description": description,
#                         "job_url": job_url
#                     })

#                     jobs_scraped += 1
#                     progress_bar.update(1)

#                 except Exception as e:
#                     logging.error(f"Error scraping job card: {e}")

#             # Handle pagination
#             next_button = await page.query_selector("button.jobs-search-pagination__button--next")
#             if next_button:
#                 is_disabled = await next_button.get_attribute("disabled")
#                 if is_disabled:
#                     logging.info("The 'Next' button is disabled. End of results.")
#                     break
#                 try:
#                     await next_button.click()
#                     await page.wait_for_timeout(2000)  # Reduced delay
#                 except Exception as e:
#                     logging.error(f"Error clicking 'Next' button: {e}")
#                     break
#             else:
#                 logging.info("No 'Next' button found or all jobs scraped. End of results.")
#                 break

#         except Exception as e:
#             logging.error(f"Error during scraping loop: {e}")
#             break

#     return raw_results

# async def scrapJobsPost(max_exp: int, total_jobs: int):
#     """Main function to scrape LinkedIn job posts."""
#     experience_levels = "2%2C3%2C4"  # Hardcoded experience levels
#     keywords = load_keywords("keywordsforjob.txt")
#     jobs_per_keyword = max(1, total_jobs // len(keywords))

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)  # Set headless=True for production
#         context = await browser.new_context()

#         # Add LinkedIn authentication cookie
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

#         # Initialize the progress bar
#         with tqdm(total=total_jobs, desc="Scraping Progress", unit="job") as progress_bar:
#             for keyword in keywords:
#                 logging.info(f"🔍 Scraping keyword: {keyword}")
#                 raw = await scrape_jobs(page, keyword, jobs_per_keyword, experience_levels, progress_bar)
#                 all_raw.extend(raw)

#         await browser.close()

#     # Filter jobs based on experience
#     filtered_jobs = filter_jobs_by_experience(all_raw, max_exp)
#     os.makedirs("data", exist_ok=True)

#     # # Save filtered jobs to JSON 
#     # with open("data/filtered_jobs.json", "w", encoding="utf-8") as f:
#     #     json.dump(filtered_jobs, f, ensure_ascii=False, indent=4)
#     file_path = "data/filtered_jobs.json"
#     if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#         with open(file_path, "r", encoding="utf-8") as f:
#             jobs = json.load(f)
#     else:
#         print("⚠️ No jobs found or file is empty")
#     jobs = []
#     logging.info(f"✅ Jobs saved: {len(filtered_jobs)} → data/filtered_jobs.json and data/filtered_jobs.csv")

import os
import re
import json
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from tqdm import tqdm

# 🔹 Old inline function
def load_keywords(file_path="keywordsforjob.txt") -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Load environment variables
load_dotenv()
LI_AT = os.getenv("LINKEDIN_LI_AT")

# Job role filters
INCLUDE_ROLES = ["Java", "Backend", "Spring Boot", "SDE", "Software Engineer"]
EXCLUDE_ROLES = ["Intern", "Manager", "Sales", "Support", "Web", "Internship"]

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def passes_job_role_filter(title):
    """Filter job titles based on include/exclude roles."""
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

        # Extract years of experience
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
    return None

async def scrape_jobs(page, keyword, total_jobs, experience_levels, progress_bar):
    """Scrape jobs for a given keyword."""
    raw_results = []

    geo_id = "102713980"  # India
    distance = 25
    origin = "JOB_SEARCH_PAGE_JOB_FILTER"
    refresh = "true"
    hour = "r86400"

    keyword_encoded = keyword.replace(" ", "%20")

    search_url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?distance={distance}"
        f"&f_E={experience_levels}"
        f"&f_TPR={hour}"
        f"&geoId={geo_id}"
        f"&keywords={keyword_encoded}"
        f"&origin={origin}"
        f"&refresh={refresh}"
    )

    logging.info(f"Scraping URL: {search_url}")

    try:
        await page.goto(search_url, timeout=180000, wait_until="networkidle")
        await page.wait_for_selector('li[data-occludable-job-id]', timeout=60000)
    except Exception as e:
        logging.error(f"Error loading search page: {e}")
        return raw_results

    jobs_scraped = 0

    while jobs_scraped < total_jobs:
        try:
            job_cards = await page.query_selector_all('li[data-occludable-job-id]')
            for job in job_cards:
                if jobs_scraped >= total_jobs:
                    break
                try:
                    await job.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)

                    await job.click()
                    await page.wait_for_timeout(1000)

                    job_url_element = await job.query_selector("a.job-card-container__link")
                    job_url = await job_url_element.evaluate("el => el.href") if job_url_element else None

                    title_element = await page.query_selector("h1.t-24.t-bold.inline")
                    title = await title_element.evaluate("el => el.innerText.trim()") if title_element else None

                    if title and not passes_job_role_filter(title):
                        progress_bar.update(1)
                        continue

                    company_element = await page.query_selector(".job-details-jobs-unified-top-card__company-name a")
                    company = await company_element.evaluate("el => el.innerText.trim()") if company_element else None

                    location_element = await page.query_selector(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis")
                    location = await location_element.evaluate("el => el.innerText.trim()") if location_element else None

                    date_posted_element = await page.query_selector(".tvm__text--positive > strong > span")
                    date_posted = await date_posted_element.evaluate("el => el.innerText.trim()") if date_posted_element else "1 day ago"

                    description_element = await page.query_selector(".jobs-description-content__text--stretch")
                    description = await description_element.evaluate("el => el.innerText.trim()") if description_element else None

                    raw_results.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "date_posted": date_posted,
                        "description": description,
                        "job_url": job_url
                    })

                    jobs_scraped += 1
                    progress_bar.update(1)

                except Exception as e:
                    logging.error(f"Error scraping job card: {e}")

            next_button = await page.query_selector("button.jobs-search-pagination__button--next")
            if next_button:
                is_disabled = await next_button.get_attribute("disabled")
                if is_disabled:
                    logging.info("Next button disabled, end of results.")
                    break
                try:
                    await next_button.click()
                    await page.wait_for_timeout(2000)
                except Exception as e:
                    logging.error(f"Error clicking next: {e}")
                    break
            else:
                break
        except Exception as e:
            logging.error(f"Error in loop: {e}")
            break

    return raw_results

async def scrapJobsPost(max_exp: int, total_jobs: int):
    """Main function to scrape LinkedIn job posts."""
    experience_levels = "2%2C3%2C4"
    keywords = load_keywords("keywordsforjob.txt")
    jobs_per_keyword = max(1, total_jobs // len(keywords))

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
        all_raw = []

        from tqdm import tqdm
        with tqdm(total=total_jobs, desc="Scraping Progress", unit="job") as progress_bar:
            for keyword in keywords:
                logging.info(f"🔍 Scraping keyword: {keyword}")
                raw = await scrape_jobs(page, keyword, jobs_per_keyword, experience_levels, progress_bar)
                all_raw.extend(raw)

        await browser.close()

    filtered_jobs = filter_jobs_by_experience(all_raw, max_exp)
    os.makedirs("data", exist_ok=True)

    with open("data/filtered_jobs.json", "w", encoding="utf-8") as f:
        json.dump(filtered_jobs, f, ensure_ascii=False, indent=4)

    logging.info(f"✅ Jobs saved: {len(filtered_jobs)} → data/filtered_jobs.json")
