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

metadata = MetaData()
GROUPS_INFO_TABLE = Table("groups_info", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(50)),
                      Column('password', VARCHAR))

async def insert_groups_info(group_name: VARCHAR, password: VARCHAR):
    async with engine.begin() as conn:
        table = GROUPS_INFO_TABLE

        insertStmt = table.insert().values(name=group_name, password=password)
        await conn.execute(insertStmt)
        await conn.commit()
        logging.info('|Db/db_functions/insert_groups_info| groups info commited')

async def fetch_groups_info(group_name: VARCHAR):
    async with engine.connect() as conn:
        table = GROUPS_INFO_TABLE

        selectStmt = select(table).where(table.c.name == group_name)
        result = await conn.execute(selectStmt)
        group_info = result.fetchall()
        logging.info('|Db/db_functions/fetch_groups_info| result %s', group_info)
        return group_info


async def fetch_group_info_by_id(group_id: int):
    async with engine.connect() as conn:
        table = GROUPS_INFO_TABLE

        selectStmt = select(table).where(table.c.id == group_id)
        result = await conn.execute(selectStmt)
        group_info = result.fetchone()
        logging.info('|Db/db_functions/fetch_group_info_by_id| result %s', group_info)
        return group_info if group_info else None


async def change_group_info(id: int, field: str, new_value: str):
    """Изменение параметра в базе данных по id"""
    async with engine.connect() as conn:
        table = GROUPS_INFO_TABLE

        # Проверка на наличие значения в параметре id
        stmt = select(table).where(table.c.id == id)
        result = await conn.execute(stmt)
        rows = result.fetchall()
        if not rows:
            return -1

        # Внесение изменений
        try:
            update_stmt = table.update().where(table.c.id == id).values({field: new_value})
            await conn.execute(update_stmt)
            await conn.commit()
            logging.info('|Db/db_functions/change_group_info| group info changed')
            return 0

        except:
            return -1


async def delete_group_info_by_group_id(group_id: int):
    async with engine.connect() as conn:
        table = GROUPS_INFO_TABLE

        deleteStmt = table.delete().where(table.c.id == group_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_functionsdelete_group_info_by_group_id| complited")