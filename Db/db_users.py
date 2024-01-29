from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_
from sqlalchemy.orm import declarative_base as base
import logging
from sqlalchemy import update

from Db.postgres import engine, users_table


async def insert_users(name: VARCHAR, group_id: int, tg_id: BIGINT):
    async with engine.begin() as conn:
        table = users_table
        
        insertStmt = table.insert().values(name=name, group_id=group_id, tg_id=tg_id)
        await conn.execute(insertStmt)
        await conn.commit()


async def fetch_users(tg_id: BIGINT):
    async with engine.connect() as conn:
        table = users_table

        selectStmt = select(table).where(table.c.tg_id == tg_id)
        result = await conn.execute(selectStmt)
        users = result.fetchall()
        logging.info('|Db/db_functions/fetch_users| result %s', users)
        return users


async def fetch_users_in_group(group_id: int):
    async with engine.connect() as conn:
        table = users_table

        selectStmt = select(table).where(table.c.group_id == group_id)
        result = await conn.execute(selectStmt)
        users = result.fetchall()
        logging.info('|Db/db_functions/fetch_users_in_group| result %s', users)
        return users


async def delete_user(tg_id: int):
    async with engine.connect() as conn:
        table = users_table

        deleteStmt = table.delete().where(table.c.tg_id == tg_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info(f'|Db/db_functions/delete_user| user with tg_id {tg_id} deleted')


async def delete_users_by_group_id(group_id: int):
    async with engine.connect() as conn:
        table = users_table
        
        deleteStmt = table.delete().where(table.c.group_id == group_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_functions/delete_users_by_group_id| complited")