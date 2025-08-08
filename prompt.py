# def combined_prompt_template(posts: list[str], resume_text: str, experience: int):
#     return f"""
# You are a helpful assistant that processes LinkedIn job posts.

# The candidate has {experience} years of experience.  
# Resume:
# \"\"\"{resume_text[:1500]}\"\"\"

# For each post below, return a JSON object with:
# {{
#   "Post_Index": 1,
#   "Is_Job_Post": true,
#   "Role": "...",
#   "Company": "...",
#   "Apply_Link": "...",
#   "Contact_Email": "...",
#   "Eligibility": "Eligible"  // or "Not Eligible"
# }}

# Rules:
# - If the post is not a job post, set `"Is_Job_Post": false` and skip other fields.
# - Use `"Not Provided"` for missing Role/Company/Link/Email.
# - Combine multiple links if present.
# - Use only "Eligible" or "Not Eligible" in Eligibility.
# - Output must be a list of JSON objects, one per post.

# ---
# Posts:
# {chr(10).join([f"{i+1}. {p}" for i, p in enumerate(posts)])}
# """
# def email_prompt_template(post_text, resume_text):
#     return f"""
# You are a helpful assistant that writes short, friendly, and professional job application emails that sound like they were written by a human.

# 🔹 Objective:
# Write a warm and natural email to apply for the job described below.

# 🔹 Job Post:
# \"\"\"{post_text}\"\"\"

# 🔹 Candidate Resume:
# \"\"\"{resume_text[:1500]}\"\"\"

# 🔹 Email Writing Instructions:
# - Start with a polite greeting. If a recruiter or contact name is clearly mentioned (e.g., "Priyanka", "John"), use it like "Hi Priyanka,". Otherwise, just use "Hi,".
# - Mention the job role and company (if available).
# - Briefly highlight 1–2 relevant skills or achievements that match the post.
# - Mention that the resume is attached.
# - Keep the tone professional yet conversational — as if a real person wrote it.
# - Avoid contractions like "I'm", "I've", etc.
# - Keep it concise (5–7 sentences), polite, and easy to read.
# - End with a professional closing and include your full name, phone number, and email.

# 🔹 Example Email:

# Subject: Application for Java Developer Role – TechnoVal Alliance

# Hi Priyanka,

# I hope you are doing well. I came across the Java Developer opening at TechnoVal Alliance and would like to express my interest in the role.

# I have hands-on experience in Java, Spring Boot, and developing scalable RESTful APIs. I have also worked with Azure integrations and API authentication (OAuth 2.0), which aligns closely with the job requirements.

# My resume is attached for your review. I would appreciate the opportunity to discuss how my skills can contribute to your team’s goals.

# Looking forward to hearing from you.

# Best regards,  
# Anshu Singh  
# 📞 +91 7388138814  
# 📧 anshukit2011@gmail.com

# ---
# Now, write a similar email for the job post and resume above.
# """


# prompt.py

# def combined_prompt_template(posts: list[str], resume_summary: str, experience: int):
#     return f"""
# You are a helpful assistant that processes LinkedIn job posts.

# The candidate has {experience} years of experience.  
# Resume Summary:
# \"\"\"{resume_summary}\"\"\"  # Summarized resume, not full raw text.

# For each post below, return a JSON object with:
# {{
#   "Post_Index": 1,
#   "Is_Job_Post": true,
#   "Role": "...",
#   "Company": "...",
#   "Apply_Link": "...",
#   "Contact_Email": "...",
#   "Eligibility": "Eligible"  // or "Not Eligible"
# }}

# Rules:
# - If the post is not a job post, set `"Is_Job_Post": false` and skip other fields.
# - Use `"Not Provided"` for missing Role/Company/Link/Email.
# - Combine multiple links if present.
# - Use only "Eligible" or "Not Eligible" in Eligibility.
# - Output must be a list of JSON objects, one per post.

# ---
# Posts:
# {chr(10).join([f"{i+1}. {p}" for i, p in enumerate(posts)])}
# """

# def combined_prompt_template(posts: list[str], resume_summary: str, experience: int):
#     return f"""
# You are an expert job-matching assistant. Your task is to analyze LinkedIn job posts and determine their relevance and eligibility based on the candidate's experience and resume summary.
# Candidate Profile:
# - Total Experience: {experience} years
# - Resume Summary:
# \"\"\"
# {resume_summary}
# \"\"\"

