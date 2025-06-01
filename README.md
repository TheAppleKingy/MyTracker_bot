Учебный проект: Таск-трекер

Создать alembic.ini
alembic init -t async migration

Создать миграцию
alembic revision --autogenerate -m "migration message"

Применить миграции до последней
alembic upgrade head

Применить мигарции до определенной
alembic upgrade migration_id

Откатить на n миграций
alembic downgrade -n

Откат до определенной миграции
alembic downgrade migration_id