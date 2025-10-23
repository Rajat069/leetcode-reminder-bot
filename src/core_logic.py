import random
from datetime import datetime, timedelta
from . import config
from . import leetcode_api
from halo import Halo
from . import email_service

def run_check():
    """Main logic to check submissions for each user and send emails."""
    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    print(f"\n[{ist_now.strftime('%Y-%m-%d %H:%M:%S')} IST] Starting submission check...")

    daily_slug, question_link = leetcode_api.get_daily_question()
    if not daily_slug:
        print("Aborting check since daily question could not be fetched.")
        return
    
    print(f"Today's POTD is '{daily_slug}'")
    today = ist_now.date()
    
    users = config.load_users()
    if not users:
        print("No users loaded from users.json. Exiting check.")
        return

    for user in users:
        username, email = user["username"], user["email"]
        print(f"\n🔍 Checking user: {username}")
        
        #submissions = leetcode_api.get_recent_submissions(username)
        with Halo(text='Fetching submissions...', spinner='star2', color='cyan') as spinner:
            submissions = leetcode_api.get_recent_submissions(username)
            spinner.succeed('Submissions fetched successfully!')

        solved_today = any(
            sub["titleSlug"] == daily_slug and
            (datetime.fromtimestamp(int(sub["timestamp"])) + timedelta(hours=5, minutes=30)).date() == today
            for sub in submissions
        )

        if solved_today:
            print(f"[ {username} ] has already solved the daily problem.")
            quote = random.choice(config.QUOTES)
            html = email_service.build_html_email(username, daily_slug, question_link, True, quote)
            subject = f"Awesome! You solved today’s LeetCode challenge!"
        else:
            print(f" [ {username} ]has not solved the daily problem yet. Sending reminder.")
            html = email_service.build_html_email(username, daily_slug, question_link, False)
            subject = f"⏳ Reminder: Solve Today’s LeetCode Problem!"

        
        with Halo(text='Sending mail..', spinner='bouncingBar', color='yellow') as spinner:
            try:
                email_service.send_email(email, subject, html)
                spinner.succeed(f"Mail sent successfully! to user {username}")
            except Exception as e:
                spinner.fail(f'Failed to send mail: {e}')

    print("\n--- Check complete ---")
