import os

from dotenv import load_dotenv
from redis.asyncio import from_url


load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = os.getenv('REDIS_URL')
BASE_API_URL = os.getenv("BASE_API_URL")
QUEUE = os.getenv("BOT_QUEUE")
redis = from_url(REDIS_URL, decode_responses=True)
