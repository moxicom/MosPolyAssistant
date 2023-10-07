import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from config import bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import general
from Db import db_functions as db
from Db import paginator_db_function as paginator


logger = logging.getLogger('[LOG-TagSystem]')
internal_error_msg = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"

cancel_btn = InlineKeyboardButton("Отмена", callback_data="cancel_tag_system")

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
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        await state.finish()
        return
    await States.PROCESS.set()
    await invoke_tag_system(callback_query, state)


async def invoke_tag_system(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None, mode = "tag", page_number = 1, items_per_page = 10):
    #  \nIf callback data is common_tag_system_switch_tag: `cts_swt:<tag_id>:<mode>:<page_number>`
    """Callback data has the following parameters:
        \nIf callback data is common_tag_system_switch_tag: `cts_swt:<tag_id>:<mode>:<page_number>`
        \n mode: tag/msg
       """
    logger.info("> Tag system function invoked")

    if callback_query.data.startswith("cts_swt"):
        parameters = callback_query.data.split(":")
        if parameters[1] != "root":
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
    logger.info("tag_system_show_tags invoked")

    try:
        async with state.proxy() as data:
            group_id = data.get("group_id")
    except Exception:
        logger.warning("Can not get group_id")
        await state.finish()
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(cancel_btn)
    message_text = ""

    err, message_text = await get_message_common_info(state, tag_id, markup, group_id, mode)
    if err:
        return

    # should use function to get current page_number of tags
    try:
        tags, is_first_page, is_last_page = await paginator.fetch_tags_with_pagination(page_number, items_per_page, group_id, tag_id)
    except Exception:
        logger.exception("Except inside tags paginator")
        await state.finish()
        return
    
    # creating paginator btns
    paginator_btns = []
    
    for tag in tags:
        markup.add(
            InlineKeyboardButton(
                tag[2],
                callback_data=f"cts_swt:{tag[0]}:tag:1"
            ))

    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=message_text,
                                    reply_markup=markup,
                                    parse_mode="Markdown")
        logger.info("Tags list were sent to user")
    except Exception as ex:
        logger.warning("Can not send a message to user with tags list")
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        await state.finish()


async def tag_system_show_messages(callback_query: types.CallbackQuery, state: FSMContext, tag_id = None, mode = "tag", page_number = 1, items_per_page = 10):
    pass


async def get_message_common_info(state: FSMContext, tag_id: int, markup: InlineKeyboardMarkup, group_id: int, mode):
    """Returns error_bool, message_text"""
    logger.info(f"get_message_common_info tag_id:{tag_id}, group id:{group_id}, mode:{mode}")
    if tag_id == None:
        message_text = "*Сейчас вы находитесь в корневом теге*"
        return False, message_text
    else:
        try:
            current_tag = await db.fetch_tag_by_id_group_id(tag_id, group_id)
            logger.info("Got current tag")
        except Exception as ex:
            logger.warning("Can not get current tag by id")
            await state.finish()
            return True, ""
        
        if current_tag[-1] == None:
            new_tag_id = "root"
        else:
            new_tag_id = current_tag[-1]

        message_text = f"*Сейчас вы находитесь в теге* _'{current_tag[2]}'_ .\n"
        markup.add(InlineKeyboardButton("< К родительскому тегу", callback_data=f"cts_swt:{new_tag_id}:{mode}:1"))
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
