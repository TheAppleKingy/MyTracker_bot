import os

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '../.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
FORMATTED_TEST_DATABASE_URL = os.getenv("FORMATTED_TEST_DATABASE_URL")
FORMATTED_DATABASE_URL = os.getenv("FORMATTED_DATABASE_URL")
SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_EXPIRE_TIME = os.getenv('ACCESS_EXPIRE_TIME')
REFRESH_EXPIRE_TIME = os.getenv('REFRESH_EXPIRE_TIME')
