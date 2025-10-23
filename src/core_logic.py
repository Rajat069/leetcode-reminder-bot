import random
from datetime import datetime, timedelta
from . import config
from . import leetcode_api
from halo import Halo
from . import email_service
from . import gemini_service 


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
    print(f"\n[{ist_now.strftime('%Y-%m-%d %H:%M:%S')} IST] Starting submission check...")

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
    with Halo(text='Fetching quote from gemini...', spinner='earth', color='cyan') as spinner:
        try:
            ai_quote = gemini_service.get_motivational_quote()
            spinner.succeed('Quote fetched successfully!')
        except Exception as e:
            spinner.fail(f'Failed to get motivational quote: {e}')   
   
  
    for user in users:
        username, email = user["username"], user["email"]
        print(f"\n🔍 Checking user: {username}")
        
        with Halo(text='Fetching submissions...', spinner='star2', color='cyan') as spinner:
            submissions = leetcode_api.get_recent_submissions(username)
            spinner.succeed('Submissions fetched successfully!')

        solved_today = any(
            sub["titleSlug"] == q_details["titleSlug"] and
            (datetime.fromtimestamp(int(sub["timestamp"])) + timedelta(hours=5, minutes=30)).date() == today
            for sub in submissions
        )

        ai_hints = []

        if solved_today:
            print(f"[ {username} ] has already solved the daily problem.")
            subject = f"Awesome! You solved today’s LeetCode challenge!"
        else:
            print(f" [ {username} ] has not solved the daily problem yet sending reminder...")
            subject = f"⏳ Reminder: Solve Today’s LeetCode Problem!"

            hint_count = get_hint_count(q_details['difficulty'], q_details['acRate'])
            print(f"Difficulty: {q_details['difficulty']}, AC Rate: {format(float(q_details['acRate']), '.2f')}% -> Generating {hint_count} hints.")
           
            with Halo(text='Calling Gemini...', spinner='arrow3', color='blue') as spinner:
                ai_hints = gemini_service.generate_optimal_hints(q_details, hint_count)
            spinner.succeed('Hints generated successfully!')
            

        #  Send email
        html = email_service.build_html_email(
            username=username,
            title=q_details['title'],
            link=q_link,
            solved=solved_today,
            quote=ai_quote,
            hints=ai_hints 
        )
        
        with Halo(text='Sending mail..', spinner='bouncingBar', color='yellow') as spinner:
            try:
                email_service.send_email(email, subject, html)
                spinner.succeed(f"Mail sent successfully! to user {username}")
            except Exception as e:
                spinner.fail(f'Failed to send mail: {e}')

    print("\n--- Check complete ---")
