from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    bot_token: str
    base_api_url: str
    timezone_db_api_key: str
    timezone_db_url: str
    secret: str


class RedisConfig(BaseSettings):
    redis_host: str
    redis_password: str

    @property
    def conn_url(self):
        return f"redis://:{self.redis_password}@{self.redis_host}:6379"
