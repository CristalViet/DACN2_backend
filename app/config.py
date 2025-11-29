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