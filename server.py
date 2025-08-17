
import os
import sys
import asyncio
import logging
import uuid
from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Import actual scrapers
from job_scraper import scrapJobsPost
from post_scraper import scrape_process_all_keywords

# Windows fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Global task tracker (shared by all modules)
# server.py
from progress import tasks   # instead of defining tasks = {} here


# FastAPI app
app = FastAPI()

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://52.168.130.75:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- MODELS ----------
class ScrapeRequest(BaseModel):
    experience: int
    total_posts: int
    mode: str               # "postData" or "jobsData"
    keywords: list[str]

# --------- ROUTES ----------
@app.post("/scrape-linkedin")
async def scrape_linkedin(payload: ScrapeRequest = Body(...)):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"progress": 0, "status": "Starting...", "result": None}

    async def runner():
        try:
            if payload.mode == "postData":
                await scrape_process_all_keywords(payload.experience, payload.total_posts, payload.keywords, task_id=task_id)
            elif payload.mode == "jobsData":
                await scrapJobsPost(payload.experience, payload.total_posts, payload.keywords, task_id=task_id)
            tasks[task_id]["status"] = "Completed ✅"
        except Exception as e:
            logging.error(f"Error in /scrape-linkedin: {e}")
            tasks[task_id]["status"] = f"Error: {str(e)}"

    asyncio.create_task(runner())

    return {"task_id": task_id, "status": "started"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    return tasks.get(task_id, {"progress": 0, "status": "Unknown Task"})

# --------- MAIN ----------
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=False)
