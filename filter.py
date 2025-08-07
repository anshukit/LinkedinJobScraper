import re

def is_valid_email(email):
    return email and email != "Not Provided" and re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_apply_link(link):
    return link and link != "Not Provided" and link.startswith("http")

def filter_eligible_posts(processed_posts):
    eligible = []
    mail_list = []
    apply_list = []

    for post in processed_posts:
        if post.get("Eligibility") != "Eligible":
            continue
        if not post.get("Is_Job_Post", False):
            continue

        eligible.append(post)

        email = post.get("Contact_Email", "").strip()
        link = post.get("Apply_Link", "").strip()

        if is_valid_email(email):
            mail_list.append(post)
        elif is_valid_apply_link(link):
            apply_list.append(post)

    return eligible, mail_list, apply_list
