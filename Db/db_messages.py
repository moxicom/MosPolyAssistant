from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_
from sqlalchemy.orm import declarative_base as base
import logging
from sqlalchemy import update
from Db.postgres import engine, messages_table


async def insert_messages(group_id: int, title: str, text: str, tag_id: int, images: str, videos: str, files: str,
                          created_at):
    async with engine.begin() as conn:
        table = messages_table
        insertStmt = table.insert().values(group_id=group_id, title=title, text=text, tag_id=tag_id, images=images, \
                                           videos=videos, files=files, created_at=created_at)
        await conn.execute(insertStmt)
        await conn.commit()

async def delete_messages_by_group_id(group_id: int):
    async with engine.begin() as conn:
        table = messages_table
        deleteStmt = table.delete().where(table.c.group_id == group_id)

        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_messages/delete_messages_by_group_id| complited")

async def fetch_messages_by_tag(tag_id: int):
    async with engine.connect() as conn:
        table = messages_table
        selectStmt = select(table).where(table.c.tag_id == tag_id)
        result = await conn.execute(selectStmt)
        messages = result.fetchall()
        logging.info("|Db/db_messages/fetch_messages_by_tag| complited")
        return messages

async def delete_messages_by_id(id: int):
    async with engine.begin() as conn:
        table = messages_table
        deleteStmt = table.delete().where(table.c.id == id)

        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_messages/delete_messages_by_id| complited")