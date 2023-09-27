from datetime import datetime
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from config import bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import general
from Db import db_functions as db


logger = logging.getLogger('[LOG]')

internal_error_msg = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"


class States(StatesGroup):
    MESSAGE = State()           # getting a new message's text from user
    CHOOSE_ACTION = State()     # get the result of selecting a tag
    EXISTING_TAG = State()      #
    NEW_TAG = State()           #
    CONFIRM = State()           # receive the user callback of any suggestion


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    """Starts message adding process.Ask user for text of message"""
    markup = ReplyKeyboardRemove()
    logger.info("STARTED ADDING NEW MESSAGE")
    await state.finish()
    # use answer_callback_query to stop button infinite load in Telegram client
    await bot.answer_callback_query(callback_query.id)

    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        await state.update_data(group_id = group_id)
        logger.info("Updated data with `group_id`")
    except Exception as ex:
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        logger.warning("Update group_id state error")
        await state.finish()
        return

    try:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Введите ваше сообщение:",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton("Отмена", callback_data="cancel"))
                               )
    except Exception as ex:
        print("\t[LOG] SENDING MESSAGE ERROR")
        await bot.send_message(chat_id=callback_query.from_user.id, text=internal_error_msg)
        logger.warning(f"start func exception: {ex}")
        await state.finish()
        return

    await States.MESSAGE.set()


async def process_message(message: types.Message, state: FSMContext):
    """Updates the data of state: `user_text=message.text`. Await a `confirm_message` func. Receive messages with `States.MESSAGE` state"""
    # Save the user's message into the state
    try:
        await state.update_data(user_text=message.text)
        logger.info("state updated: user_text set")
    except Exception as ex:
        logger.debug("ERROR TO UPDATE state data")
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
    
    async with state.proxy() as data:
        user_text = data['user_text']

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Да", callback_data="admin-tag-confirm_msg_yes"))
        markup.add(InlineKeyboardButton("Нет", callback_data="admin-tag-confirm_msg_no"))
        markup.add(InlineKeyboardButton("Отменить", callback_data="cancel"))  # Add this line

        try:
            await message.reply("Ваше сообщение корректно?", reply_markup=markup)
        except Exception as ex:
            await message.answer("Внутренняя ошибка")
            await state.finish()
            return

        await States.CONFIRM.set()


async def confirm_msg_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await ask_for_tag(callback_query.message, state)
    # !!!! MAKE THERE `ПОСМОТРЕТЬ ВСЕ ТЕГИ BTN`


async def confirm_msg_no(callback_query: types.CallbackQuery, state: FSMContext):
    """Asks user to retype new message"""
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text="Пожалуйста, введите ваше сообщение снова.", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data="cancel")))
        await States.MESSAGE.set()
    except Exception as ex:
        logger.warning(str(ex))
        await bot.send_message(callback_query.from_user.id, "Ошибка на сервере. Попробуйте еще раз. При повторе ошибки обратитесь к администратору")
        await state.finish()


async def ask_for_tag(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Существующий тег", callback_data="admin-tag-select-existing_tag"))
    markup.add(InlineKeyboardButton("Добавить новый тег", 
    callback_data="admin-tag-create-new-tag"))
    markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))

    await message.reply("Выберете тег", reply_markup=markup)
    await States.CHOOSE_ACTION.set()


async def process_callback_existing_tag(callback_query: types.CallbackQuery, state: FSMContext):
    print('кнопка существующий тег')
    await bot.answer_callback_query(callback_query.id)
    group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
    # !!!!!!!!!!!!!!!!!!!!!!!!!
    existing_tags = await db.fetch_tags(group_id)
    # !!!!!!!!!!!!!!!!!!!!!!!!!
    if existing_tags:
        markup = InlineKeyboardMarkup(row_width=2)
        for tag in existing_tags:
            markup.add(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
        markup.add(InlineKeyboardButton("Создать новый тег", callback_data='new_tag'))
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text="Выберите тег:", reply_markup=markup)
        await States.EXISTING_TAG.set()

    else:
        await bot.answer_callback_query(callback_query.id, "Нет существующих тегов, пожалуйста, добавьте новый тег.",
                                        show_alert=True)


