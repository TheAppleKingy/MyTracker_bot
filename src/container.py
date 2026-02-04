from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.aiogram import AiogramProvider
from redis.asyncio import from_url, Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

from src.application.interfaces.clients import *
from src.application.interfaces import *
from src.application.interfaces.services import *
from src.infra.clients import *
from src.infra.configs import RedisConfig, BotConfig
from src.infra.services import *
from src.infra.redis_storage import AsyncRedisBotStorage
from src.interfaces.handlers.telegram.middleware import HandleErrorMiddleware
from src.interfaces.handlers.telegram.tasks.shared import *


class ClientsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_backend_client(self, conf: BotConfig, token_service: TokenServiceInterface) -> BackendClientInterface:
        return HttpBackendClient(conf.base_api_url, token_service)

    country_client = provide(CountryClient, provides=CountryClientInterface)

    @provide
    def get_tz_client(self, conf: BotConfig) -> TimezoneClientInterface:
        return HttpTZClient(conf.timezone_db_api_key, conf.timezone_db_url)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_token_service(self, conf: BotConfig) -> TokenServiceInterface:
        return JWTService(conf.secret)

    notify_service = provide(CeleryNotifyService, provides=NotifyServiceInterface)


class ConfProvider(Provider):
    scope = Scope.APP

    @provide
    def bot_conf(self) -> BotConfig:
        return BotConfig()

    @provide
    def redis_conf(self) -> RedisConfig:
        return RedisConfig()


class SharedProvider(Provider):
    scope = Scope.APP

    set_reminder_case = provide(SetReminder, scope=Scope.REQUEST)
    change_deadline_case = provide(ChangeDeadline, scope=Scope.REQUEST)
    finish_task_case = provide(FinishTask, scope=Scope.REQUEST)
    force_finish_task_case = provide(ForceFinishTask, scope=Scope.REQUEST)

    @provide
    def get_redis(self, conf: RedisConfig) -> Redis:
        return from_url(conf.conn_url, decode_responses=True)

    redis_bot_storage = provide(AsyncRedisBotStorage, provides=AsyncStorageInterface, scope=Scope.REQUEST)

    @provide
    def fsm_storage(self, redis: Redis) -> RedisStorage:
        return RedisStorage(redis=redis)

    @provide
    def get_bot(self, conf: BotConfig) -> Bot:
        return Bot(conf.bot_token)

    @provide
    def get_dispatcher(self, storage: RedisStorage) -> Dispatcher:
        dispatcher = Dispatcher(storage=storage)
        dispatcher.message.middleware(HandleErrorMiddleware())
        dispatcher.callback_query.middleware(HandleErrorMiddleware())
        return dispatcher


container = make_async_container(
    ClientsProvider(),
    ServiceProvider(),
    ConfProvider(),
    SharedProvider(),
    AiogramProvider()
)
