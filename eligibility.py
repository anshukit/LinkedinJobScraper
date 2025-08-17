import asyncio
import os
import json
import pdfplumber
from azure_llm import llm
from prompt import combined_prompt_template, resume_summary_prompt_template
from progress import tasks


RESUME_PATH = os.path.join("data", "resume.pdf")

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def load_resume_text():
    with pdfplumber.open(RESUME_PATH) as pdf:
        return " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    
def generate_resume_summary(resume_text: str) -> str:
    prompt = resume_summary_prompt_template(resume_text)
    response = llm.invoke(prompt)
    return response.content.strip()

async def analyze_batch(batch, resume_summary, experience, semaphore):
    prompt = combined_prompt_template(batch, resume_summary, experience)
    async with semaphore:
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content.strip()
    while content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
    parsed = json.loads(content)
    results = []
    if isinstance(parsed, list):
        for j, item in enumerate(parsed):
            item["Job_Description"] = batch[j] if j < len(batch) else ""
            results.append(item)
    else:
        parsed["Job_Description"] = batch[0]
        results.append(parsed)
    return results

async def analyze_posts_batch(post_list, experience, task_id=None, batch_size=7):
    resume_text = extract_text_from_pdf(RESUME_PATH)
    resume_summary = generate_resume_summary(resume_text)

    semaphore = asyncio.Semaphore(2)
    batches = [post_list[i : i + batch_size] for i in range(0, len(post_list), batch_size)]

    results = []
    total_batches = len(batches)

    for idx, batch in enumerate(batches, start=1):
        batch_result = await analyze_batch(batch, resume_summary, experience, semaphore)
        results.extend(batch_result)

        if task_id:
            percent = int((idx / total_batches) * 100)
            tasks[task_id]["progress"] = 20 + int(60 * (percent / 100))
            tasks[task_id]["status"] = f"LLM Analysis {percent}%"

    return results
