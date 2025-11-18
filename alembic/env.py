import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Cho Python tìm app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Base từ database
from app.database import Base
# Import tất cả model để Alembic nhận biết
from app.models import user, user_role, category, summary, comment, note, reading_history, vocabulary, recommendation, rating

# Alembic config
config = context.config
raw_url = os.getenv("DATABASE_URL")
# Escape % để tránh configparser lỗi
escaped_url = raw_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", escaped_url)
fileConfig(config.config_file_name)

# metadata để autogenerate
target_metadata = Base.metadata


