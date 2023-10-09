import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from aiogram.dispatcher import FSMContext
from config import bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import general
from Db import db_functions as db
from Db import paginator_db_function as paginator


logger = logging.getLogger('[LOG-TagSystem]')
INTERNAL_ERROR_MSG = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"

cancel_btn = InlineKeyboardButton("Закрыть", callback_data="cancel_tag_system")


class States(StatesGroup):
    PROCESS = State()          # state to use menu


async def button_imitation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Нажми",
                         reply_markup=InlineKeyboardMarkup()
                         .add(InlineKeyboardButton("Вызвать меню", callback_data="start_tag_system"),
                              cancel_btn))


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    """Updates data of state and invokes `invoke_tag_system` function"""
    logger.info("Tag system started")
    await callback_query.answer()
    await state.finish()
    # update group_id data
    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        await state.update_data(group_id = group_id)
        logger.info(f"Updated data with `group_id` {group_id}")
    except Exception as ex:
        logger.exception("Exception while updating group_id")
        logger.warning("Update group_id state error")
        await bot.send_message(callback_query.from_user.id, INTERNAL_ERROR_MSG)
        await state.finish()
        return
    await States.PROCESS.set()
    await invoke_tag_system(callback_query, state)


async def invoke_tag_system(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None, mode = "tag", page_number = 1, items_per_page = 2):
    #  \nIf callback data is common_tag_system_switch_tag: `cts_swt:<tag_id>:<mode>:<page_number>`
    """Callback data has the following parameters:
        \nIf callback data is common_tag_system_switch_tag: `cts_swt:<tag_id>:<mode>:<page_number>`
        \n mode: tag/msg
       """
    logger.info("> Tag system function invoked")

    if callback_query.data.startswith("cts_swt"):
        parameters = callback_query.data.split(":")
        if parameters[1] != "root" or tag_id != None:
            tag_id = int(parameters[1])
        else:
            tag_id = None
        mode = parameters[2]
        page_number = int(parameters[3])
        await callback_query.answer()

    logger.info(f"tag_id:{tag_id}, mode:{mode}, page_number:{page_number}")

    if mode == "tag":
        await tag_system_show_tags(callback_query, state, tag_id, mode, page_number, items_per_page)
    elif mode == "msg":
        await tag_system_show_messages(callback_query, state, tag_id, mode, page_number, items_per_page)


async def tag_system_show_tags(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None, mode = "tag", page_number = 1, items_per_page = 10):
    """Show a list of tags with paginator"""

    logger.info("tag_system_show_tags invoked")

    try:
        async with state.proxy() as data:
            group_id = data.get("group_id")
    except Exception:
        logger.warning("Can not get group_id")
        await state.finish()
        return
    
    markup = InlineKeyboardMarkup()
    message_text = ""

    err, message_text = await get_message_common_info(callback_query, state, tag_id, markup, group_id, mode)
    if err:
        return

    # should use function to get current page_number of tags
    try:
        tags, is_first_page, is_last_page = await paginator.fetch_tags_with_pagination(page_number, items_per_page, group_id, tag_id)
    except Exception:
        logger.exception("Except inside tags paginator")
        await state.finish()
        return
    
    # creating paginator btns ⬅️➡️
    left_arrow_unicode = "«"
    right_arrow_unicode = "»"
    previous_page = InlineKeyboardButton(f"{left_arrow_unicode}",
                                         callback_data=f"cts_swt:{tag_id}:{mode}:{page_number - 1}")
    next_page = InlineKeyboardButton(f"{right_arrow_unicode}",
                                         callback_data=f"cts_swt:{tag_id}:{mode}:{page_number + 1}")
    if is_first_page and not is_last_page:
        markup.add(next_page)
    elif not is_first_page and not is_last_page:
        markup.add(previous_page, next_page)
    elif not is_first_page and is_last_page:
        markup.add(previous_page)  

    # ✉️
    folder_emoji = '📁'
    for tag in tags:
        markup.add(
            InlineKeyboardButton(
                f"{folder_emoji}|{tag[2]}",
                callback_data=f"cts_swt:{tag[0]}:tag:1"
            ))

    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=message_text,
                                    reply_markup=markup,
                                    parse_mode=ParseMode.MARKDOWN)
        logger.info("Tags list were sent to user")
    except Exception as ex:
        logger.warning("Can not send a message to user with tags list")
        await bot.send_message(callback_query.from_user.id, INTERNAL_ERROR_MSG)
        await state.finish()


