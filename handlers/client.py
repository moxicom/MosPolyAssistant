import asyncio

from aiogram import types, Dispatcher
from config import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboards as keyboards
from Db import db_users as db_users
from Db import db_client as db_client
from Db import db_tags as db_tags
from handlers import general



class TagState(StatesGroup):
    sub_tag = State()

class MessageIDState(StatesGroup):
    message_id = State()


async def get_maintags(message: types.Message, state: FSMContext):
    users = await general.check_user_existence(message.from_user.id)
    if not users:
        await message.reply("Вы не состоите в группе.")
        return
    users = await db_users.fetch_users(message.from_user.id)
    tags = await db_client.fetch_main_tags(users[0].group_id)
    if(len(tags) <= 0):
        await message.reply("Тэги не найдены.")
    tag_message = "Главные теги:\n" + "\n".join(f"{i+1}. {tag.name}" for i, tag in enumerate(tags)) 
    await message.reply(tag_message)
    await message.answer("Введите номер тега")
    await state.update_data(tags=tags)
    # async with state.proxy() as data:
    #     data['tags'] = tags

    await TagState.sub_tag.set()


async def get_subtags(message: types.Message, state: FSMContext):
    tag_id = message.text
    user = await db_users.fetch_users(message.from_user.id)
    
    data = await state.get_data()

    if not user or user[0].group_id == -1:
        await message.reply("Вы не состоите в группе.")
        await state.finish()
        return
    
    if not tag_id.isdigit()or int(tag_id) > len(data.get('tags', [])):
        await message.reply(f"Номер тега '{tag_id}' не найден.")
        await state.finish()
        return
    
    tag = data.get('tags', [])[int(tag_id) - 1]
    subtags = await db_client.fetch_sub_tags(tag.id)

    if not subtags:
        messages = await db_client.fetch_messages_by_tag(user[0].group_id, tag.id)
        await message.answer(f"Сообщения с тегом '{tag.name}':")
        print(messages)
        message_text = ''

        for msg in messages:
            message_text += f"ID: {msg.id}, Заголовок: {msg.title}\n"

        await message.answer(message_text, reply_markup = keyboards.get_message_markup)
        await state.finish()
    else:
        tag_message = "Подтеги:\n" + "\n".join(f"{i+1}. {subtag.name}" for i, subtag in enumerate(subtags))
        tag_keyboard = keyboards.get_tag_keyboard(tag.id)
        await message.reply(tag_message, reply_markup = tag_keyboard)
        await state.update_data(tags=subtags)
        await TagState.sub_tag.set()


async def process_tag_callback(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')
    print("if 0 ", callback_data[0])
    if callback_data[0] == "back":
        tag_id = int(callback_data[1])
        tag = await db_tags.fetch_tag_by_id(tag_id)
        print("if 1")
        if tag and tag.parent_id is not None:
            parent_tag = await db_tags.fetch_tag_by_id(tag.parent_id)
            print("if 2")
            if parent_tag:
                print("if 3")
                subtags = await db_client.fetch_sub_tags(parent_tag.id)
                print("if 3 1")
                tag_message = "Подтеги:\n" + "\n".join(f"{i+1}. {subtag.name}" for i, subtag in enumerate(subtags))
                tag_keyboard = keyboards.get_tag_keyboard(parent_tag.id)
                print("if 3 2")
                await callback.message.edit_text(tag_message, reply_markup = tag_keyboard)
                await state.update_data(tags=subtags)
                await TagState.sub_tag.set()
            else:
                await callback.answer("Родительский тег не найден.")
        else:
            await callback.answer("Этот тег не имеет родителя.")
    elif callback_data[1] == "message":
        await get_message_by_id(callback.message, state)
    await callback.answer()


async def get_message_by_id(message: types.Message, state: FSMContext):
    message_id = message.get_args()
    if not message_id:
        await message.answer("Пожалуйста, введите ID сообщения.")
        await MessageIDState.message_id.set()
    else:
        await process_message_id(message, state, message_id)

async def process_message_id_input(message: types.Message, state: FSMContext):
    message_id = message.text
    await process_message_id(message, state, message_id)

async def process_message_id(message: types.Message, state: FSMContext, message_id: str):
    users = await db_users.fetch_users(message.from_user.id)
    if not users or users[0].group_id == -1:
        await message.answer("Вы не состоите в группе.")
        return
    if not message_id.isdigit():
        await message.reply("Пожалуйста, введите ID сообщения в числовом формате.")
        return
    message_id = int(message_id)
    msg = await db_client.fetch_message_by_id(message_id)
    if msg: 
        if msg.group_id == users[0].group_id:
            await message.reply(f"ID: {msg.id}\nЗаголовок: {msg.title}\nТекст: {msg.text}")
        else:
            await message.reply("Данное сообщение предназначено для другой группы.")  
    else:
        await message.reply(f"Сообщение с ID '{message_id}' не найдено.")
    await state.finish()

def client_handlers(dp: Dispatcher):
    dp.register_message_handler(get_maintags, commands=['get_tags'])
    dp.register_message_handler(get_subtags, state=TagState.sub_tag)
    dp.register_message_handler(get_message_by_id, commands=['get_message'])
    dp.register_message_handler(process_message_id_input, state=MessageIDState.message_id)
    # dp.register_callback_query_handler(callback=process_tag_callback, state="*") WTF IS THIS??????????!!!!!!
