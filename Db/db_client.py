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


async def fetch_messages_by_tag(group_id: int, tag_id: int):
    async with engine.connect() as conn:
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
        selectStmt = select(table).where(table.c.group_id == group_id, table.c.tag_id == tag_id)
        result = await conn.execute(selectStmt)
        messages = result.fetchall()
        return messages


async def fetch_main_tags(group_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table).where(table.c.group_id == group_id, table.c.parent_id.is_(None))
        result = await conn.execute(selectStmt)
        tags = result.fetchall()
        return tags


async def fetch_sub_tags(parent_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table).where(table.c.parent_id == parent_id)
        result = await conn.execute(selectStmt)
        tags = result.fetchall()
        return tags


async def fetch_message_by_id(id: int):
    async with engine.connect() as conn:
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
        selectStmt = select(table).where(table.c.id == id)
        result = await conn.execute(selectStmt)
        message = result.fetchone()
        return message