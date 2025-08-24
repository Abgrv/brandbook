# config.py
from __future__ import annotations
import os
from dotenv import load_dotenv

# грузим .env из корня проекта
load_dotenv()

# --- Google OAuth ---
GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "http://127.0.0.1:8000/auth/google/callback")

# --- JWT ---
JWT_SECRET: str = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRES_MIN: int = int(os.getenv("JWT_EXPIRES_MIN", "60"))

# --- DB ---
DATABASE_URL: str | None = os.getenv("DATABASE_URL")
