from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, Table, MetaData, VARCHAR, Date, and_
from sqlalchemy.orm import declarative_base as base
import asyncio
from sqlalchemy import update

# myBase = base()
engine = asyncio_ext.create_async_engine(
    "postgresql+asyncpg://postgres:1234@localhost:5432/mydatabase",
    echo=False,
    future=True
)
# engine = asyncio_ext.create_async_engine(
#     "postgresql+asyncpg://postgres:314159@localhost:5432/postgres",
#     echo=False,
#     future=True
# )

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


########################### users #######################
async def insert_users(name: VARCHAR, group_id: int, tg_id: int):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table('users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR),
                      Column('group_id', Integer),
                      Column('tg_id', Integer))
        insertStmt = table.insert().values(name=name, group_id=group_id, tg_id=tg_id)
        await conn.execute(insertStmt)
        await conn.commit()


async def fetch_users(tg_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR),
                      Column('group_id', Integer),
                      Column('tg_id', Integer))
        selectStmt = select(table).where(table.c.tg_id == tg_id)
        result = await conn.execute(selectStmt)
        users = result.fetchall()
        print('----------------\n fetch_users result\n ', users, '\n-------------------')
        return users


async def fetch_users_in_group(group_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR),
                      Column('group_id', Integer),
                      Column('tg_id', Integer))
        selectStmt = select(table).where(table.c.group_id == group_id)
        result = await conn.execute(selectStmt)
        users = result.fetchall()
        print('----------------\n fetch_users_in_group result\n ', users, '\n-------------------')
        return users


async def delete_users(tg_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR),
                      Column('group_id', Integer),
                      Column('tg_id', Integer))
        deleteStmt = table.delete().where(table.c.tg_id == tg_id)
        await conn.execute(deleteStmt)
        await conn.commit()


########################### groups_info #################
async def insert_groups_info(group_name: VARCHAR, password: VARCHAR):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("groups_info", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(50)),
                      Column('password', VARCHAR))
        insertStmt = table.insert().values(name=group_name, password=password)
        await conn.execute(insertStmt)
        await conn.commit()
        print('--------------' + 'groups info commited' + '------------')


async def fetch_groups_info(group_name: VARCHAR):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("groups_info", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(50)),
                      Column('password', VARCHAR))
        selectStmt = select(table).where(table.c.name == group_name)
        result = await conn.execute(selectStmt)
        group_info = result.fetchall()
        print('--------------------------\n fetch_groups_info result = \n', group_info, '\n--------------------------')
        return group_info


async def fetch_group_info_by_id(group_id: int):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("groups_info", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(50)),
                      Column('password', VARCHAR))
        selectStmt = select(table).where(table.c.id == group_id)
        result = await conn.execute(selectStmt)
        group_info = result.fetchone()
        print('--------------------------\n fetch_group_info_by_id result = \n', group_info,
              '\n--------------------------')
        return group_info if group_info else None


async def change_group_info(id: int, field: str, new_value: str):
    """Изменение параметра в базе данных по id"""
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table('groups_info', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', VARCHAR(20)),
                      Column('password', VARCHAR(20))
                      )

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
            print('--------------' + 'group info changed' + '------------')
            return 0

        except:
            return -1


###########################  groups_members ####################
async def insert_groups_members(member_id: int, group_id: int, role: int):
    async with engine.begin() as conn:
        metadata = MetaData()
        table = Table("groups_members", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('member_id', Integer),
                      Column('group_id', Integer),
                      Column('role', Integer))
        insertStmt = table.insert().values(member_id=member_id, group_id=group_id, role=role)
        await conn.execute(insertStmt)
        await conn.commit()


async def fetch_groups_members(group_id: int = -1, member_id: int = -1):
    async with engine.connect() as conn:
        metadata = MetaData()
        table = Table("groups_members", metadata,
                      Column('id', Integer, primary_key=True),
                      Column('member_id', Integer),
                      Column('group_id', Integer),
                      Column('role', Integer))

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
        print('-' * 15 + '\n\t fetch_groups_members result = \n\t', group_members, '\n' + '-' * 15)
        return group_members


async def fetch_tags(group_id: int):
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


########################### tags ########################
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


########################### messages ####################
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

# async def fetch_users(group_id: int):
#     async with engine.connect() as conn:
#         metadata = MetaData()
#         table = Table("users", metadata,
#                         Column('id', Integer, primary_key=True),
#                         Column('name', VARCHAR),
#                         Column('group_id', Integer),
#                         Column('tg_id', Integer))
#         selectStmt = select(table).where(table.c.group_id == group_id)
#         result = await conn.execute(selectStmt)
#         users = result.fetchall()
#         print('--------------------------\n', users, '\n--------------------------')
#         return users

# async def delete_users(tg_id: int):
#     async with engine.connect() as conn:
#         metadata = MetaData()
#         table = Table('users', metadata,
#                         Column('id', Integer, primary_key=True),
#                         Column('name', VARCHAR),
#                         Column('group_id', Integer),
#                         Column('tg_id', Integer))
#         deleteStmt = table.delete().where(table.c.tg_id == tg_id)
#         await conn.execute(deleteStmt)
#         await conn.commit()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(insert_groups_info(name='qwe', password='zxc'))
# loop.run_until_complete(insert_users("qwe", 1, 22))