async def process_callback_new_tag(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text="Введите название новго тега:")
        await States.NEW_TAG.set()
        logger.info("Asking user for a new tag")
    except Exception as ex:
        await bot.send_message(callback_query.from_user.id, "Непредвиденная ошибка")
        await state.finish()
        logger.warning("Arror at tag creating process: }" + str(ex))


async def add_new_tag(message: types.Message, state: FSMContext):
    """Gets a `message.text` as a new tag and updates state data `tag=message.text`"""
    try:
        new_tag = message.text
        await state.update_data(tag=new_tag)
        await confirm_tag(message, state)
        logger.info("New tag confirmed")
    except Exception as ex:
        await state.finish()
        await message.answer("Ощибка на сервере")
        logger.info("Cannot confirm a new tag")


async def confirm_tag(message: types.Message, state: FSMContext):
    """
    Updates state with  `user_text`. Invokes when user send new tag name
    """
    async with state.proxy() as data:
        user_text = data['user_text']
        tag = data['tag']

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Да", callback_data="confirm_tag_yes"))
        markup.add(InlineKeyboardButton("Нет", callback_data="confirm_tag_no"))
        markup.add(InlineKeyboardButton("Отменить", callback_data="cancel"))
        
        try:
            await message.reply(f"Выбранный тег: {tag}\n Тег корректен?", reply_markup=markup)
        except Exception as ex:
            await message.answer("Внутренняя ошибка")
            await state.finish()
            return
    
        await States.CONFIRM.set()


async def confirm_tag_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # await confirm_full_message(callback_query.message, state)
    # Invoke a tag menu
    await invoke_tag_menu(callback_query, state)


