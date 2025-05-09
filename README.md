Учебный проект: Таск-трекер

Создать миграцию
alembic init -t async migration //после этого создается alembic.ini

Обновить миграции при обновлении моделей данных
alembic revision --autogenerate -m "migration message"

Применить миграции до последней
alembic upgrade head

Применить мигарции до определенной
alembic upgrade migration_id

Откатить на n миграций
alembic downgrade -n

Откат до определенной миграции
alembic downgrade migration_id