# Instructions:
# For each job post below, return a JSON object with the following fields:
# {{
#   "Post_Index": 1,                       # Index of the post in the list
#   "Is_Job_Post": true,                   # Set to false if it's not a real job post (e.g., meme, quote, general post)
#   "Role": "Software Engineer",           # Role being hired for (or "Not Provided" if missing)
#   "Company": "Google",                   # Company name (or "Not Provided" if missing)
#   "Apply_Link": "https://...",           # Direct apply or job post link (combine multiple if found, else "Not Provided")
#   "Contact_Email": "hr@example.com",     # Contact or recruiter email (or "Not Provided")
#   "Eligibility": "Eligible"              # "Eligible" if job seems relevant to resume, else "Not Eligible"
# }}
# Eligibility Criteria:
# - Match based on skills, technologies, role, and domain mentioned in the resume summary.
# - Consider seniority level based on experience (e.g., 1.5 years = junior, 4+ years = mid-level).
# - Do not guess — only mark "Eligible" if clearly aligned with the candidate’s experience and skills.
# - Mark as "Not Eligible" if unclear or irrelevant.
# Rules:
# - If the post is not a real job post, set `"Is_Job_Post": false` and ignore other fields.
# - Use "Not Provided" if Role, Company, Link, or Email is missing.
# - Keep the response strictly as a JSON list of objects.
# ---
# Posts:
# {chr(10).join([f"{i+1}. {p}" for i, p in enumerate(posts)])}
# """

def combined_prompt_template(posts: list[str], resume_summary: str, experience: int):

    return f"""
You are an expert job-matching assistant. Your task is to analyze LinkedIn job posts and determine their relevance and eligibility based on the candidate's profile.

Candidate Profile:
- Total Experience: {experience} years
- Resume Summary:
\"\"\"  
{resume_summary}  
\"\"\"

Instructions:
For each job post, return a JSON object with the following fields:
{{
  "Post_Index": int,                    # Index of the post (1-based)
  "Is_Job_Post": bool,                  # False if not a real job post (e.g., meme, quote)
  "Role": str,                          # Job title (or "Not Provided")
  "Company": str,                       # Company name (or "Not Provided")
  "Apply_Link": str,                    # Direct application link (or "Not Provided")
  "Contact_Email": str,                 # Recruiter contact email (or "Not Provided")
  "Eligibility": str                    # "Eligible" or "Not Eligible"
}}

### Experience Handling:
- Use the candidate’s total experience: **{experience} years**.
- If a job post explicitly lists experience (e.g., "5+ years", "3–6 years"), extract the **maximum value** and compare.
- If vague language is used, estimate as follows:
  - "Senior" → 5+ years
  - "Mid-level" → 3–5 years
  - "Junior" or "Entry-level" → 0–2 years
- A job is **"Not Eligible"** if the required experience exceeds the candidate's by more than 1 year.
- If no experience is mentioned, make a reasonable guess based on job title and wording.
- Internships are always "Not Eligible".

### Eligibility Criteria:
- A job is "Eligible" **only if** all of the following are true:
  - The post is a genuine job post (not a meme, general post, or advertisement).
  - The role matches one of the candidate’s **Suggested_Roles** from the resume summary.
  - The job description includes skills or technologies mentioned in the resume summary.
  - The experience requirement (if mentioned or estimated) is valid as per **Experience Handling**.

### A post is "Not Eligible" if:
- The domain or role clearly doesn’t match the candidate’s Suggested_Roles (e.g., UI/UX, Frontend-only, Testing).
- The post lacks a concrete job description or relevant technical content.
- The job is explicitly an internship.

### Rules:
- If the post is not a real job post, set `"Is_Job_Post": false` and leave other fields as "Not Provided".
- Use "Not Provided" if any field (Role, Company, Link, or Email) is missing.
- Output must be a valid JSON list of objects (one per job post) without extra explanation.

---
Posts:
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(posts)])}
"""

