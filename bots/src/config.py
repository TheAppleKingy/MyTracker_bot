import os

from dotenv import load_dotenv
from redis.asyncio import from_url


load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = os.getenv('REDIS_URL')
BASE_API_URL = os.getenv("BASE_API_URL")
QUEUE = os.getenv("BOT_QUEUE")
TIMEZONE_DB_API_KEY = os.getenv("TIMEZONE_DB_API_KEY")
