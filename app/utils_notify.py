"""Send login credentials via email and/or SMS to a newly-registered student.

Email uses SMTP settings from environment variables (works with Gmail app
passwords, Outlook, etc.). SMS uses Twilio if TWILIO_* env vars are set.
Both channels are best-effort: failures are logged, never raised, so
registration always completes.
"""
import os, smtplib, ssl, logging
from email.message import EmailMessage

log = logging.getLogger(__name__)

def _send_email(to_email: str, student_number: str, password: str) -> bool:
    host = os.getenv("MAIL_SERVER")
    user = os.getenv("MAIL_USERNAME")
    pw   = os.getenv("MAIL_PASSWORD")
    if not (host and user and pw and to_email):
        log.info("Email not configured or no recipient; skipping email send.")
        return False
    port = int(os.getenv("MAIL_PORT", "587"))
    sender = os.getenv("MAIL_FROM", user)
    use_tls = os.getenv("MAIL_USE_TLS", "1") == "1"

    msg = EmailMessage()
    msg["Subject"] = "Your MU Portal Login Details"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"""Welcome to MU Portal!

Your account has been created. Use the credentials below to log in:

  Student Number : {student_number}
  Password       : {password}

Please keep these safe and change your password after your first login.

— MU Portal
"""
    )
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as s:
                s.login(user, pw); s.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as s:
                s.ehlo()
                if use_tls:
                    s.starttls(context=ssl.create_default_context()); s.ehlo()
                s.login(user, pw); s.send_message(msg)
        return True
    except Exception as e:
        log.exception("Failed to send credentials email: %s", e)
        return False

def _send_sms(to_phone: str, student_number: str, password: str) -> bool:
    sid    = os.getenv("TWILIO_ACCOUNT_SID")
    token  = os.getenv("TWILIO_AUTH_TOKEN")
    from_  = os.getenv("TWILIO_FROM")
    if not (sid and token and from_ and to_phone):
        log.info("SMS not configured or no phone; skipping SMS send.")
        return False
    try:
        from twilio.rest import Client  # optional dependency
    except Exception:
        log.warning("twilio package not installed; skipping SMS.")
        return False
    body = (f"MU Portal login — Student #: {student_number}  "
            f"Password: {password}")
    try:
        Client(sid, token).messages.create(to=to_phone, from_=from_, body=body)
        return True
    except Exception as e:
        log.exception("Failed to send credentials SMS: %s", e)
        return False

def send_credentials(email: str, phone: str, student_number: str, password: str):
    """Try email first, then SMS. Returns (email_ok, sms_ok)."""
    return _send_email(email, student_number, password), _send_sms(phone, student_number, password)
