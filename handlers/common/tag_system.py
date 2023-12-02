import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from aiogram.dispatcher import FSMContext
from config import bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import general
from Db import db_tags as db_tags
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
    # set standart view_mode
    await state.update_data(view_mode = 'default')
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
        # Checking for the current view_mode, it depends on what happens when you click on the tag
        # default, move_tag_step_2 - standard behavior
        # move_tag - clicking on the tag activates the 2nd stage of the tag movement function
        async with state.proxy() as data:
            if data['view_mode'] == 'default':
                callback_mode = f"cts_swt:{tag[0]}:tag:1"
            # Move tags  
            elif data['view_mode'] == 'move_tag':
                callback_mode = f"move_tag:{tag[0]}:step_2"
            elif data['view_mode'] == 'move_tag_step_2':
                # "Hides" the tag so that it is impossible to move the tag into itself
                if tag[0] == int(data['moving_tag_id']):
                    continue
                else:
                    callback_mode = f"cts_swt:{tag[0]}:tag:1"
            # Delete tag
            elif data['view_mode'] == 'delete_tag':
                callback_mode = f'delete_tag:{tag[0]}:confirm:{tag[2]}'
            # Rename tag
            elif data['view_mode'] == 'rename_tag':
                callback_mode = f'rename_tag:{tag[0]}:selected:{tag[2]}'
            markup.add(
                InlineKeyboardButton(
                    f"{folder_emoji}|{tag[2]}",
                    callback_data=callback_mode
                ))

    logger.info('message_text ' + message_text)
    try:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=message_text,
                                    reply_markup=markup,
                                    parse_mode=ParseMode.MARKDOWN)
        logger.info("Tags list were sent to user")
    except Exception as ex:
        logger.warning("Can not send a message to user with tags list || "+ str(ex))
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
                callback_data=f"receive_message_by_id:{message[0]}"
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
    

    # Canceling any operations with tags and messages. Setting the default view_mode
    BACK_BTN = InlineKeyboardButton('Отменить', callback_data="cancel_operation_tag")

    # Move tags
    MOVE_TAG_BTN = InlineKeyboardButton('Переместить тег', callback_data=f"move_tag:{BUTTON_TAG_ID}:step_1")
    PASTE_TAG_BTN = InlineKeyboardButton('Вставить в текущий тег', callback_data=f"move_tag:{BUTTON_TAG_ID}:step_3")

    # Delete tag
    DELETE_TAG_BTN = InlineKeyboardButton('Удалить тег', callback_data=f"delete_tag:{BUTTON_TAG_ID}:select_tag")
    
    # Rename tag
    RENAME_TAG_BTN = InlineKeyboardButton('Переименовать тег', callback_data=f"rename_tag:{BUTTON_TAG_ID}:select_tag")

    logger.info(f"get_message_common_info tag_id:{tag_id}, group id:{group_id}, mode:{mode}")

    # getting a current tag
    if tag_id == None:
        message_text = "*Сейчас вы находитесь в корневом теге*"
        markup.add(cancel_btn)

        # Checking the view_mode, the display of different buttons is dependent on it
        async with state.proxy() as data:
            # Basic functionality buttons
            if data['view_mode'] == 'default':
                markup.add(CHANGE_MODE_BTN)

                # Show all avalable functional
                if mode == TAG_MODE:
                    markup.add(MOVE_TAG_BTN, DELETE_TAG_BTN)
                    markup.add(RENAME_TAG_BTN)
                logger.info("view_mode' == 'default")

            # Buttons that depend on the context of the operation
            else:
                markup.add(BACK_BTN)
                # Move tags
                if data['view_mode'] == 'move_tag':
                    message_text += "\nВыберите тег для перемещения"
                    logger.info("view_mode' == 'move_tag")
                elif data['view_mode'] == 'move_tag_step_2':
                    logger.info("view_mode' == 'move_tag_step_2")
                    message_text += "\nВыберите тег для вставки"
                    markup.add(PASTE_TAG_BTN)
                # Delete tags
                elif data['view_mode'] == 'delete_tag':
                    message_text += "\nВыберите тег для удаления (Все вложенные теги и сообщения будут удалены)"
                # Rename tag
                elif data['view_mode'] == 'rename_tag':
                    message_text += "\nВыберите тег для переименования"
        # markup.add(CHANGE_MODE_BTN)
        return False, message_text
    else:
        try:
            current_tag = await db_tags.fetch_tag_by_id_group_id(tag_id, group_id)
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

        BACK_TO_PARENT = InlineKeyboardButton("\U00002934 К родительскому тегу", callback_data=f"cts_swt:{new_tag_id}:{mode}:1")

        # Checking the view_mode, the display of different buttons is dependent on it
        async with state.proxy() as data:
            # Basic functionality buttons
            if data['view_mode'] == 'default':
                markup.add(cancel_btn, BACK_TO_PARENT)
                markup.add(CHANGE_MODE_BTN)
                
                # Show all avalable functional
                if mode == TAG_MODE:
                    markup.add(MOVE_TAG_BTN, DELETE_TAG_BTN)
                    markup.add(RENAME_TAG_BTN)
                logger.info("view_mode' == 'default")

            # Buttons that depend on the context of the operation
            else:
                logger.info("view_mode' != 'default")
                markup.add(BACK_BTN, BACK_TO_PARENT)
                # Move tags
                if data['view_mode'] == 'move_tag':
                    message_text += "\nВыберите тег для перемещения"
                elif data['view_mode'] == 'move_tag_step_2':
                    message_text += "\nВыберите тег для вставки"
                    # markup.add(BACK_TO_PARENT)
                    markup.add(PASTE_TAG_BTN)
                # Delete tags
                elif data['view_mode'] == 'delete_tag':
                    message_text += "\nВыберите тег для удаления (Все вложенные теги и сообщения будут удалены)"
                # Rename tag
                elif data['view_mode'] == 'rename_tag':
                    message_text += "\nВыберите тег для переименования"
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

async def cancel_operation_tag(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(view_mode = 'default')
    logger.info('cancel_operation_tag | view_mode = default')
    await invoke_tag_system(callback_query, state)



def tag_system_handlers(dp: Dispatcher):
    dp.register_message_handler(button_imitation, commands=['tag_menu'])
    dp.register_callback_query_handler(cancel_tag_system, lambda c: c.data == "cancel_tag_system", state="*")
    dp.register_callback_query_handler(start, lambda c: c.data.startswith("start_tag_system"), state="*")
    dp.register_callback_query_handler(invoke_tag_system, lambda c: c.data.startswith("cts_swt"), state=States.PROCESS)

    dp.register_callback_query_handler(cancel_operation_tag, lambda c: c.data == "cancel_operation_tag", state="*")