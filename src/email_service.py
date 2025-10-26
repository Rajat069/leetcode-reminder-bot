import smtplib
from email.message import EmailMessage
from . import config
from datetime import datetime, timezone, timedelta

def send_email(to_email, subject, html_content):
    """Sends an email using the configured SMTP settings."""
   
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        print(f"[ERROR] SMTP not configured. Skipping email to {to_email}")
        return False

    try:
        msg = EmailMessage()
        msg['From'] = f"LeetCode Reminder Bot <{config.SMTP_USER}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content("This email requires HTML support to be viewed correctly.")
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(msg)

        return True
    except smtplib.SMTPAuthenticationError:
        print(f"\n Authentication failed for {config.SMTP_USER}.")
        print("  Please check that your GMAIL_APP_PASSWORD is correct.")
        return False
    except Exception as e:
        print(f"\n Failed to send email to {to_email}: {e}")
        return False


def build_html_email(username, title, link, solved, quote=None, hints=None):
    """Builds a responsive email with optional AI hints, quotes, and a live countdown GIF."""
    
    if hints is None:
        hints = []

    timer_html = ""

    if solved:
        preheader_text = f"Great job on solving {title}!"
        heading = f"🎉 Great Job, {username}!"
        subtext = f"You’ve completed today’s LeetCode challenge: <strong>{title}</strong>. Keep up the amazing momentum!"
        button_text = "View Challenge"
        button_color = "#4CAF50" 
        footer = f"<em>“{quote}”</em>" if quote else "<em>Keep up the great work!</em>"
        hints_html = ""
        
    else:
        preheader_text = f"Don't forget to solve {title} today!"
        heading = f"Hey <a href='https://leetcode.com/u/{username}' target='_blank' style='text-decoration: none;'>{username}</a>, time to code!"
        subtext = f"Today's problem, <strong>{title}</strong>, is waiting for you. Don't miss out on your streak!"
        button_text = f"Solve '{title}' Now"
        button_color = "#000000" 
        footer = f"<em>“{quote}”</em>" if quote else "<em>“Small daily improvements lead to big results.” 🌱</em>"

        deadline_iso = get_deadline_for_potd()
        gif_url = f"https://i.countdownmail.com/4khdvf.gif?end_date_time={deadline_iso}"
                
        timer_html = f"""
            <tr>
                <td align="center" style="padding: 10px 0 10px 0;">
                    <a href="{link}" target="_blank" style="text-decoration: none;">
                        <img src="{gif_url}" style="width:45%!important;" border="0" alt="Time remaining to solve"/>
                    </a>
                </td>
            </tr>
        """
        
        # --- Hints Section ---
        if hints:
            hints_list_items = "".join([f'<li style="margin-bottom: 10px; line-height: 1.6;">{h}</li>' for h in hints])
            hints_html = f"""
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px;">
                <tr>
                    <td style="background-color: #f9f9f9; border: 1px solid #eee; border-radius: 8px; padding: 25px;">
                        <h3 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #333;">💡 AI-Powered Hints</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            {hints_list_items}
                        </ul>
                    </td>
                </tr>
            </table>
            """
        else:
            hints_html = ""

    # --- HTML & CSS Template ---
    return f"""
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="x-apple-disable-message-reformatting">
            <title>LeetCode Reminder</title>

            <style>
                html, body {{
                    margin: 0 auto !important;
                    padding: 0 !important;
                    height: 100% !important;
                    width: 100% !important;
                    background: #f1f1f1;
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    color: #333;
                }}
                .wrapper {{
                    width: 100%;
                    background-color: #f1f1f1;
                }}
                .container {{
                    width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                }}
                @media screen and (max-width: 600px) {{
                    .container {{
                        width: 100% !important;
                        margin: 0 !important;
                        border: none !important;
                        border-radius: 0 !Dimportant;
                    }}
                    .content {{
                        padding: 25px !important;
                    }}
                    .button-link {{
                        display: block !important;
                        width: 100% !important;
                        box-sizing: border-box;
                    }}
                }}
            </style>
        </head>
        <body style="margin: 0; padding: 0 !important; background-color: #f1f1f1;">
            <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
                {preheader_text}
            </div>

            <center class="wrapper">
                <div style="max-width: 600px; margin: 0 auto;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="container" style="max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; border: 1px solid #ddd;">
                        <tr>
                            <td align="center" style="padding: 20px 0 15px 0; font-size: 20px; font-weight: 600; color: #000;">
                               <img src="https://i.postimg.cc/qRgJjC6P/Leet-Code-logo-black.png" alt="" width="20px" height="20px">
                                LeetCode Daily Reminder
                            </td>
                        </tr>
                        {timer_html}
                        <tr>
                            <td class="content" style="padding: 30px 40px;">
                                <h1 style="margin: 0 0 20px 0; font-size: 24px; font-weight: 600; color: #000; text-align: center;">{heading}</h1>
                                <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 1.6;">
                                    {subtext}
                                </p>
                                
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center">
                                            <a href="{link}" target="_blank" class="button-link" style="background-color: {button_color}; color: #ffffff; font-size: 16px; font-weight: bold; text-decoration: none; padding: 14px 22px; border-radius: 5px; display: inline-block;">
                                                {button_text} &rarr;
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                {hints_html}
                                
                            </td>
                        </tr>
                        
                        <tr>
                            <td class="content" style="padding: 0 40px 30px 40px; border-top: 1px solid #eee;">
                                <p style="margin: 20px 0 0 0; font-size: 14px; color: #555; text-align: left;">
                                    {footer}
                                </p>
                            </td>
                        </tr>
                    </table>

                    </div>
            </center>
        </body>
        </html>
            """

def get_deadline_for_potd(hour=17, minute=0):
    """
    Returns a deadline in UTC ISO format (YYYY-MM-DDTHH:MM:SSZ) 
    based on the current time in PST. 
    
    Parameters:
    hour (int): The hour in PST to use for the deadline (default: 17)
    minute (int): The minute in PST to use for the deadline (default: 0)

    Returns:
    str: The deadline in UTC ISO format
    """
    tz_pst = timezone(timedelta(hours=-8))  # PST

    now_utc = datetime.now(timezone.utc)
    now_pst = now_utc.astimezone(tz_pst)

    today_deadline_pst = now_pst.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if now_pst >= today_deadline_pst:
        today_deadline_pst += timedelta(days=1)

    deadline_utc = today_deadline_pst.astimezone(timezone.utc)
    return deadline_utc.isoformat()


#To Do - add a function that send admin email when bot is stopped
#def stop_bot_admin_email():


