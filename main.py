import schedule
import time
import sys
import threading
import itertools
from src.core_logic import run_check
from src.config import validate_config, load_users
from tqdm import tqdm
import time
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from src.leetcode_api import setup_cache_eviction
import uvicorn
from src.bot_api import app
import threading

spinner_running = True
spinner_cycle = itertools.cycle(['-', '\\', '|', '/'])
scheduled_user_times = {}  # Track scheduled times per user for comparison

def spinner_thread():
    """A simple thread to show a spinning cursor in the console."""
    while spinner_running:
        sys.stdout.write(next(spinner_cycle) + '\r')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(' \r')
    sys.stdout.flush()

def schedule_jobs():
    """Sets up per-user scheduled times from the database."""
    global scheduled_user_times
    users = load_users()
    
    if not users:
        print(" No users found. No jobs scheduled.")
        return
    
    unique_times = set()
    new_scheduled_times = {}
    
    for user in users:
        reminder_times = user.get("reminderTimes", [])
        user_id = user['id']
        
        if not reminder_times:
            print(f"⏭️  User {user['username']} has no reminder times configured.")
            new_scheduled_times[user_id] = []
            continue
        
        new_scheduled_times[user_id] = reminder_times
        
        for time_str in reminder_times:
            unique_times.add(time_str)
            # Schedule job for this time (job will handle filtering by user)
            schedule.every().day.at(time_str).do(run_check, user_id=user_id)
    
    scheduled_user_times = new_scheduled_times
    print(f"⏰ Scheduling jobs at the following UTC times: {', '.join(sorted(unique_times))}")
    print(f"📊 Total jobs scheduled: {len(schedule.jobs)}")

def reload_jobs_if_changed():
    """Check if any user's reminder times have changed and reload jobs if needed."""
    global scheduled_user_times
    users = load_users()
    
    if not users:
        return
    
    needs_reload = False
    
    for user in users:
        user_id = user['id']
        current_times = set(user.get("reminderTimes", []))
        previous_times = set(scheduled_user_times.get(user_id, []))
        
        if current_times != previous_times:
            print(f"🔄 Reminder times changed for user {user['username']}")
            needs_reload = True
            break
    
    if needs_reload:
        print("🔄 Reloading scheduler with updated times...")
        schedule.clear()  # Clear all existing jobs
        schedule_jobs()   # Reschedule with new times
    else:
        print("✅ No timing changes detected.")

def run_scheduler():
    """Main function to start the bot."""
    global spinner_running
    console = Console()
    
    # startup banner
    console.print(Panel.fit(
        "[bold yellow]LeetCode Reminder Bot[/bold yellow]\n\n"
        "[blue]     Version 1.0[/blue]",
        title="🤖 Welcome",
        border_style="green",
        padding=(1, 5)
    ))
    
    # Initialize cache eviction scheduler
    cache_scheduler = setup_cache_eviction()

    with tqdm(total=100, 
                desc="Initializing system",
                colour='cyan',
                ncols=75,
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}') as pbar:
            for i in range(10):
                time.sleep(0.1)
                pbar.update(10)

    if not validate_config():
        sys.exit(1) # Exit if secrets aren't set

    # Run one check immediately on startup
    try:
        run_check()
    except Exception as e:
        print(f"\nAn error occurred during the initial run: {e}")

    schedule_jobs()
    
    schedule.every(30).minutes.do(reload_jobs_if_changed)
    
    print("\n  Scheduler is now running. Waiting for the next scheduled time...")
    print("   (Running as a service. Press Ctrl+C to exit if running locally.)")

    t = threading.Thread(target=spinner_thread)
    t.start()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n")
        rprint(Panel.fit(
            "[bold yellow]Shutting down the bot[/bold yellow]\nSending mail to admin",
            title=" Goodbye! :(",
            border_style="cyan",
            padding=(1, 4)
        ))
        spinner_running = False
        t.join()

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    print("🚀 Starting Bot API Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
