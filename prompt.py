def combined_prompt_template(posts: list[str], resume_text: str, experience: int):
    return f"""
You are a helpful assistant that processes LinkedIn job posts.

The candidate has {experience} years of experience.  
Resume:
\"\"\"{resume_text[:1500]}\"\"\"

For each post below, return a JSON object with:
{{
  "Post_Index": 1,
  "Is_Job_Post": true,
  "Role": "...",
  "Company": "...",
  "Apply_Link": "...",
  "Contact_Email": "...",
  "Eligibility": "Eligible"  // or "Not Eligible"
}}

Rules:
- If the post is not a job post, set `"Is_Job_Post": false` and skip other fields.
- Use `"Not Provided"` for missing Role/Company/Link/Email.
- Combine multiple links if present.
- Use only "Eligible" or "Not Eligible" in Eligibility.
- Output must be a list of JSON objects, one per post.

---
Posts:
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(posts)])}
"""
def email_prompt_template(post_text, resume_text):
    return f"""
You are a helpful assistant that writes short, friendly, and professional job application emails that sound like they were written by a human.

🔹 Objective:
Write a warm and natural email to apply for the job described below.

🔹 Job Post:
\"\"\"{post_text}\"\"\"

🔹 Candidate Resume:
\"\"\"{resume_text[:1500]}\"\"\"

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


# def email_prompt_template(post_text, resume_text):
#     return f"""
# You are a helpful assistant that writes short and friendly job application emails.

# 🔹 Goal: Write a concise and conversational email to apply for the following job.

# 🔹 Job Post:
# \"\"\"{post_text}\"\"\"

# 🔹 Candidate Resume:
# \"\"\"{resume_text[:1500]}\"\"\"

# 🔹 Instructions:
# - Start with a warm greeting using the recipient’s name if available.
# - Mention the role and company if identified in the job post.
# - Highlight 1–2 relevant skills or experiences that match the post.
# - Mention that the resume is attached.
# - End with a polite and professional closing including name, phone number, and email.
# - Do **not** use contractions like "I’ve", "I’m", etc.

# 🔹 Style Guide Example:

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
# Now, generate a similar email using the given job post and resume.
# """

def eligibility_prompt_template(post_text, resume_text, candidate_experience):
    return f"""
You are an intelligent job eligibility evaluator.

The candidate has **{candidate_experience} years of experience**.

Evaluate whether the candidate is eligible for the given job post by analyzing skill match, responsibilities, and experience.

---
📌 ELIGIBILITY RULES:
1. If **experience is mentioned** in the job post, ensure the candidate meets or exceeds it.
2. If **experience is not mentioned**, decide based only on skill and role relevance.
3. Match relevant **skills, technologies, and responsibilities** between the job post and the resume.

---
✅ Output Format:
Return only one of the following, **without explanation**:
- Eligible  
- Not Eligible

---
📄 Job Post:
\"\"\"{post_text}\"\"\"

📄 Resume:
\"\"\"{resume_text}\"\"\"
"""
