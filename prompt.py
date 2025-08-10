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



def email_prompt_template(post_text, resume_summary_json):
    return f"""
You are a helpful assistant that writes short, friendly, and professional cold emails to apply for jobs.

Job Post:
\"\"\"{post_text}\"\"\"

Candidate Resume Summary (JSON):
\"\"\"{resume_summary_json}\"\"\"

Instructions:
- Calculate total years of experience from the Work_Experience durations.
- Mention experience briefly (rounded up) only if the job requires ≤ 2 years of experience; otherwise, focus on skills and relevant achievements.
- Use Suggested_Roles and Skills to pick 1-2 relevant skills or accomplishments to highlight.
- Start with a greeting using the recruiter's name if available, else "Hi,".
- Mention the job role and company if possible.
- Write a short, polite, and professional email (3-5 sentences).
- Avoid contractions like "I'm", "I've".
- Ensure the email sounds genuine, natural, and true—not overly formal or robotic.
- End with a courteous closing including Full_Name and Phone only.

Example:

Subject: Application for Java Backend Developer Role

Hi Priyanka,

I am writing to express my interest in the Java Backend Developer role at TechnoVal Alliance. I have 2 years of experience in Java and Spring Boot, with expertise in building scalable microservices.

I would welcome the opportunity to discuss how I can contribute to your team.

Best regards,  
Anshu Singh  
+91 7388138814

---
Now, write a similar email for the job post and resume above.
"""


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
