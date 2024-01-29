# python3 -m venv ./env
# source env/bin/activate

.PHONY: migration install_dep run alembic migration

venv:
	python3 -m venv ./env

install_dep:
	env/bin/python -m pip install python-dotenv
	env/bin/python -m pip install aiogram==2.25.1
	env/bin/python -m pip install SQLAlchemy==2.0.21
	env/bin/python -m pip install asyncpg==0.28.0
	env/bin/python -m pip install asyncio
	env/bin/python -m pip install alembic
	env/bin/python -m pip install psycopg2-binary
	env/bin/python -m pip list

alembic:
	alembic init migration
	# Use alembic.ini to make migraion properties
	# You do not need use this command

MIG_NAME ?= default_migration

migration:
	env/bin/python -m alembic revision --autogenerate -m "$(MIG_NAME)"
	env/bin/python -m alembic upgrade head


run:
	env/bin/python -m start_bot
	# or just run start_bot.py using env