from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "MB Solar Hub - Attendance & Daily Work Management System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Timezone: Crucial business requirement (Asia/Kolkata)
    TIMEZONE: str = "Asia/Kolkata"

    # Database
    DATABASE_URL: str = "sqlite:///./mb_solar_hub.db"

    # Supabase Auth
    SUPABASE_URL: str = "https://hpfqqbuaozdgpsdvylrh.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhwZnFxYnVhb3pkZ3BzZHZ5bHJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTUxNTUxMDgsImV4cCI6MjExMDczMTEwOH0.v_cCbwsaA4hrhx1iJGYXg1o0tY62H-AIgKqzaeHxgqU"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: str = "mb-solar-hub-attendance-jwt-secret-key-32chars"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Management Alerts / Reporting (Sir)
    SIR_EMAIL: str = "management@mbsolarhub.com"
    SIR_NAME: str = "Sir (Management)"
    EMAILS_FROM: str = "attendance-alerts@mbsolarhub.com"
    SMTP_HOST: Optional[str] = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Attendance Window Rules (in 24-hr IST)
    NORMAL_WORK_START: str = "09:00"
    NORMAL_WORK_END: str = "18:00"
    CHECKIN_WINDOW_START: str = "08:45"
    CHECKIN_WINDOW_END: str = "10:00"
    CHECKOUT_WINDOW_START: str = "18:00"
    CHECKOUT_WINDOW_END: str = "19:00"
    LUNCH_START: str = "13:00"
    LUNCH_END: str = "14:00"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
