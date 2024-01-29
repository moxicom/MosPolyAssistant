from sqlalchemy.ext import asyncio as asyncio_ext # engine
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")

url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"
print(url)

engine = asyncio_ext.create_async_engine(url)

metadata = MetaData()

users_table = Table('users', metadata,
                Column('id', Integer, primary_key=True),
                Column('name', VARCHAR),
                Column('group_id', Integer),
                Column('tg_id', BIGINT))
