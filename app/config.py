# ⚙️ 7️⃣ app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:29122004@127.0.0.1:3306/booklearning"  # sửa username/pass/db của bạn tại đây
)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID", "")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY", "")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY", "")
PAYOS_BASE_URL = os.getenv("PAYOS_BASE_URL", "https://api.payos.vn")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

# Email configuration for OTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Your Gmail App Password
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)  # Email sender address

# OTP configuration
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))  # OTP expires in 10 minutes
OTP_LENGTH = int(os.getenv("OTP_LENGTH", "6"))  # 6-digit OTP