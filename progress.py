# # progress.py

# shared progress tracking dict
tasks = {}

def init_task(task_id, total_posts=0):
    tasks[task_id] = {
        "progress": 0,
        "status": "Starting...",
        "scraped": 0,        # counter of posts scraped so far
        "total_posts": total_posts
    }
