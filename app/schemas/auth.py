from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RequestOTPRequest(BaseModel):
    """Request OTP for login"""
    email: EmailStr
    password: str | None = None  # Optional: if provided, verify password; if not, just check email exists


class VerifyOTPRequest(BaseModel):
    """Verify OTP code"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class RegisterRequest(BaseModel):
    # Accept both 'username' and 'name' for frontend compatibility
    # Frontend may send 'name', backend uses 'username'
    username: str | None = Field(None, min_length=1, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=100)  # Alias for username
    email: EmailStr
    password: str = Field(..., min_length=1)
    phone: str | None = Field(None, max_length=20)
    
    @model_validator(mode='after')
    def validate_username_or_name(self):
        """Ensure either username or name is provided, and normalize to username"""
        if not self.username and not self.name:
            raise ValueError("Either 'username' or 'name' must be provided")
        # If name is provided but username is not, use name as username
        if self.name and not self.username:
            self.username = self.name
        # Ensure username is set (should always be after this point)
        if not self.username:
            raise ValueError("Username is required")
        return self
    
    model_config = ConfigDict(
        # Allow extra fields to be ignored (in case frontend sends extra data)
        extra="ignore"
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


