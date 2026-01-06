import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import time

class MailSender:
    def __init__(self, smtp_server: str, port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send_email(self, to_email: str, subject: str, body: str, retries: int = 3):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        for attempt in range(retries):
            try:
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
                logging.info(f"Email sent successfully to {to_email}")
                return True
            except Exception as e:
                logging.error(f"Attempt {attempt+1} failed to send email to {to_email}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
        return False
