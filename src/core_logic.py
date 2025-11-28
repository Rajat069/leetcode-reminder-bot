import random
from datetime import datetime, timedelta
from . import config
from . import leetcode_api
from halo import Halo
from . import email_service
from . import gemini_service 
import requests
from pytz import timezone


def get_hint_count(difficulty, acRate):
    """
    Calculates the number of hints to show based on your logic.
    """
    acRate = float(acRate) 
    
    if difficulty == "Easy":
        return 1 if acRate >= 60 else 2
    elif difficulty == "Medium":
        return 2 if acRate >= 55 else 3
    elif difficulty == "Hard":
        return 3 if acRate >= 40 else 4
    
    return 2 # Default fallback


def run_check():
    """Main logic to check submissions for each user and send emails."""
    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    print(f"\n[{ist_now.strftime('%Y-%m-%d %I:%M:%S %p %a')} IST] Starting submission check...")

    # Get all question data
    question_data = leetcode_api.get_daily_question()
    if not question_data:
        print("Aborting check since daily question could not be fetched.")
        return
    
    q_details = question_data['question']
    q_link = question_data['fullLink']

    print(f"Today's POTD is '{q_details['title']}' ({q_details['difficulty']})")
    today = ist_now.date()
    
    users = config.load_users()
    if not users:
        print("No users loaded from users.json. Exiting check.")
        return

     # Get one AI quote for everyone for this run
    with Halo(text='Fetching quote from gemini...', spinner='balloon2', color='cyan') as spinner:
        try:
            ai_quote = gemini_service.get_motivational_quote()
            spinner.succeed('Quote fetched successfully!')
        except Exception as e:
            spinner.fail(f'Failed to get motivational quote: {e}')   

    ai_hints = [] 
  
    for user in users:
        try:
            result = check_single_user(user, q_details, q_link, today, ai_quote, ai_hints)
            print(f" [ {user['username']} ] Result: {result}")
        except Exception as e:
            print(f" [ {user['username']} ] Error during check: {e}")
    print("\n--- Check complete ---")

def update_status(user_id, status):
    """Sends a PATCH request to update user status."""
    if not config.USER_SERVICE_URL or not config.USER_SERVICE_API_KEY:
        return

    url = f"{config.USER_SERVICE_URL}/{user_id}/status"
    headers = {
        "X-API-Key": config.USER_SERVICE_API_KEY,
        "Content-Type": "application/json"
    }
    
    now_iso = datetime.utcnow().isoformat()
    
    payload = {
        "status": status,
        "lastChecked": now_iso
    }
    
    try:
        requests.patch(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        print(f"Failed to update status for {user_id}: {e}")

def check_single_user(user, q_details, q_link, today, ai_quote, ai_hints):
    """Checks a single user and sends email if needed. Returns status message."""
    username, email = user["username"], user["email"]
    print(f"\n🔍 Checking user: {username}")

    new_status = "pending"
    
    with Halo(text='Fetching submissions...', spinner='star2', color='cyan') as spinner:
            submissions = leetcode_api.get_recent_submissions(username)
            spinner.succeed('Submissions fetched successfully!')

    solved_today = any(
        sub["titleSlug"] == q_details["titleSlug"] and
        (datetime.fromtimestamp(int(sub["timestamp"])) + timedelta(hours=5, minutes=30)).date() == today
        for sub in submissions
    )
    
    if solved_today:
        print(f"[ {username} ] has already solved the daily problem.")
        subject = "Awesome! You solved today’s LeetCode challenge!"
        new_status = "solved"
        result_msg = "solved"
    else:
        print(f" [ {username} ] has not solved the daily problem yet sending reminder...")
        subject = "⏳ Reminder: Solve Today’s LeetCode Problem!"
        new_status = "pending"
        result_msg = "reminded"
        if len(ai_hints) == 0:
                    hint_count = get_hint_count(q_details['difficulty'], q_details['acRate'])
                    with Halo(text='Generating Hints...', spinner='arrow3', color='blue') as spinner:
                        try:
                            ai_hints = gemini_service.generate_optimal_hints(q_details, hint_count)
                            spinner.succeed('Hints generated successfully!')
                        except Exception as e:
                            spinner.fail(f'Failed to generate hints: {e}')
                            ai_hints = gemini_service.DEFAULT_HINTS        

    
    html = email_service.build_html_email(
        username=username,
        title=q_details['title'],
        difficulty=q_details['difficulty'], 
        link=q_link,
        solved=solved_today,
        quote=ai_quote,
        hints=ai_hints,
    )
    
    update_status(username, new_status)
    
    with Halo(text='Sending mail..', spinner='bouncingBar', color='yellow') as spinner:
            try:
                email_service.send_email(email, subject, html)
                spinner.succeed(f"Mail sent successfully! to user {username}")
            except Exception as e:
                spinner.fail(f'Failed to send mail: {e}')

    return result_msg

def check_single_user_on_demand(username, email):
    """
    Standalone function to check one user, fetching fresh Daily Question data.
    Returns a dict with the outcome (e.g., 'solved', 'reminded', 'error').
    """
    #Fetch Fresh Daily Question (Important for manual refresh!)
    question_data = leetcode_api.get_daily_question()
    if not question_data:
        raise Exception("Could not fetch daily question")
        
    q_details = question_data['question']
    q_link = question_data['fullLink']
    
    ai_quote = gemini_service.get_motivational_quote() # Or cache this
    ai_hints = gemini_service.DEFAULT_HINTS 

    result_msg = check_single_user(
        {"username": username, "email": email, "id": None},
        q_details, q_link, datetime.utcnow().date(), ai_quote, ai_hints
    )
    
    return {"message": result_msg}