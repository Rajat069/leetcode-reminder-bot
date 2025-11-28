import requests
from . import config
from cachetools import TTLCache, cached
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import time

cache = TTLCache(maxsize=1, ttl=24*60*15)

def get_daily_question():
    """Fetches the title and link of the daily LeetCode question"""
    try:
        cached_result = cache.get('daily_question')
        if cached_result:
            print("Fetched daily question from cache.")
            return cached_result
        
        response = requests.post(
            config.LEETCODE_API_URL, 
            json={'query': config.QUERY_DAILY_QUESTION}
        )
        response.raise_for_status()
        q_data = response.json()["data"]["activeDailyCodingChallengeQuestion"]
        q_data['fullLink'] = "https://leetcode.com" + q_data['link']

        cache['daily_question'] = q_data
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
        #print("DEBUG: recent submissions response =", response.json()["data"]["recentAcSubmissionList"][0])
        return response.json()["data"]["recentAcSubmissionList"]
    except Exception as e:
        print(f"\n Error fetching submissions for {username}: {e}")
        return []

def evict_cache():
    """Evicts all cached data"""
    cache.expire() 
    print("Cache eviction run at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

def setup_cache_eviction():
    """Sets up the cache eviction scheduler to run at 5:00 AM PST"""
    scheduler = BackgroundScheduler(timezone=timezone('US/Pacific'))
    scheduler.add_job(evict_cache, 'cron', hour=5, minute=0)
    scheduler.start()
    return scheduler