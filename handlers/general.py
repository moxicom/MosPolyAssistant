import asyncio
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
        print('EXCEPTION: ' + ex)
