# keywords_config.py

KEYWORD_GROUPS = {
    "Languages": ["Java Developer", "Python Developer"],
    "Frameworks": ["Spring Boot Developer"],
    "Roles": [
        "Backend Developer", "Backend Engineer", "Software Engineer", "Software Developer", 
        "Full Stack Developer", "Data Engineer", "Data Scientist", "Machine Learning Engineer", 
        "AI Engineer", "SDE", "SDE 1", "SDE 2", "Graduate Engineer Trainee", "Associate Software Engineer", 
        "Junior Developer", "Trainee Developer", "API Developer", "Cloud Engineer", "DevOps Engineer","React Developer"
    ],
    "Hiring Cues": [
        "We are hiring", "Hiring now", "Immediate joiner", "Looking for developer", "Job opening", 
        "Walk-in interview", "Hiring fresher", "Hiring software engineer", "Urgent requirement", 
        "Open positions", "Now hiring backend"
    ]
}

# Flattened list of all keywords
ALL_KEYWORDS = [kw for group in KEYWORD_GROUPS.values() for kw in group]
