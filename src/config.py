import os
from dotenv import load_dotenv
import requests

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- New Variables for Microservice ---
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8081/api/users")
USER_SERVICE_API_KEY = os.getenv("USER_SERVICE_API_KEY")

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
      acRate
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

def load_users():
    """
    Loads the user list from the Java User-Management Microservice.
    """
    if not USER_SERVICE_API_KEY:
        print(" [WARNING] USER_SERVICE_API_KEY is not set. Cannot fetch users.")
        return []

    headers = {
        "X-API-Key": USER_SERVICE_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        print(f" Fetching users from: {USER_SERVICE_URL}")
        response = requests.get(USER_SERVICE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        api_users = response.json()
        
        # Map Java DTO (leetcodeUsername) to Python Bot expected keys (username)
        # The bot expects a list of dicts: [{'username': '...', 'email': '...'}, ...]
        bot_users = [
            {
                "id": user.get("id"),
                "username": user.get("leetcodeUsername"),
                "email": user.get("email"),
                "reminderTimes": user.get("reminderTimes", [])
            }
            for user in api_users
            if user.get("status") != "paused" # Optional: filter out paused users
        ]
        
        print(f" Successfully loaded {len(bot_users)} users from API.")
        return bot_users

    except requests.exceptions.RequestException as e:
        print(f" Error fetching users from API: {e}")
        return []

def validate_config():
    """Checks if essential secrets are loaded."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(" FATAL ERROR: SMTP_USER or GMAIL_APP_PASSWORD is not set.")
        return False
    
    if not USER_SERVICE_API_KEY:
        print(" FATAL ERROR: USER_SERVICE_API_KEY is not set.")
        return False

    print("Configuration and secrets loaded successfully.")
    return True
