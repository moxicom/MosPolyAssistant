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


tags_table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))


messages_table = Table("messages", metadata,
                       Column('id', Integer, primary_key=True),
                       Column('group_id', Integer),
                       Column('title', VARCHAR),
                       Column('text', VARCHAR),
                       Column('tag_id', Integer),
                       Column('images', VARCHAR),
                       Column('videos', VARCHAR),
                       Column('files', VARCHAR),
                       Column('created_at', Date))


group_members_table = Table("groups_members", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('member_id', Integer),
                      Column('group_id', Integer),
                      Column('role', Integer))


groups_info_table = Table("groups_info", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(50)),
                      Column('password', VARCHAR))


attachments_table = Table('attachments', metadata,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('video', VARCHAR, nullable=True),
                      Column('file', VARCHAR, nullable=True),
                      Column('image', VARCHAR, nullable=True),
                      Column('audio', VARCHAR, nullable=True))