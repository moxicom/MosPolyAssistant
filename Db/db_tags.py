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

async def fetch_tags(group_id: int):
    """Returns array of tags name"""
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table)
        result = await conn.execute(selectStmt)
        rows = result.fetchall()
        return [row[2] for row in rows]
    

async def get_tag_id_by_name(tag_name: str, group_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('tags', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))

        select_stmt = select(table).where(and_(table.c.name == tag_name, table.c.group_id == group_id))
        result = await conn.execute(select_stmt)
        row = result.fetchone()

        if row:
            return row[0]
        else:
            return None
        
        
async def get_tags_by_parent_id(parent_id: int, group_id: int):
    """Returns an array of tags that have (id, group_id, name, parent_id)"""
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('tags', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        select_stmt = select(table).where(and_(table.c.parent_id == parent_id, table.c.group_id == group_id))
        result = await conn.execute(select_stmt)
        tags = result.fetchall()
        return tags

async def insert_tags(group_id: int, name: str, parent_id: int):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        insertStmt = table.insert().values(group_id=group_id, name=name, parent_id=parent_id)
        await conn.execute(insertStmt)
        await conn.commit()


async def fetch_tag_by_id(current_tag_id: int):
    """Returns a tag that have (id, group_id, name, parent_id)"""
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table).where(table.c.id == current_tag_id)
        result = await conn.execute(selectStmt)
        tag = result.fetchone()
        return tag


async def fetch_tag_by_id_group_id(current_tag_id: int, group_id: int):
    """Returns a tag that have (id, group_id, name, parent_id)"""
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table).where(and_(table.c.id == current_tag_id, table.c.group_id == group_id))
        result = await conn.execute(selectStmt)
        tag = result.fetchone()
        return tag


async def fetch_tag_by_name(group_id: int, name: str):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        selectStmt = select(table).where(table.c.group_id == group_id, table.c.name == name)
        result = await conn.execute(selectStmt)
        tag = result.fetchone()
        return tag

async def delete_tags_by_group_id(group_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        deleteStmt = table.delete().where(table.c.group_id == group_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_tags/delete_tags_by_group_id| complited")

async def delete_tag_by_tag_id(tag_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        deleteStmt = table.delete().where(table.c.id == tag_id)
        await conn.execute(deleteStmt)
        await conn.commit()
        logging.info("|Db/db_tags/delete_tag_by_tag_id| complited")

async def update_parent_id(tag_id: int, new_parent_id: int):
    """Updates the parent_id of a tag with the specified tag_id."""
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("tags", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('group_id', Integer),
                      Column('name', VARCHAR),
                      Column('parent_id', Integer))
        update_stmt = (
            table.update()
            .where(table.c.id == tag_id)
            .values(parent_id=new_parent_id)
        )
        await conn.execute(update_stmt)
        await conn.commit()