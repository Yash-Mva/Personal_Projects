
## Requirements
- Python 3.8+
- Free Reddit API credentials from https://www.reddit.com/prefs/apps
- Free Groq API key from https://console.groq.com/keys

## Setup
1. Install dependencies:
    pip install praw python-dotenv requests
2. Create a `.env` file and fill in your credentials.
3. Run the script:
    python reddit_persona_groq.py
4. Enter a Reddit profile URL (e.g., https://www.reddit.com/user/kojied/)
5. Output will be saved as `<username>_persona.txt`