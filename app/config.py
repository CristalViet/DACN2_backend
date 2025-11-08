# ⚙️ 7️⃣ app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:29122004@127.0.0.1:3306/booklearning"  # sửa username/pass/db của bạn tại đây
)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
