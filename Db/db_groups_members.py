from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, BIGINT, and_
from sqlalchemy.orm import declarative_base as base
import logging
from sqlalchemy import update
from Db.postgres import engine, group_members_table


async def insert_groups_members(member_id: int, group_id: int, role: int):
    async with engine.begin() as conn:
        table = group_members_table

        insertStmt = table.insert().values(member_id=member_id, group_id=group_id, role=role)
        await conn.execute(insertStmt)
        await conn.commit()


async def fetch_groups_members(group_id: int = -1, member_id: int = -1):
    async with engine.connect() as conn:
        table = group_members_table

        if (group_id == -1 and member_id != -1):
            selectStmt = select(table).where(table.c.member_id == member_id)
        elif (group_id != -1 and member_id != -1):
            selectStmt = select(table).where(table.c.group_id == group_id, table.c.member_id == member_id)
        elif (group_id != -1 and member_id == -1):
            selectStmt = select(table).where(table.c.group_id == group_id)
        else:
            return Exception("NO ARGS")

        result = await conn.execute(selectStmt)
        group_members = result.fetchall()
        logging.info('|Db/db_functions/fetch_groups_members| result %s', group_members)
        return group_members


async def delete_group_members_by_group_id(group_id: int):
    async with engine.connect() as conn:
        table = group_members_table

        deleteStmt = table.delete().where(table.c.group_id == group_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_functions/delete_group_members_by_group_id| complited")


async def delete_group_member(id: int):
    async with engine.connect() as conn:
        table = group_members_table

        deleteStmt = table.delete().where(table.c.member_id == id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_functions/delete_group_member| complited")