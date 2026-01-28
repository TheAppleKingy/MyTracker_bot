import os

from celery import Celery
from celery.signals import worker_process_shutdown
from aiogram import Bot
from dishka import make_container, Provider, provide, Scope, Container
from dishka.integrations.celery import DishkaTask, setup_dishka

from src.infra.configs import BotConfig, RedisConfig


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def bot_conf(self) -> BotConfig:
        return BotConfig()

    @provide
    def redis_conf(self) -> RedisConfig:
        return RedisConfig()

    @provide
    def bot(self, conf: BotConfig) -> Bot:
        return Bot(conf.bot_token)


container = make_container(BotProvider())


def get_celery():
    celery = Celery(__name__, task_cls=DishkaTask)
    conf = container.get(RedisConfig)
    celery.conf.broker_url = conf.conn_url
    celery.conf.result_backend = conf.conn_url
    celery.autodiscover_tasks(['src.infra.tasks'])
    setup_dishka(container, celery)
    return celery


celery_app = get_celery()


@worker_process_shutdown.connect()
def _close_container(*args, **kwargs):
    container: Container = celery_app.conf["dishka_container"]
    container.close()
