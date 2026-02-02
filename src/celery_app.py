from celery import Celery  # type: ignore
from celery.signals import worker_process_shutdown  # type: ignore
from aiogram import Bot
from dishka import make_container, Provider, provide, Scope, Container
from dishka.integrations.celery import DishkaTask, setup_dishka
from redis.asyncio import Redis, from_url

from src.infra.configs import BotConfig, RedisConfig
from src.infra.redis_storage import RedisBotStorage
from src.application.interfaces.storage import StorageInterface


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def bot_conf(self) -> BotConfig:
        return BotConfig()  # type: ignore

    @provide
    def redis_conf(self) -> RedisConfig:
        return RedisConfig()  # type: ignore

    @provide
    def redis(self, conf: RedisConfig) -> Redis:
        return from_url(conf.conn_url, decode_responses=True)

    @provide
    def storage(self, redis: Redis) -> StorageInterface:
        return RedisBotStorage(redis)

    @provide
    def bot(self, conf: BotConfig) -> Bot:
        return Bot(conf.bot_token)


container = make_container(BotProvider())


def get_celery():
    celery = Celery(__name__, task_cls=DishkaTask)
    conf = container.get(RedisConfig)
    celery.conf.broker_url = conf.conn_url
    celery.conf.result_backend = conf.conn_url
    celery.autodiscover_tasks(['src.infra.tasks.notify'])
    setup_dishka(container, celery)
    return celery


celery_app = get_celery()


@worker_process_shutdown.connect()
def _close_container(*args, **kwargs):
    container: Container = celery_app.conf["dishka_container"]
    container.close()
