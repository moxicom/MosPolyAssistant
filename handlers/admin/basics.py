import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from handlers import general

from keyboards import main_keyboards as keyboards


logger = logging.getLogger('[LOG]')


async def send_all_basic_admin_commands(message: types.Message, state: FSMContext):
    """Sends a main admin keyboard to user if this user is a group admin (owner)"""
    await state.finish()
    user = message.from_user
    logger.info(f"{user.username} is trying to open admin panel")
    
    exist = await general.check_user_existence(user.id)
    if not exist:
        await message.reply("Вы не присоединены ни к одной группе")
        return
    role = await general.get_role_by_tg_id(user.id)
    if role == 2:
        try:
            await message.answer("Выбери, что ты хочешь сделать", reply_markup=keyboards.admin_functions_mkp)
            logger.info(f"keyboard send to {user.username}")
        except Exception as ex:
            logger.warning("Can not send a message with keyboard. "+ str(ex))
    else:
        await message.reply("Извини, но у тебя другие права")
        logger.info(f"{user.username} Bad role result")
            

def admin_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_all_basic_admin_commands, commands=["admin_panel"], state="*")