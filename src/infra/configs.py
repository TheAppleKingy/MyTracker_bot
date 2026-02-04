from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    bot_token: str
    base_api_url: str
    timezone_db_api_key: str
    timezone_db_url: str
    secret: str
    bot_send_message_base_url: str

    @property
    def bot_send_message_url(self):
        return self.bot_send_message_base_url + self.bot_token + "/sendMessage"


class RedisConfig(BaseSettings):
    redis_host: str
    redis_password: str

    @property
    def conn_url(self):
        return f"redis://:{self.redis_password}@{self.redis_host}:6379"
