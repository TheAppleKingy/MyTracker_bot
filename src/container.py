from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.aiogram import AiogramProvider
from redis import from_url, Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

from application.interfaces.clients import *
from src.application.interfaces.token_service import TokenServiceInterface
from infra.clients import *
from src.infra.configs import RedisConfig, BotConfig
from src.infra.jwt import JWTService


class ClientsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_backend_provider(self, conf: BotConfig, token_service: TokenServiceInterface) -> BackendClientInterface:
        return HttpBackendClient(conf.base_api_url, token_service)

    country_client = provide(CountryClient, provides=CountryClientInterface)

    @provide
    def get_tz_client(self, conf: BotConfig) -> TimezoneClientInterface:
        return HttpTZClient(conf.timezone_db_api_key, conf.timezone_db_url)

    @provide(scope=Scope.APP)
    def get_redis_client(self, conf: RedisConfig) -> Redis:
        return from_url(conf.conn_url)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_token_service(self, conf: BotConfig) -> TokenServiceInterface:
        return JWTService(conf.secret)


conf_provider = Provider(scope=Scope.APP)
conf_provider.provide_all(BotConfig, RedisConfig)


class SharedProvider(Provider):
    scope = Scope.APP

    @provide
    def get_storage(self, cli: Redis) -> RedisStorage:
        return RedisStorage(cli)

    @provide
    def get_bot(self, conf: BotConfig) -> Bot:
        return Bot(conf.bot_token)

    @provide
    def get_dispatcher(self, storage: RedisStorage) -> Dispatcher:
        return Dispatcher(storage=storage)


container = make_async_container(
    ClientsProvider(),
    ServiceProvider(),
    AiogramProvider())
