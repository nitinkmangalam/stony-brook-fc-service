import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://nitin:temp@localhost/fifa_tournament")
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