async def confirm_tag_no(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await ask_for_tag(callback_query.message, state)


async def invoke_tag_menu(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None):
    """callback data: `switch_to_tag:{tag_id}`; `submit_tag:{tag_id}`"""

    await callback_query.answer()

    # get all child tags
    if callback_query.data.startswith("switch_to_tag"):
        tag_id = int(callback_query.data.split(":")[-1])
    try:
        async with state.proxy() as data:
            group_id = data.get("group_id")
        tags = await db.get_tags_by_parent_id(tag_id, group_id)
        logger.info("Got all tags")
    except Exception as ex:
        logger.warning("Can not get tags by parent_id")
        await state.finish()
        return

    markup = InlineKeyboardMarkup()

    # check if tag with id = tag_id is root tag
    if tag_id == None:
        tags_text = "Сейчас вы находитесь в корневом теге.\nВыберите тег из списка ниже:\n"
        markup.add(InlineKeyboardButton("Подтвердить", callback_data=f"submit_tag:Root"))
    else:
        try:
            current_tag = await db.fetch_tag_by_id_group_id(tag_id, group_id)
            logger.info("Got current tag")
        except Exception as ex:
            logger.warning("Can not get current tag by id")
            await state.finish()
            return
        tags_text = f"Сейчас вы находитесь в {current_tag[2]}.\n"
        markup.add(InlineKeyboardButton("Подтвердить", callback_data=f"submit_tag:{current_tag[0]}"))

    markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    

    #if there is no tags
    if len(tags) == 0:
        await bot.send_message(callback_query.from_user.id, tags_text + 
                         "В данный момент здесь нет тегов",
                         reply_markup=markup)
        return
    

    for tag in tags:
        tags_text += f"\t> {tag[2]}\n"
        markup.add(InlineKeyboardButton(tag[2], callback_data=f"switch_to_tag:{tag[0]}"))

    try:
        await bot.send_message(callback_query.from_user.id, tags_text, reply_markup=markup)
        logger.info("root tags were sent to user")
    except Exception as ex:
        logger.warning("Can not send a message to user with root tags")
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        await state.finish()


async def confirm_full_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_text = data['user_text']
        tag = data['tag']
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Да", callback_data="admin-tag-confirm_full_yes"))
        markup.add(InlineKeyboardButton("Нет", callback_data="admin-tag-confirm_full_no"))
        markup.add(InlineKeyboardButton("Отменить", callback_data="cancel"))  # Add this line

        try:
            await message.reply(f"Проверьте сообщение еще раз. Все верно?\n\nСообщение: {user_text}\nТег: {tag}\n",
                            reply_markup=markup)
        except Exception as ex:
            await message.answer("Внутренняя ошибка")
            await state.finish()
            return

        await States.CONFIRM.set()


async def get_tg_ids_in_group(group_id: int, exclude_tg_id: int):
    users_in_group = await db.fetch_users_in_group(group_id)
    tg_ids = [user[3] for user in users_in_group if user[3] != exclude_tg_id]
    return tg_ids


async def confirm_full_yes(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user_text = data['user_text']
        # this is a tag text (description)
        tag = data['tag']
        await bot.answer_callback_query(callback_query.id)
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)

        # Fetch all existing tags
        existing_tags = await db.fetch_tags(group_id=group_id)
        # Insert the new tag into the tags table
        if tag not in existing_tags:
            await db.insert_tags(group_id=group_id, name=tag, parent_id=None)
        tag_id = await db.get_tag_id_by_name(tag_name=tag, group_id=group_id)

        # Insert the message into the messages table
        await db.insert_messages(group_id=group_id, title=user_text, text=user_text, tag_id=tag_id, images=None,
                                 videos=None, files=None, created_at=datetime.now())

        await bot.send_message(chat_id=callback_query.from_user.id, text="Сообщение отправлено.")
        # The tg_id to exclude
        exclude_tg_id = callback_query.from_user.id
        tg_ids = await get_tg_ids_in_group(group_id, exclude_tg_id)
        for id in tg_ids:
            await bot.send_message(chat_id=id, text=tag + '\n' + user_text)
        await state.finish()


async def confirm_full_no(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Начинаем заново.")
    await start(callback_query, state)


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()


async def process_callback_actual_existing_tag(callback_query: types.CallbackQuery, state: FSMContext):
    tag = callback_query.data[4:]
    await callback_query.answer(callback_query.id)
    await state.update_data(tag=tag)
    await confirm_tag(callback_query.message, state)




def tags_handlers(dp: Dispatcher):
    dp.register_message_handler(process_message, state=States.MESSAGE)
    dp.register_message_handler(add_new_tag, state=States.NEW_TAG)
    
    dp.register_callback_query_handler(start, lambda c: c.data == "write_message", state="*")
    dp.register_callback_query_handler(process_callback_existing_tag, lambda c: c.data == "admin-tag-select-existing_tag",
                                       state=States.CHOOSE_ACTION)
    dp.register_callback_query_handler(process_callback_new_tag, lambda c: c.data == "admin-tag-create-new-tag",
                                       state=[States.CHOOSE_ACTION, States.EXISTING_TAG])

    dp.register_callback_query_handler(process_callback_actual_existing_tag, state=States.EXISTING_TAG)
    dp.register_callback_query_handler(confirm_full_yes, lambda c: c.data == "admin-tag-confirm_full_yes", state=States.CONFIRM)
    dp.register_callback_query_handler(confirm_full_no, lambda c: c.data == "admin-tag-confirm_full_no", state=States.CONFIRM)
    dp.register_callback_query_handler(confirm_tag_yes, lambda c: c.data == "confirm_tag_yes", state=States.CONFIRM)
    dp.register_callback_query_handler(confirm_tag_no, lambda c: c.data == "confirm_tag_no", state=States.CONFIRM)

    # message text confirm result funcs
    dp.register_callback_query_handler(confirm_msg_yes, lambda c: c.data == "admin-tag-confirm_msg_yes", state=States.CONFIRM)
    dp.register_callback_query_handler(confirm_msg_no, lambda c: c.data == "admin-tag-confirm_msg_no", state=States.CONFIRM) 

    # tags hierarchy
    dp.register_callback_query_handler(invoke_tag_menu, lambda c: c.data.startswith("switch_to_tag"), state=[States.CONFIRM, States.EXISTING_TAG])

    dp.register_callback_query_handler(cancel, lambda c: c.data == "cancel", state="*")  

# CALLBACKS FROM MAIN KEYBOARDS:
# change_password, list_of_group, write_message

# 
# STATES PARAMS:
# 
# 
