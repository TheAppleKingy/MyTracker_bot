import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = os.getenv('REDIS_URL')
BASE_API_URL = os.getenv("BASE_API_URL")
