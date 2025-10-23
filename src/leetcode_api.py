import requests
from . import config

def get_daily_question():
    """Fetches the title and link of the daily LeetCode question"""
    try:
        response = requests.post(
            config.LEETCODE_API_URL, 
            json={'query': config.QUERY_DAILY_QUESTION}
        )
        response.raise_for_status()
        q_data = response.json()["data"]["activeDailyCodingChallengeQuestion"]
        q_data['fullLink'] = "https://leetcode.com" + q_data['link']
        return q_data

    except Exception as e:
        print(f"\n Error fetching daily question: {e}")
        return None

def get_recent_submissions(username):
    """Fetches the 50 most recent accepted submissions for a user"""
    try:
        variables = {"username": username, "limit": 50}
        response = requests.post(
            config.LEETCODE_API_URL,
            json={'query': config.QUERY_RECENT_SUBMISSIONS, 'variables': variables}
        )
        response.raise_for_status()
        return response.json()["data"]["recentAcSubmissionList"]
    except Exception as e:
        print(f"\n Error fetching submissions for {username}: {e}")
        return []
