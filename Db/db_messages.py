from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_
from sqlalchemy.orm import declarative_base as base
import logging
from sqlalchemy import update

engine = asyncio_ext.create_async_engine(
    "postgresql+asyncpg://postgres:314159@localhost:5432/postgres",
    echo=False,
    future=True
)

async def createTable():
    metadata = MetaData()
    table = Table("messages", metadata,
                  Column('id', Integer, primary_key=True),
                  Column('group_id', Integer),
                  Column('title', VARCHAR(255)),
                  Column('text', String),
                  Column('tag_id', Integer),
                  Column('images', String),
                  Column('videos', String),
                  Column('files', String),
                  Column('created_at', Date))
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        await conn.commit()

async def insert_messages(group_id: int, title: str, text: str, tag_id: int, images: str, videos: str, files: str,
                          created_at):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("messages", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('title', VARCHAR),
                      Column('text', VARCHAR),
                      Column('tag_id', Integer),
                      Column('images', VARCHAR),
                      Column('videos', VARCHAR),
                      Column('files', VARCHAR),
                      Column('created_at', Date))
        insertStmt = table.insert().values(group_id=group_id, title=title, text=text, tag_id=tag_id, images=images, \
                                           videos=videos, files=files, created_at=created_at)
        await conn.execute(insertStmt)
        await conn.commit()

async def delete_messages_by_group_id(group_id: int):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("messages", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('title', VARCHAR),
                      Column('text', VARCHAR),
                      Column('tag_id', Integer),
                      Column('images', VARCHAR),
                      Column('videos', VARCHAR),
                      Column('files', VARCHAR),
                      Column('created_at', Date))
        
        deleteStmt = table.delete().where(table.c.group_id == group_id)

        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_messages/delete_messages_by_group_id| complited")

async def fetch_messages_by_tag(tag_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("messages", metadata,
                      Column('id', BIGINT, primary_key=True),
                      Column('group_id', BIGINT),
                      Column('title', VARCHAR),
                      Column('text', VARCHAR),
                      Column('tag_id', BIGINT),
                      Column('images', VARCHAR),
                      Column('videos', VARCHAR),
                      Column('files', VARCHAR),
                      Column('created_at', Date))
        selectStmt = select(table).where(table.c.tag_id == tag_id)
        result = await conn.execute(selectStmt)
        messages = result.fetchall()
        logging.info("|Db/db_messages/fetch_messages_by_tag| complited")
        return messages

async def delete_messages_by_id(id: int):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("messages", metadata,
                      Column('id', BIGINT, primary_key=True),
                      Column('group_id', BIGINT),
                      Column('title', VARCHAR),
                      Column('text', VARCHAR),
                      Column('tag_id', BIGINT),
                      Column('images', VARCHAR),
                      Column('videos', VARCHAR),
                      Column('files', VARCHAR),
                      Column('created_at', Date))

        deleteStmt = table.delete().where(table.c.id == id)

        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_messages/delete_messages_by_id| complited")