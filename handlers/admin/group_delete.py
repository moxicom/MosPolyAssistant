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
    DELETE_FROM_GROUP_MEMBERS = State()
    DELETE_FROM_USERS = State()
    DELETE_FROM_FILES = State()
    DELETE_FROM_IMAGES = State()
    DELETE_FROM_MESSAGES = State()
    DELETE_FROM_TAGS = State()
    DELETE_FROM_GROUP_INFO = State()

internal_error_msg = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"

def cancel_button_markup():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Отменить", callback_data="cancel"))


async def group_delete_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Checking the administrator password. If true, starts the delete process."""
    logging.info("group_delete_start")
    markup = ReplyKeyboardRemove()
    logging.info("Started password check to delete a group")
    await state.finish()
    # use answer_callback_query to stop button infinite load in Telegram client
    await bot.answer_callback_query(callback_query.id)

    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        await state.update_data(group_id = group_id)
        logging.info("Updated data with `group_id`")
    except Exception as ex:
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        logging.warning("Update group_id state error")
        await state.finish()
        return

    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Для удаления группы введите текущий пароль:",
                                    reply_markup=InlineKeyboardMarkup()
                                    .add(InlineKeyboardButton("Отмена", callback_data="cancel_tag"))
                                    )
    except Exception as ex:
        print("\t[LOG] Receiving password from user ERROR")
        await bot.send_message(chat_id=callback_query.from_user.id, text=internal_error_msg)
        logging.warning(f"group_delete_start func exception: {ex}")
        await state.finish()
        return

    await States.PASSWORD_CHECK.set()

async def password_check(message: types.Message, state: FSMContext):   
    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=message.from_user.id)
        group_info_fetch = await db.fetch_group_info_by_id(group_id)

        logging.info('Password_check to delete group %s', group_info_fetch[0])

        if hashlib.sha256(message.text.encode()).hexdigest() == group_info_fetch[0][2]:
            await message.answer('Пароль верный')
            # Saving information in the database about new user
            await state.()
        else:
            await message.answer('Пароль неверный')
            await state.finish()
    except Exception as ex:
        await message.reply(internal_error_msg)
        logging.warning('An error has occurred: ' + str(ex))
        await state.finish()

    """Updates the data of state: `user_text=message.text`. Await a `confirm_message` func. Receive messages with `States.MESSAGE` state"""
    # Save the user's message into the state
    try:
        await state.update_data(user_text=message.text)
        logging.info("state updated: user_text set")
    except Exception as ex:
        logging.debug("ERROR TO UPDATE state data")
        await message.answer(internal_error_msg)
        await state.finish()
        return

    # Call the confirm_message function to validate the message
    try:
        await confirm_message(message, state)
    except Exception as ex:
        await message.answer(internal_error_msg)
        await state.finish()
        return

async def confirm_message(message: types.Message, state: FSMContext):
    

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Да", callback_data="admin-tag-confirm_msg_yes"))
    markup.add(InlineKeyboardButton("Нет", callback_data="admin-tag-confirm_msg_no"))
    try:
         await message.reply("Вы уверены что хотите удалить группу? (Все сообщения, теги, файлы будут удалены)", reply_markup=markup)
    except Exception as ex:
        await message.answer(internal_error_msg)
        await state.finish()
        return
    await States.DELETE_FROM_GROUP_MEMBERS.set()

async def confirm_msg_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # await ask_for_tag(callback_query.message, state)
    await ask_for_tag(callback_query, state)
    # !!!! MAKE THERE `ПОСМОТРЕТЬ ВСЕ ТЕГИ BTN`


async def confirm_msg_no(callback_query: types.CallbackQuery, state: FSMContext):
    """Stop group delete"""
    state.finish()
    bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Вот что ты можешь сделать", reply_markup=keyboards.admin_functions_mkp)


def group_delete_handlers(dp: Dispatcher):
    dp.register_message_handler(password_check, state=States.PASSWORD_CHECK)

    # message text confirm result funcs
    dp.register_callback_query_handler(confirm_msg_yes, lambda c: c.data == "admin-tag-confirm_msg_yes", state=States.CONFIRM)
    dp.register_callback_query_handler(confirm_msg_no, lambda c: c.data == "admin-tag-confirm_msg_no", state=States.CONFIRM) 
    
    dp.register_callback_query_handler(group_delete_start, lambda c: c.data == "group_delete", state="*")

    #dp.register_callback_query_handler(text='group_delete', callback=group_delete_start, state='*')