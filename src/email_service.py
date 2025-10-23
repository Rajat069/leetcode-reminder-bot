import smtplib
from email.message import EmailMessage
from . import config

def send_email(to_email, subject, html_content):
    """Sends an email using the configured SMTP settings."""
    # Config is now loaded from config.py
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
        print("   Please check that your GMAIL_APP_PASSWORD is correct.")
        return False
    except Exception as e:
        print(f"\n Failed to send email to {to_email}: {e}")
        return False


def build_html_email(username, title_slug, link, solved, quote=None):
    """Builds a responsive and enhanced HTML email."""
    
    if solved:
        preheader_text = f"Great job on solving {title_slug}!"
        heading = f"🎉 Great Job, {username}!"
        subtext = f"You’ve completed today’s LeetCode challenge: <strong>{title_slug}</strong>. Keep up the amazing momentum!"
        button_text = "View Challenge"
        button_color = "#4CAF50" # Green
        footer = f"<em>{quote}</em>"
    else:
        preheader_text = f"Don't forget to solve {title_slug} today!"
        heading = f"⚠️ Hey {username}, time to code!"
        subtext = f"Today's problem, <strong>{title_slug}</strong>, is waiting for you. Don't miss out on your streak!"
        button_text = f"Solve '{title_slug}' Now"
        button_color = "#000000" # Black
        footer = "<em>“Small daily improvements lead to big results.” 🌱</em>"

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

        <!--[if mso]>
            <style>
                * {{
                    font-family: sans-serif !important;
                }}
            </style>
        <![endif]-->

        <style>
            /* CSS resets and base styles */
            html, body {{
                margin: 0 auto !important;
                padding: 0 !important;
                height: 100% !important;
                width: 100% !important;
                background: #f1f1f1;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #333;
            }}

            /* Center the email */
            .wrapper {{
                width: 100%;
                background-color: #f1f1f1;
            }}

            /* Main container */
            .container {{
                width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ddd;
            }}

            /* Responsive styles */
            @media screen and (max-width: 600px) {{
                .container {{
                    width: 100% !important;
                    margin: 0 !important;
                    border: none !important;
                    border-radius: 0 !important;
                }}
                .content {{
                    padding: 25px !important;
                }}
                .button-link {{
                    display: block !important;
                    width: 100% !important;
                    box-sizing: border-box; /* Ensures padding doesn't break width */
                }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0 !important; background-color: #f1f1f1;">
        <!-- Visually hidden preheader text -->
        <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
            {preheader_text}
        </div>

        <center class="wrapper">
            <div style="max-width: 600px; margin: 0 auto;">
                <!--[if (gte mso 9)|(IE)]>
                <table align="center" border="0" cellspacing="0" cellpadding="0" width="600" style="width:600px;">
                <tr>
                <td align="center" valign="top">
                <![endif]-->
                
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="container" style="max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; border: 1px solid #ddd;">
                    <!-- Logo/Header (Optional, but good practice) -->
                    <tr>
                        <td align="center" style="padding: 20px 0 10px 0; font-size: 20px; font-weight: 600; color: #000;">
                            LeetCode Daily Reminder
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td class="content" style="padding: 30px 40px;">
                            <h1 style="margin: 0 0 20px 0; font-size: 24px; font-weight: 600; color: #000;">{heading}</h1>
                            <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 1.6;">
                                {subtext}
                            </p>
                            
                            <!-- CTA Button -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="left">
                                        <a href="{link}" target="_blank" class="button-link" style="background-color: {button_color}; color: #ffffff; font-size: 16px; font-weight: bold; text-decoration: none; padding: 14px 22px; border-radius: 5px; display: inline-block;">
                                            {button_text} &rarr;
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer Quote -->
                    <tr>
                        <td class="content" style="padding: 0 40px 30px 40px; border-top: 1px solid #eee;">
                            <p style="margin: 20px 0 0 0; font-size: 14px; color: #555; text-align: left;">
                                {footer}
                            </p>
                        </td>
                    </tr>
                </table>

                <!--[if (gte mso 9)|(IE)]>
                </td>
                </tr>
                </table>
                <![endif]-->
            </div>
        </center>
    </body>
    </html>
        """