async def tag_system_show_messages(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None, mode = "tag", page_number = 1, items_per_page = 10):
    logger.info("tag_system_show_messages invoked" )
    logger.info(f"{tag_id} {mode} {page_number}")
    # getting a group_id from state data
    try:
        async with state.proxy() as data:
            group_id = data.get("group_id")
    except Exception:
        logger.warning("Can not get group_id")
        await state.finish()
        return
    
    markup = InlineKeyboardMarkup()
    message_text = ""

    err, message_text = await get_message_common_info(callback_query, state, tag_id, markup, group_id, mode)
    if err:
        return

    # should use function to get current page_number of tags
    try:
        messages, is_first_page, is_last_page = await paginator.fetch_messages_with_pagination(page_number, items_per_page, group_id, tag_id)
        pass
    except Exception:
        logger.exception("Except inside tags paginator")
        await state.finish()
        return
    
    # creating paginator btns
    left_arrow_unicode = "⬅️"
    right_arrow_unicode = "➡️"
    previous_page = InlineKeyboardButton(f"{left_arrow_unicode}",
                                         callback_data=f"cts_swt:{tag_id}:{mode}:{page_number - 1}")
    next_page = InlineKeyboardButton(f"{right_arrow_unicode}",
                                         callback_data=f"cts_swt:{tag_id}:{mode}:{page_number + 1}")
    if is_first_page and not is_last_page:
        markup.add(next_page)
    elif not is_first_page and not is_last_page:
        markup.add(previous_page, next_page)
    elif not is_first_page and is_last_page:
        markup.add(previous_page)  

    # 📁
    message_emoji = '✉️'
    for message in messages:
        markup.add(
            InlineKeyboardButton(
                f"{message_emoji}|{message[2]}",
                # !!! SHOULD ADD A SEND MESSAGE FUNCTION
                callback_data="qwerty"
            ))

    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=message_text,
                                    reply_markup=markup,
                                    parse_mode="Markdown")
        logger.info("Messages list were sent to user")
    except Exception as ex:
        logger.warning("Can not send a message to user with messages list")
        await bot.send_message(callback_query.from_user.id, INTERNAL_ERROR_MSG)
        await state.finish()


async def get_message_common_info(callback_query: types.CallbackQuery, state: FSMContext, tag_id: int, markup: InlineKeyboardMarkup, group_id: int, mode):
    """Returns error_bool, message_text
    \n Also this function add a cancel, to parent tag, change mode buttons
    """
    # ✉️|📁|
    TAG_MODE = "tag"
    MSG_MODE = "msg"
    CHANGED_MODE = MSG_MODE if mode == TAG_MODE else TAG_MODE
    CHANGE_MODE_TEXT = "Увидеть сообщения" if mode == TAG_MODE else "Увидеть теги"
    BUTTON_TAG_ID = "root" if tag_id == None else tag_id
    CHANGE_MODE_BTN = InlineKeyboardButton(CHANGE_MODE_TEXT, callback_data=f"cts_swt:{BUTTON_TAG_ID}:{CHANGED_MODE}:1")

    logger.info(f"get_message_common_info tag_id:{tag_id}, group id:{group_id}, mode:{mode}")

    # getting a current tag
    if tag_id == None:
        message_text = "*Сейчас вы находитесь в корневом теге*"
        markup.add(cancel_btn)

        # creating a button to change a view mode        
        markup.add(CHANGE_MODE_BTN)
        return False, message_text
    else:
        try:
            current_tag = await db.fetch_tag_by_id_group_id(tag_id, group_id)
            logger.info("Got current tag")
        except Exception as ex:
            logger.warning("Can not get current tag by id")
            await state.finish()
            return True, ""
        
        # check if tag have deleted or missed
        if current_tag == None:
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            await bot.send_message(callback_query.message.chat.id, "Выбранный тег скорее всего был удален")
            await state.finish()
            return True, ""
        
        # check if current tag is a root tag
        if current_tag[-1] == None:
            new_tag_id = "root"
        else:
            new_tag_id = current_tag[-1]

        # adding `go to parent` button
        message_text = f"Сейчас вы находитесь в теге\n*{current_tag[2]}*:\n"
        markup.add(cancel_btn, InlineKeyboardButton("\U00002934 К родительскому тегу", callback_data=f"cts_swt:{new_tag_id}:{mode}:1"))
        
        markup.add(CHANGE_MODE_BTN)
        return False, message_text


async def cancel_tag_system(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info("Cancel button pressed")
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, "Вы отменили текущее действие. В случае необходимости \nнажмите на > /help < Или напишите эту команду в чат")
        await state.finish()
    except Exception:
        await state.finish()


async def tag_system_not_available(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()


def tag_system_handlers(dp: Dispatcher):
    dp.register_message_handler(button_imitation, commands=['tag_menu'])
    dp.register_callback_query_handler(cancel_tag_system, lambda c: c.data == "cancel_tag_system", state="*")
    dp.register_callback_query_handler(start, lambda c: c.data.startswith("start_tag_system"), state="*")
    dp.register_callback_query_handler(invoke_tag_system, lambda c: c.data.startswith("cts_swt"), state=States.PROCESS)
