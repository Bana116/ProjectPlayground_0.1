import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# ---------------------------------------------------------
# Base send email function
# ---------------------------------------------------------
def send_email(to, subject, html_body):
    """
    Sends email via SMTP (Gmail or any SMTP provider).
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

        print(f"Email sent to {to}. Subject: {subject}")

    except Exception as e:
        print("Email error:", e)


# ---------------------------------------------------------
# Confirmation email (after form submission)
# ---------------------------------------------------------
def send_confirmation_email(user_email, user_type):
    if user_type == "designer":
        subject = "You're In! Welcome Designer 🎨"
        html = f"""
        <h2>Welcome to CreativePlay!</h2>
        <p>Thanks for joining as a <b>designer</b>. We’ll send your first match soon.</p>
        """
    else:
        subject = "You're In! Welcome Founder 🚀"
        html = f"""
        <h2>Welcome to CreativePlay!</h2>
        <p>Thanks for joining as a <b>founder</b>. We’re searching for great designers for you.</p>
        """

    send_email(user_email, subject, html)


# ---------------------------------------------------------
# Match email – sent to both sides when matched
# ---------------------------------------------------------
def send_match_email(user_email, matched_person):
    subject = "You’ve Got a Match! 🔥"

    html = f"""
    <h2>Your Match Is Ready!</h2>

    <p>You’ve been matched with <b>{matched_person.name}</b>.</p>

    <p>Email: {matched_person.email}</p>

    <p>Say hey and start building together!</p>
    """

    send_email(user_email, subject, html)


# ---------------------------------------------------------
# Rematch email – sent after a rematch request
# ---------------------------------------------------------
def send_rematch_email(user_email, match_list):
    subject = "Your New Matches Are Ready 🔄"

    match_items = ""
    for m in match_list:
        match_items += f"""
        <p><b>{m.name}</b><br>
        Email: {m.email}<br>
        Skills/Experience: {m.skills or m.experience}</p>
        <hr>
        """

    html = f"""
    <h2>Your New Matches Are Here!</h2>
    <p>You requested a rematch and we found new designers for you.</p>

    {match_items}

    <p>Use your matches wisely — you got this!</p>
    """

    send_email(user_email, subject, html)


# ---------------------------------------------------------
# Out of credits email
# ---------------------------------------------------------
def send_out_of_credits_email(user_email):
    subject = "You're Out of Credits 😭"
    html = """
    <h2>Oh no!</h2>
    <p>You’ve used all your rematch credits.</p>
    <p>You can buy more anytime to keep finding better matches.</p>
    """

    send_email(user_email, subject, html)