def email_prompt_template(post_text, resume_summary):
    return f"""
You are a helpful assistant that writes short, friendly, and professional job application emails that sound like they were written by a human.

🔹 Objective:
Write a warm and natural email to apply for the job described below.

🔹 Job Post:
\"\"\"{post_text}\"\"\" 

🔹 Candidate Resume Summary:
\"\"\"{resume_summary}\"\"\" 

🔹 Email Writing Instructions:
- Start with a polite greeting. If a recruiter or contact name is clearly mentioned (e.g., "Priyanka", "John"), use it like "Hi Priyanka,". Otherwise, just use "Hi,".
- Mention the job role and company (if available).
- Briefly highlight 1–2 relevant skills or achievements that match the post.
- Mention that the resume is attached.
- Keep the tone professional yet conversational — as if a real person wrote it.
- Avoid contractions like "I'm", "I've", etc.
- Keep it concise (5–7 sentences), polite, and easy to read.
- End with a professional closing and include your full name, phone number, and email.

🔹 Example Email:

Subject: Application for Java Developer Role – TechnoVal Alliance

Hi Priyanka,

I hope you are doing well. I came across the Java Developer opening at TechnoVal Alliance and would like to express my interest in the role.

I have hands-on experience in Java, Spring Boot, and developing scalable RESTful APIs. I have also worked with Azure integrations and API authentication (OAuth 2.0), which aligns closely with the job requirements.

My resume is attached for your review. I would appreciate the opportunity to discuss how my skills can contribute to your team’s goals.

Looking forward to hearing from you.

Best regards,  
Anshu Singh  
📞 +91 7388138814  
📧 anshukit2011@gmail.com

---
Now, write a similar email for the job post and resume above.
"""


# def resume_summary_prompt_template(resume_text: str):
#     return f"""
# You are an expert resume parser.

# Analyze the following resume content and generate a structured JSON summary with these fields:

# - Full_Name
# - Email
# - Phone
# - Location
# - Years_of_Experience (best estimate from content)
# - Education (short summary)
# - Skills (as a list of unique skills)
# - Technical_Expertise (brief description of technical strengths)
# - Work_Experience (short summary including roles and durations)
# - Projects (short summary if mentioned)
# - Notable_Achievements (awards, recognitions, performance highlights)

# Resume Content:
# \"\"\"
# {resume_text}
# \"\"\"

# Respond only in valid JSON format without commentary or explanation.
# """

# def resume_summary_prompt_template(resume_text: str):
#     return f"""
# You are an expert resume parser and job role inference assistant.

# Analyze the resume below and generate a structured JSON with fields listed in **exact order**. Pay special attention to the candidate's strongest and most relevant skills and experiences.

# ### Fields (in this exact order):

# - Suggested_Roles: List of likely job roles, **prioritized by strength of alignment** with the resume.  
#   Focus on core technologies, experience depth, and project exposure.  
#   Example: If Java and Spring Boot are used heavily, suggest roles like ["Java Developer", "Backend Engineer"].  
#   Include frontend roles like "Frontend Developer" **only if frontend skills are prominently featured**.

# - Full_Name
# - Email
# - Phone
# - Location
# - Years_of_Experience (best estimate from resume)
# - Education (short summary)
# - Skills (list of unique technical tools and languages)
# - Technical_Expertise (brief summary of core strengths)
# - Work_Experience (roles, companies, durations)
# - Projects (short summary if mentioned)
# - Notable_Achievements (awards, recognitions, performance highlights)

# Resume Content:
# \"\"\"
# {resume_text}
# \"\"\"

# Respond **only** with a valid JSON object in the above order. Do not include any explanation or comments.
# """

def resume_summary_prompt_template(resume_text: str):
    return f"""
You are an expert resume parser and job role inference assistant.

Analyze the resume below and generate a structured JSON with fields listed in **exact order**. Pay special attention to the candidate's strongest and most relevant skills and experiences.

### Fields (in this exact order):

- Suggested_Roles: List of likely job roles, **prioritized by strength of alignment** with the resume.  
  Focus on core technologies, experience depth, and project exposure.  
  Example: If Java and Spring Boot are used heavily, suggest roles like ["Java Developer", "Backend Engineer"].  
  Include frontend roles like "Frontend Developer" **only if frontend skills are prominently featured**.

- Full_Name  
- Email  
- Phone  
- Location  
- Education (short summary)  
- Skills (list of unique technical tools and languages)  
- Technical_Expertise (brief summary of core strengths)  
- Work_Experience (roles, companies, durations)  
- Projects (short summary if mentioned)  
- Notable_Achievements (awards, recognitions, performance highlights)

Resume Content:
\"\"\"  
{resume_text}  
\"\"\"

Respond **only** with a valid JSON object in the above order. Do not include any explanation or comments.
"""
