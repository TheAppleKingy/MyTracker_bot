# MyTracker - это личный таск-трекер с управлением через телеграм-бота.

Для запуска серверной части приложения на локальной машине:
```commandline
docker-compose up --build
```
После поднятия контейнера не забудьте применить миграции к бд:
```commandline
docker-compose exec app alembic upgrade head
```

На данном этапе разрабатывается API и архитектура серверной части. Вскоре начнется разработка бота

* Технологии:
* * бэкенд - **FastaAPI**
* * бот - **aiogram**
* * локальный веб-сервер - **uvicorn**
* * бд - **PostrgreSQL**
* * работа с бд - **SQLAlchemy и asyncpg**
* * тестироывние - **pytest**
* * кеш, брокер задач - **Redis**
* * очереди задач - **Celery**

------------------------------------------------------------------------------------------------------------
*Создать alembic.ini*
```commandline
alembic init -t async migration
```

*Создать миграцию*
```
alembic revision --autogenerate -m "migration message"
```

*Применить миграции до последней*
```
alembic upgrade head
```

*Применить мигарции до определенной*
```
alembic upgrade migration_id
```

*Откатить на n миграций*
```
alembic downgrade -n
```

*Откат до определенной миграции*
```
alembic downgrade migration_id
```
