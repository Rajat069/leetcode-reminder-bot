import os
import json
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# This is great for local development.
# On VM, we will set these variables directly.
load_dotenv()

# --- Load Environment Variables ---
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
LEETCODE_API_URL = os.getenv("LEETCODE_API_URL", "https://leetcode.com/graphql")

# --- Static Config (App-level constants) ---
QUOTES = [
    "Keep pushing! You’re closer than you think 💪",
    "Consistency beats motivation every time ⚡",
    "Another problem solved — another step ahead 🚀",
    "Your hard work today is your success tomorrow 💫",
    "One problem a day keeps the bugs away 🧠"
]

# --- GraphQL Queries ---
QUERY_DAILY_QUESTION = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      title
      titleSlug
      difficulty
      hints
      topicTags{
        name
      }
    }
  }
}
"""

QUERY_RECENT_SUBMISSIONS = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    titleSlug
    timestamp
  }
}
"""

# --- Helper Functions ---

def load_users():
    """Loads the user list from users.json."""
    users_filepath = 'users.json' # place users.json in the root
    if not os.path.exists(users_filepath):
        # local testing
        users_filepath = os.path.join(os.path.dirname(__file__), '..', 'users.json')

    try:
        with open(users_filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(" users.json file not found at {users_filepath}.")
        return []
    except json.JSONDecodeError:
        print(f" Error: {users_filepath} is not valid JSON.")
        return []

def validate_config():
    """Checks if essential secrets are loaded."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(" FATAL ERROR: SMTP_USER or GMAIL_APP_PASSWORD is not set.")
        print("  Please set these environment variables before running.")
        print("  If running locally, check your .env file.")
        return False
    
    print("Configuration and secrets loaded successfully.")
    return True

