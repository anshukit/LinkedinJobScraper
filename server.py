import os
import sys
import asyncio
import json
from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn
import logging
from job_scraper import scrapJobsPost
from post_scraper import scrape_process_all_keywords

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from config import DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()
# Define request model
class ScrapeRequest(BaseModel):
    experience: int
    total_posts: int
    mode: str  # "all_keywords" or "job_posts"

# Unified FastAPI endpoint
@app.post("/scrape-linkedin")
async def scrape_linkedin(payload: ScrapeRequest = Body(...)):
    try:
        if payload.mode == "postData":
            # Call the function for scraping all keywords
            await scrape_process_all_keywords(payload.experience, payload.total_posts)
            return {
                "status": "success",
                "message": f"Scraped {payload.total_posts} posts with experience {payload.experience} years (all keywords).",
            }
        elif payload.mode == "jobsData":
            # Call the function for scraping job posts
            await scrapJobsPost(payload.experience, payload.total_posts)
            return {
                "status": "success",
                "message": f"Scraped {payload.total_posts} job posts with experience {payload.experience} years.",
            }
        else:
            return {
                "status": "error",
                "message": f"Invalid mode: {payload.mode}. Use 'all_keywords' or 'job_posts'.",
            }
    except Exception as e:
        logging.error(f"Error in /scrape-linkedin: {e}")
        return {
            "status": "error",
            "message": str(e),
        }

# Main entry point for running the script
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run LinkedIn Job Scraper")
    parser.add_argument("--mode", choices=["cli", "api"], default="cli", help="Run mode: cli or api")
    parser.add_argument("--experience", type=int, default=2, help="Years of experience (for CLI mode)")
    parser.add_argument("--total_posts", type=int, default=20, help="Total posts to scrape (for CLI mode)")
    parser.add_argument("--scrape_mode", choices=["all_keywords", "job_posts"], default="all_keywords", help="Scrape mode for CLI")
    args = parser.parse_args()

    if args.mode == "cli":
        print("Running in CLI mode")
        if args.scrape_mode == "postData":
            asyncio.run(scrape_process_all_keywords(args.experience, args.total_posts))
        elif args.scrape_mode == "jobsData":
            asyncio.run(scrapJobsPost(args.experience, args.total_posts))
    else:
        print("Running FastAPI server")
        uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=False)