import asyncio
import logging
from aiogram import types

from Db import db_functions as db


async def check_user_existence(tg_id: int) -> bool:
    try:
        fetch_user = await db.fetch_users(tg_id=tg_id)
        if (len(fetch_user) == 0):
            return False
        else:
            return True
    except Exception as ex:
        logging.warning('EXCEPTION: ' + str(ex))


async def get_group_id_by_tg_id(tg_id: int):
    try:
        fetch_user = await db.fetch_users(tg_id=tg_id)
        return int(fetch_user[0][2])
    except Exception as ex:
        logging.warning('EXCEPTION: ' + str(ex))


async def get_role_by_tg_id(tg_id: int):
    try:
        fetch_user = await db.fetch_users(tg_id=tg_id)
        fetch_group_members = await db.fetch_groups_members(group_id=fetch_user[0][2])
        role = None
        for member in fetch_group_members:
            if member[1] == fetch_user[0][0]:
                role = member[3]
        return role
    except Exception as ex:
        logging.warning('EXCEPTION: ' + str(ex))


async def get_group_name_by_tg_id(tg_id: int):
    pass
