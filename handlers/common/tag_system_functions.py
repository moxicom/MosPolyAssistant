import logging

from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.dispatcher import FSMContext
from config import bot

from Db import db_tags as db_tags
from handlers.admin import tags
from handlers.common import tag_system
from handlers import general

async def move_tag(callback_query: types.CallbackQuery, state: FSMContext):
    parameters = callback_query.data.split(':')
    if parameters[1] != 'root':
        tag_id = int(parameters[1])
    else:
        tag_id = None

    # Selecting a tag to move    
    if parameters[2] == 'step_1':
        logging.info('move_tag step 1')
        await state.update_data(view_mode = 'move_tag')
        await tag_system.invoke_tag_system(callback_query, state, tag_id=tag_id)
    # Choosing a place to move tag    
    elif parameters[2] == 'step_2':
        logging.info('move_tag step 2')
        await state.update_data(view_mode = 'move_tag_step_2')
        await state.update_data(moving_tag_id = tag_id)
        await tag_system.invoke_tag_system(callback_query, state)
    # Performing a move
    elif parameters[2] == 'step_3':
        logging.info('move_tag step 3')
        logging.info('|tag_system_functions/move_tag| tag moving has started')
        
        try:
           async with state.proxy() as data: 
                await db_tags.update_parent_id(new_parent_id=tag_id, tag_id=data['moving_tag_id'])
        except Exception as ex:
            logging.warning('|tag_system_functions/move_tag| tag move error ' + str(ex))

        await state.update_data(view_mode = 'default')
        await tag_system.invoke_tag_system(callback_query, state)

async def delete_tag(callback_query: types.CallbackQuery, state: FSMContext):
    parameters = callback_query.data.split(':')
    if parameters[1] != 'root':
        tag_id = int(parameters[1])
    else:
        tag_id = None

    # Selecting a tag to delete  
    if parameters[2] == 'select_tag':
        logging.info('move_tag step select_tag')
        # Changing the view_mode in order to change the callback_mode on the displayed tags.
        await state.update_data(view_mode = 'delete_tag')
        await tag_system.invoke_tag_system(callback_query, state, tag_id=tag_id)

    # Confirmation of tag deletion 
    elif parameters[2] == 'confirm':
        group_id = await general.get_group_id_by_tg_id(callback_query.from_user.id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Да", callback_data=f"delete_tag:{parameters[1]}:delete:{group_id}"))
        markup.add(InlineKeyboardButton("Нет", callback_data="cancel_operation_tag"))

        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=f'Вы уверены что хотите удалить тег {parameters[3]}',
                                    reply_markup=markup,
                                    parse_mode=ParseMode.MARKDOWN)
    # Start deletion
    elif parameters[2] == 'delete':
        logging.info('|tag_system_functions/delete_tag| tag deleting has started')
        print(parameters)
        await tags.delete_tag(tag_id=tag_id, group_id=int(parameters[3]))
        await state.update_data(view_mode = 'default')
        await tag_system.invoke_tag_system(callback_query, state)
        logging.info('|tag_system_functions/delete_tag| tag deleting has finished')


def tag_system_functions_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(move_tag, lambda c: c.data.startswith("move_tag"), state="*")
    dp.register_callback_query_handler(delete_tag, lambda c: c.data.startswith("delete_tag"), state="*")