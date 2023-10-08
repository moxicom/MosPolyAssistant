from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_, func
from sqlalchemy.orm import declarative_base as base
import asyncio
from sqlalchemy import update


engine = asyncio_ext.create_async_engine(
    "postgresql+asyncpg://postgres:314159@localhost:5432/postgres",
    echo=False,
    future=True
)


metadata = MetaData()

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


async def fetch_tags_with_pagination(page_number: int, items_per_page: int, group_id, parent_id):
    """Fetch tags with pagination and check if it's the last page"""

    async with engine.connect() as conn:
        offset = (page_number - 1) * items_per_page

        select_stmt = select(tags_table).where(and_(tags_table.c.group_id == group_id, tags_table.c.parent_id == parent_id))
        select_stmt = select_stmt.offset(offset).limit(items_per_page)

        result = await conn.execute(select_stmt)
        rows = result.fetchall()

        if not rows:
            if page_number != 1:
                return [], False, True
            else:
                return [], True, True
        
        tags = rows
        is_first_page = page_number == 1
        is_last_page = len(rows) < items_per_page

        return tags, is_first_page, is_last_page
    

async def fetch_messages_with_pagination(page_number: int, items_per_page: int, group_id, tag_id):
    """Fetch messages by tag_id and with pagination and check if it's the last page"""
    
    async with engine.connect() as conn:
        offset = (page_number - 1) * items_per_page

        select_stmt = select(messages_table).where(and_(messages_table.c.group_id == group_id, messages_table.c.tag_id == tag_id))
        select_stmt = select_stmt.offset(offset).limit(items_per_page)

        result = await conn.execute(select_stmt)
        rows = result.fetchall()

        if not rows:
            if page_number != 1:
                return [], False, True
            else:
                return [], True, True
        
        messages = rows
        is_first_page = page_number == 1
        is_last_page = len(rows) < items_per_page

        return messages, is_first_page, is_last_page
