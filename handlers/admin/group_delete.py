import hashlib
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import bot
from keyboards import main_keyboards as keyboards
from Db import db_functions as db
from handlers import general


class States(StatesGroup):
    PASSWORD_CHECK = State()
    CONFIRM_DELETE = State()
    DELETE_GROUP = State()
    

internal_error_msg = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"

def cancel_button_markup():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Отменить", callback_data="cancel"))


async def group_delete_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Checking the administrator password. If true, starts the delete process."""
    logging.info("|group_delete/group_delete_start| Password verification started")
    markup = ReplyKeyboardRemove()
    # use answer_callback_query to stop button infinite load in Telegram client
    # await bot.answer_callback_query(callback_query.id)

    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        await state.update_data(group_id = group_id)

        logging.info("|group_delete/group_delete_start| Updated data with `group_id`")
    except Exception as ex:
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        logging.warning("|group_delete/group_delete_start| Update group_id state error " + str(ex))
        await state.finish()
        return

    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Для удаления группы введите текущий пароль:",
                                    reply_markup=InlineKeyboardMarkup()
                                    .add(InlineKeyboardButton("Отмена", callback_data="cancel_tag"))
                                    )
        # We save the id of the current message for subsequent deletion of markup
        await state.update_data(prev_bot_message_id = callback_query.message.message_id)
    except Exception as ex:
        logging.warning("|group_delete/group_delete_start| Receiving password from user ERROR")
        await bot.send_message(chat_id=callback_query.from_user.id, text=internal_error_msg)
        logging.warning(f"group_delete_start func exception: {ex}")
        await state.finish()
        return

    await States.PASSWORD_CHECK.set()

async def password_check(message: types.Message, state: FSMContext):   
    try:
        async with state.proxy() as data:
            # Deleting the markup of the previous message
            prev_bot_message_id = data['prev_bot_message_id']
            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=prev_bot_message_id,
                                    reply_markup=None)

        group_id = await general.get_group_id_by_tg_id(tg_id=message.from_user.id)
        await state.update_data(group_id = group_id)
        logging.info("|group_delete/password_check| Updated data with `group_id`")

        group_info_fetch = await db.fetch_group_info_by_id(group_id)
        logging.info('|group_delete/password_check| Password_check to delete group %s', group_info_fetch)
        
    except Exception as ex:
        await bot.send_message(message.from_user.id, internal_error_msg)
        logging.warning("|group_delete/password_check| Update group_info error " + str(ex))
        await state.finish()
        return

    try:
        if hashlib.sha256(message.text.encode()).hexdigest() == group_info_fetch[2]:
            await States.CONFIRM_DELETE.set()
            await group_delete_confirm_message(message, state)
        else:
            await message.answer('Пароль неверный. Удаление группы прекращено')
            await state.finish()
            return
    except Exception as ex:
        await message.reply(internal_error_msg)
        logging.warning('|group_delete/password_check| An error has occurred: ' + str(ex))
        await state.finish()


async def group_delete_confirm_message(message: types.Message, state: FSMContext):
    """Call the group_delete_confirm_message function to validate the group delete """
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Да", callback_data="admin-group_delete-confirm_msg_yes"))
    markup.add(InlineKeyboardButton("Нет", callback_data="admin-group_delete-confirm_msg_no"))
    try:
        await message.reply("Вы уверены что хотите удалить группу? (Все сообщения, теги, файлы будут удалены)", reply_markup=markup)
    except Exception as ex:
        await message.answer(internal_error_msg)
        logging.warning('|group_delete/group_delete_confirm_message| An error has occurred: ' + str(ex))
        await state.finish()
        return

async def confirm_msg_yes(callback_query: types.CallbackQuery, state: FSMContext):
    """Start group delete"""
    try:
        await bot.answer_callback_query(callback_query.id)
        await States.DELETE_GROUP.set()
        
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Начат процесс удаления группы...", reply_markup=None)
        
    except Exception as ex:
        await callback_query.message.answer(internal_error_msg)
        logging.warning('|group_delete/confirm_msg_yes| An error has occurred: ' + str(ex))
        await state.finish()
        return
    await delete_group(callback_query, state)
    

async def confirm_msg_no(callback_query: types.CallbackQuery, state: FSMContext):
    """Stop group delete"""
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Вот что ты можешь сделать", reply_markup=keyboards.admin_functions_mkp)
    
async def delete_group(callback_query: types.CallbackQuery, state: FSMContext):
    """Search for all users in the groups_members table and delete from group_members"""
    logging.info("|group_delete/delete_group_members| group members delete start")
    async with state.proxy() as data:
        # Deleting the markup of the previous message
        group_id = data['group_id'] 
    try:
        await db.delete_group_members_by_group_id(group_id)
        await db.delete_users_by_group_id(group_id)
        #await db.delete_images_by_message_id(message_id)
        await db.delete_messages_by_group_id(group_id)
        await db.delete_tags_by_group_id(group_id)
        await db.delete_group_info_by_group_id(group_id)
    except Exception as ex:
        await callback_query.answer(internal_error_msg)
        logging.warning('|group_delete/delete_group_members| An error has occurred: ' + str(ex))
        await state.finish()
        return
    logging.info("|group_delete/delete_group_members| group members delete finished")
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Группа успешно удалена", reply_markup=None)
    #await bot.send_message(callback_query.message.from_user.id, text="Группа успешно удалена")
    await state.finish()


def group_delete_handlers(dp: Dispatcher):
    dp.register_message_handler(password_check, state=States.PASSWORD_CHECK)
    dp.register_message_handler(group_delete_confirm_message, state=States.CONFIRM_DELETE)
    dp.register_message_handler(delete_group, state=States.DELETE_GROUP)

    # message text confirm result funcs
    dp.register_callback_query_handler(confirm_msg_yes, lambda c: c.data == "admin-group_delete-confirm_msg_yes", state="*")
    dp.register_callback_query_handler(confirm_msg_no, lambda c: c.data == "admin-group_delete-confirm_msg_no", state="*") 
    
    dp.register_callback_query_handler(group_delete_start, lambda c: c.data == "group_delete", state="*")
