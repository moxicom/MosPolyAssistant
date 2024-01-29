# python3 -m venv ./env
# source env/bin/activate

.PHONY: migration install_dep run alembic migration

install_dep:
	pip install python-dotenv
	pip install aiogram==2.25.1
	pip install SQLAlchemy==2.0.21
	pip install asyncpg==0.28.0
	pip install asyncio
	pip install alembic
	pip install psycopg2-binary
	pip list

run:
	python3 start_bot.py

alembic:
	alembic init migration
	# В файле alembic.ini указываем адрес базы

MIG_NAME ?= default_migration

migration:
	alembic revision --autogenerate -m "$(MIG_NAME)"
	alembic upgrade head
