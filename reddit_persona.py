
import os
import re
import requests
import praw
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def extract_username(profile_url):
    match = re.search(r'reddit\.com/user/([^/]+)/?', profile_url)
    return match.group(1) if match else None

def fetch_user_data(username, limit=50):
    user = reddit.redditor(username)
    comments = [f"[COMMENT] {c.body}" for c in user.comments.new(limit=limit)]
    posts = [f"[POST] {s.title}\n{s.selftext}" for s in user.submissions.new(limit=limit)]
    return comments[:20], posts[:20]

def build_prompt(posts, comments):
    combined = "\n".join(posts + comments)
    return f"""
You are a behavioral analyst. Create a detailed Reddit User Persona based on the content below. Include:
- Fictional Name
- Age Range
- Likely Occupation
- Interests & Hobbies
- Political/Religious hints (if any)
- Tone and Language Style
- Online Behavior
- Personality Traits
- Values and Beliefs

For each trait, include a quote from a post or comment to justify it.

Reddit Content:
{combined}
"""

def call_groq_mixtral(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemma2-9b-it",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        raise Exception(f"Groq API Error: {res.status_code} - {res.text}")
    
    return res.json()["choices"][0]["message"]["content"].strip()

def save_persona(username, text):
    filename = f"{username}_persona.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Persona saved to: {filename}")

def main():
    profile_url = input("Enter Reddit profile URL: ")
    username = extract_username(profile_url)
    if not username:
        print(" Invalid URL.")
        return
    
    print(f"🔍 Fetching data for u/{username}...")
    comments, posts = fetch_user_data(username)

    if not (comments or posts):
        print("No content found.")
        return

    print("🧠 Generating persona with Mixtral via Groq...")
    prompt = build_prompt(posts, comments)
    persona = call_groq_mixtral(prompt)

    save_persona(username, persona)

if __name__ == "__main__":
    main()
