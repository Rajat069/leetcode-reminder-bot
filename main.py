import schedule
import time
import sys
import threading
import itertools
from src.core_logic import run_check
from src.config import validate_config
from tqdm import tqdm
import time
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

spinner_running = True
spinner_cycle = itertools.cycle(['-', '\\', '|', '/'])

def spinner_thread():
    """A simple thread to show a spinning cursor in the console."""
    while spinner_running:
        sys.stdout.write(next(spinner_cycle) + '\r')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(' \r')
    sys.stdout.flush()

def schedule_jobs():
    """Sets up the scheduled times for the submission check."""
    # Note: These times are UTC, which is standard for servers.
    utc_times = ["03:30", "06:30", "13:30", "17:30"]
    print(f"⏰ Scheduling jobs at the following UTC times: {', '.join(utc_times)}")
    for t in utc_times:
        schedule.every().day.at(t).do(run_check)

def main():
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
    #loading animation
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
            "[bold yellow]Shutting down the bot[/bold yellow]\n",
            title=" Goodbye! :(",
            border_style="cyan",
            padding=(1, 4)
        ))
        spinner_running = False
        t.join()

if __name__ == "__main__":
    main()
