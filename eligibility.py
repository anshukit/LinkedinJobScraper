# from tqdm import tqdm
# import os
# import json
# import pdfplumber
# from azure_llm import llm
# from prompt import combined_prompt_template

# RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")

# def extract_text_from_pdf(file_path):
#     with pdfplumber.open(file_path) as pdf:
#         return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# def load_resume_text():
#     with pdfplumber.open(RESUME_PATH) as pdf:
#         return " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

# def analyze_posts_batch(post_list, resume_text, experience, batch_size=5):
#     results = []
#     num_batches = (len(post_list) + batch_size - 1) // batch_size

#     for i in tqdm(range(0, len(post_list), batch_size), total=num_batches, desc="🧠 LLM Analysis Progress", ncols=80):
#         batch = post_list[i:i + batch_size]
#         prompt = combined_prompt_template(batch, resume_text, experience)

#         try:
#             response = llm.invoke(prompt).content.strip()

#             # ✅ Clean up markdown-style blocks
#             while response.startswith("```"):
#                 response = response.strip("`").strip()
#                 if response.lower().startswith("json"):
#                     response = response[4:].strip()

#             if not response:
#                 raise ValueError("Empty response from LLM")

#             parsed = json.loads(response)

#             if isinstance(parsed, list):
#                 for j, item in enumerate(parsed):
#                     item["Job_Description"] = batch[j] if j < len(batch) else ""
#                     results.append(item)
#             else:
#                 parsed["Job_Description"] = batch[0]
#                 results.append(parsed)

#         except Exception as e:
#             results.append({
#                 "error": str(e),
#                 "raw_output": response if 'response' in locals() else None
#             })

#     return results

# eligibility.py

import asyncio
import os
import json
import pdfplumber
from tqdm import tqdm
from azure_llm import llm
from tqdm.asyncio import tqdm_asyncio
from prompt import combined_prompt_template, resume_summary_prompt_template

RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")


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


# def analyze_posts_batch(post_list, experience, batch_size=5):
#     resume_text = extract_text_from_pdf(RESUME_PATH)
#     resume_summary = generate_resume_summary(resume_text)

#     results = []
#     num_batches = (len(post_list) + batch_size - 1) // batch_size

#     for i in tqdm(range(0, len(post_list), batch_size), total=num_batches, desc="🧠 LLM Analysis Progress", ncols=80):
#         batch = post_list[i:i + batch_size]
#         prompt = combined_prompt_template(batch, resume_summary, experience)

#         try:
#             response = llm.invoke(prompt).content.strip()

#             # ✅ Clean up markdown-style code blocks
#             while response.startswith("```"):
#                 response = response.strip("`").strip()
#                 if response.lower().startswith("json"):
#                     response = response[4:].strip()

#             if not response:
#                 raise ValueError("Empty response from LLM")

#             parsed = json.loads(response)

#             if isinstance(parsed, list):
#                 for j, item in enumerate(parsed):
#                     item["Job_Description"] = batch[j] if j < len(batch) else ""
#                     results.append(item)
#             else:
#                 parsed["Job_Description"] = batch[0]
#                 results.append(parsed)

#         except Exception as e:
#             results.append({
#                 "error": str(e),
#                 "raw_output": response if 'response' in locals() else None
#             })

#     return results

async def analyze_batch(batch, resume_summary, experience, semaphore):
    prompt = combined_prompt_template(batch, resume_summary, experience)

    async with semaphore:
        # Wrap blocking llm.invoke in a thread to avoid blocking event loop
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content.strip()

    # Clean markdown code block if any
    while content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()

    if not content:
        raise ValueError("Empty response from LLM")

    parsed = json.loads(content)

    # Attach job descriptions from batch
    results = []
    if isinstance(parsed, list):
        for j, item in enumerate(parsed):
            item["Job_Description"] = batch[j] if j < len(batch) else ""
            results.append(item)
    else:
        parsed["Job_Description"] = batch[0]
        results.append(parsed)

    return results


async def analyze_posts_batch(post_list, experience, batch_size=5):
    resume_text = extract_text_from_pdf(RESUME_PATH)
    resume_summary = generate_resume_summary(resume_text)

    semaphore = asyncio.Semaphore(4)  # max 3 parallel LLM calls

    batches = [post_list[i : i + batch_size] for i in range(0, len(post_list), batch_size)]

    results = []

    # Await the coroutine to get list of batch results
    batch_results = await tqdm_asyncio.gather(
        *(analyze_batch(batch, resume_summary, experience, semaphore) for batch in batches),
        total=len(batches),
        desc="🧠 LLM Analysis Progress",
        ncols=80,
    )

    # batch_results is a list of lists
    for batch_result in batch_results:
        results.extend(batch_result)

    return results