"""
In-memory OTP storage with expiration
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import logging
from app.config import OTP_EXPIRY_MINUTES, OTP_LENGTH

logger = logging.getLogger(__name__)


class OTPStorage:
    """
    In-memory storage for OTP codes with expiration
    Format: {email: {"otp": "123456", "expires_at": datetime, "user_id": int}}
    """
    def __init__(self):
        self._storage: dict[str, dict] = {}
    
    def generate_otp(self) -> str:
        """Generate a random 6-digit OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(OTP_LENGTH)])
    
    def store_otp(self, email: str, user_id: int) -> str:
        """
        Generate and store OTP for email
        
        Args:
            email: User email
            user_id: User ID
            
        Returns:
            str: Generated OTP code
        """
        # Clean up expired OTPs
        self._cleanup_expired()
        
        # Generate new OTP
        otp_code = self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Store OTP
        self._storage[email.lower()] = {
            "otp": otp_code,
            "expires_at": expires_at,
            "user_id": user_id,
            "created_at": datetime.now()
        }
        
        logger.info(f"OTP stored for {email}, expires at {expires_at}")
        return otp_code
    
    def verify_otp(self, email: str, otp: str) -> Optional[int]:
        """
        Verify OTP code for email
        
        Args:
            email: User email
            otp: OTP code to verify
            
        Returns:
            Optional[int]: User ID if OTP is valid, None otherwise
        """
        # Clean up expired OTPs
        self._cleanup_expired()
        
        email_lower = email.lower()
        stored_data = self._storage.get(email_lower)
        
        if not stored_data:
            logger.warning(f"No OTP found for {email}")
            return None
        
        # Check if OTP matches
        if stored_data["otp"] != otp:
            logger.warning(f"Invalid OTP for {email}")
            return None
        
        # Check if expired
        if datetime.now() > stored_data["expires_at"]:
            logger.warning(f"OTP expired for {email}")
            del self._storage[email_lower]
            return None
        
        # OTP is valid, return user_id and remove OTP
        user_id = stored_data["user_id"]
        del self._storage[email_lower]
        logger.info(f"OTP verified successfully for {email}")
        return user_id
    
    def _cleanup_expired(self):
        """Remove expired OTPs from storage"""
        now = datetime.now()
        expired_emails = [
            email for email, data in self._storage.items()
            if now > data["expires_at"]
        ]
        for email in expired_emails:
            del self._storage[email]
    
    def get_otp_info(self, email: str) -> Optional[dict]:
        """Get OTP info without removing it (for debugging)"""
        self._cleanup_expired()
        return self._storage.get(email.lower())


# Global OTP storage instance
otp_storage = OTPStorage()


