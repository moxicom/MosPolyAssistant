import logging

from Db import db_users as db_users
from Db import db_groups_members as db_groups_members

async def check_user_existence(tg_id: int) -> bool:
    try:
        fetch_user = await db_users.fetch_users(tg_id=tg_id)
        if (len(fetch_user) == 0):
            return False
        else:
            return True
    except Exception as ex:
        logging.warning('|general/check_user_existence| EXCEPTION: ' + str(ex))
        return False


async def get_group_id_by_tg_id(tg_id: int):
    try:
        fetch_user = await db_users.fetch_users(tg_id=tg_id)
        return int(fetch_user[0][2])
    except Exception as ex:
        logging.warning('|general/get_group_id_by_tg_id| EXCEPTION: ' + str(ex))


async def get_role_by_tg_id(tg_id: int):
    try:
        fetch_user = await db_users.fetch_users(tg_id=tg_id)
        # Check if user exists in db
        if len(fetch_user) == 0:
            return -1
        # !! FIXED PARAMETER BELOW, CHECK FOR BUGS
        fetch_group_members = await db_groups_members.fetch_groups_members(group_id=fetch_user[0][2], member_id=fetch_user[0][0])
        role = -1
        for member in fetch_group_members:
            if member[1] == fetch_user[0][0]:
                role = member[3]
        return role
    except Exception as ex:
        logging.warning('|general/get_role_by_tg_id| EXCEPTION: ' + str(ex))


async def get_group_name_by_tg_id(tg_id: int):
    pass
