# import os
# import json
# import pdfplumber
# from azure_llm import llm
# from prompt import combined_prompt_template

# RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")

# import pdfplumber

# def extract_text_from_pdf(file_path):
#     with pdfplumber.open(file_path) as pdf:
#         return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# # 📄 Load text from resume PDF
# def load_resume_text():
#     with pdfplumber.open(RESUME_PATH) as pdf:
#         return " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
# def analyze_posts_batch(post_list, resume_text, experience, batch_size=5):
#     results = []

#     for i in range(0, len(post_list), batch_size):
#         batch = post_list[i:i + batch_size]
#         prompt = combined_prompt_template(batch, resume_text, experience)

#         try:
#             response = llm.invoke(prompt).content.strip()

#             # ✅ Remove markdown-style code blocks (```json ... ```)
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

#             print(f"✅ Processed batch {i // batch_size + 1}")

#         except Exception as e:
#             print(f"❌ Error parsing batch {i // batch_size + 1}: {e}")
#             results.append({
#                 "error": str(e),
#                 "raw_output": response if 'response' in locals() else None
#             })

#     return results

from tqdm import tqdm
import os
import json
import pdfplumber
from azure_llm import llm
from prompt import combined_prompt_template

RESUME_PATH = os.getenv("RESUME_PATH", "anshu_singh_resume.pdf")

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def load_resume_text():
    with pdfplumber.open(RESUME_PATH) as pdf:
        return " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

def analyze_posts_batch(post_list, resume_text, experience, batch_size=5):
    results = []
    num_batches = (len(post_list) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(post_list), batch_size), total=num_batches, desc="🧠 LLM Analysis Progress", ncols=80):
        batch = post_list[i:i + batch_size]
        prompt = combined_prompt_template(batch, resume_text, experience)

        try:
            response = llm.invoke(prompt).content.strip()

            # ✅ Clean up markdown-style blocks
            while response.startswith("```"):
                response = response.strip("`").strip()
                if response.lower().startswith("json"):
                    response = response[4:].strip()

            if not response:
                raise ValueError("Empty response from LLM")

            parsed = json.loads(response)

            if isinstance(parsed, list):
                for j, item in enumerate(parsed):
                    item["Job_Description"] = batch[j] if j < len(batch) else ""
                    results.append(item)
            else:
                parsed["Job_Description"] = batch[0]
                results.append(parsed)

        except Exception as e:
            results.append({
                "error": str(e),
                "raw_output": response if 'response' in locals() else None
            })

    return results
