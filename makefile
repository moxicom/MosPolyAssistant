# python3 -m venv ./env
# source env/bin/activate
make_env:
	pip install python-dotenv
	pip install aiogram==2.25.1
	pip install SQLAlchemy==2.0.21
	pip install asyncpg==0.28.0
	pip install asyncio
	pip list

run:
	python3 start_bot.py