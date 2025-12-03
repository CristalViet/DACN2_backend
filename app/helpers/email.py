"""
Email helper for sending OTP emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM

logger = logging.getLogger(__name__)


def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email
    
    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = email
        msg['Subject'] = "Your OTP Code for Book Learning"
        
        # Email body
        body = f"""
        <html>
          <body>
            <h2>Your OTP Code</h2>
            <p>Hello,</p>
            <p>Your One-Time Password (OTP) for login is:</p>
            <h1 style="color: #4CAF50; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Book Learning Team</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.error("SMTP credentials not configured. Cannot send email.")
            return False
            
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"OTP email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


