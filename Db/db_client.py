from sqlalchemy.sql import select
from sqlalchemy.orm import declarative_base as base
import logging
from Db.postgres import engine, messages_table, tags_table


async def fetch_messages_by_tag(group_id: int, tag_id: int):
    async with engine.connect() as conn:
        table = messages_table
        selectStmt = select(table).where(table.c.group_id == group_id, table.c.tag_id == tag_id)
        result = await conn.execute(selectStmt)
        messages = result.fetchall()
        return messages


async def fetch_main_tags(group_id: int):
    async with engine.connect() as conn:
        table = tags_table
        selectStmt = select(table).where(table.c.group_id == group_id, table.c.parent_id.is_(None))
        result = await conn.execute(selectStmt)
        tags = result.fetchall()
        return tags


async def fetch_sub_tags(parent_id: int):
    async with engine.connect() as conn:
        table = tags_table
        selectStmt = select(table).where(table.c.parent_id == parent_id)
        result = await conn.execute(selectStmt)
        tags = result.fetchall()
        return tags


async def fetch_message_by_id(id: int):
    async with engine.connect() as conn:
        table = messages_table
        selectStmt = select(table).where(table.c.id == id)
        result = await conn.execute(selectStmt)
        message = result.fetchone()
        return message