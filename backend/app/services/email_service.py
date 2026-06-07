# Module: app.services.email_service
# Description: Service handling SMTP and SendGrid email integration with console log fallbacks.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """
        Sends an email using SendGrid if key is provided, else falls back to SMTP,
        and finally falls back to logging/console if credentials are not configured.
        """
        # Try SendGrid first if API key is provided
        if settings.SENDGRID_API_KEY:
            try:
                # We try importing SendGrid client dynamically
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail as SGMail
                
                message = SGMail(
                    from_email=(settings.ALERT_FROM_EMAIL, settings.ALERT_FROM_NAME),
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_body,
                    plain_text_content=text_body
                )
                # List-Unsubscribe Header
                message.add_header({"List-Unsubscribe": f"<mailto:unsubscribe@inflationiq.ai?subject=unsubscribe>, <https://inflationiq.ai/unsubscribe>"})
                
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Email successfully sent via SendGrid to {to_email}")
                    return True
                else:
                    logger.warning(f"SendGrid failed with status {response.status_code}: {response.body}")
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid: {e}. Trying SMTP fallback...")

        # SMTP Fallback
        if settings.SMTP_HOST:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{settings.ALERT_FROM_NAME} <{settings.ALERT_FROM_EMAIL}>"
                msg["To"] = to_email
                msg.add_header("List-Unsubscribe", f"<mailto:unsubscribe@inflationiq.ai?subject=unsubscribe>, <https://inflationiq.ai/unsubscribe>")

                msg.attach(MIMEText(text_body, "plain"))
                msg.attach(MIMEText(html_body, "html"))

                # Connect and send
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                    if settings.SMTP_USE_TLS:
                        server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.ALERT_FROM_EMAIL, to_email, msg.as_string())
                
                logger.info(f"Email successfully sent via SMTP to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP to {to_email}: {e}")

        # Console logging fallback
        logger.info(f"[EMAIL MOCK SEND] To: {to_email} | Subject: {subject}\nBody:\n{text_body}")
        return True
