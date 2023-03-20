import asyncio

import hashlib

from aiogram import types, Dispatcher
from start_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboards as markups

from Db import db_functions as db


class FSMregister(StatesGroup):
    name = State()
    role = State()
    group = State()
    password = State()
    password_repeat = State()


async def register_start(message: types.Message):
    await message.reply("Отлично, как вас зовут? (Пример: Иванов И)")
    print("1")  
    await FSMregister.name.set()


async def user_name_set(message: types.Message, state: FSMContext):
    # ТУТ НАДО ВСТАВИТЬ ПРОВЕРКУ НА ИМЯ
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(message.from_user.id, "Отлично, укажите вашу роль.\n\t Если выберете старосту, то вы создаете новую группу. \
                        \n\tИначе - присоединяетесь к существующей", reply_markup=markups.role_chosing_mkp)
    await FSMregister.next()
    

############### ROLES: 0 - basic member, 1 - modder, 2 - owner (староста)

async def user_role_owner_set(callback: types.CallbackQuery, state:FSMContext):
    print("role set 2") 
    async with state.proxy() as data:
        data['role'] = '2'
    await callback.message.answer("Вы выбрали роль старосты, теперь придумайте название группы")
    await callback.answer()
    await FSMregister.next()


async def user_role_regular_set(callback: types.CallbackQuery, state:FSMContext):
    print("role set 0") 
    async with state.proxy() as data:
        data['role'] = '0'
    await callback.message.answer("Вы выбрали роль обычного пользователя, теперь введите название группы")
    await callback.answer()
    await FSMregister.next()


async def users_group_set(message: types.Message, state: FSMContext): #FSM group
    print("group set")
    async with state.proxy() as data:
        if (data['role'] == '0'):
            try:
                fetch = await db.fetch_groups_info(name = message.text)
                if ( len(fetch) != 0):
                    await message.reply('Отлично, группа найдена, введите пароль')
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем не найдена')
                    await FSMregister.group.set()
            except Exception as ex : 
                await message.reply('Ошибка ' + str(ex))
                await state.finish()
        elif (data['role'] == '2'):
            try:
                fetch = await db.fetch_groups_info(name = message.text)
                if ( len(fetch) == 0):
                    await message.reply('Отлично, группа не найдена, введите пароль')
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем уже существует, придумайте новое')
                    await FSMregister.group.set()
            except Exception as ex : 
                await message.reply('Ошибка ' + str(ex))
                await state.finish()
    #if (data['role'] == '1')
        # ТУТ НУЖНА ПРОВЕРКА НА СУЩЕСТВОВАНИЕ ГРУППЫ. ЕСЛИ СУЩЕСТВУЕТ, ТО НАПИСАТЬ, ЧТО СУЗЕСТВУЕТ И ВЕРНУТЬСЯ в user_group_set
        # ЕСЛИ не СУЩЕСТВУЕТ, ТО СЕЙВИМ ИМЯ В ДАТЕ
        # async with state.proxy() as data:
        #     data['group'] = ИМЯ
    #elif (data['role'] == '0')
        # тут надо короче проверить существование группы.
        # если она существует, то надо просить пароль
        # ЕСЛИ НЕ СУЩЕСТВУЕТ, то НАПИСАТЬ, ЧТО неСУщЕСТВУЕТ И ВЕРНУТЬСЯ в user_group_set
    # обработчик кнопки отмена
    # кнопка вернуться назад и тп (кста кнопки отмена должны быть везде, а кнопка назад на всех кроме user_name_set)

    # ТО ЧТО НиЖе ЭТО ПО РОФЛУ ДЛЯ ТЕСТОВ
    # if True:
    #     await message.answer("Такая группа действительно существует. Вы угадали название")
    #     async with state.proxy() as data:
    #         data['group'] = message.text
    #     await message.answer("Введите пароль")
    #     await FSMregister.next()
    
    # #если не существует
    # else:
    #     await message.answer("Такой группы не существует, попробуйте ввести название заново")
    #     await FSMregister.group.set()


async def users_password_check(message: types.Message, state: FSMContext): #FSM password
    async with state.proxy() as data:
            if (data['role'] == '0'):
                try:
                    fetch = await db.fetch_groups_info(name = data['name'])
                    if (hashlib.sha256(message.text.encode().hexdigest()) == fetch[0][2]): 
                        await message.answer('Пароль верный!')
                        await message.answer(f'{data["name"]} {data["group"]}')
                        await state.finish()
                except Exception as ex:
                    await message.reply('Ошибка ' + str(ex))
                    await state.finish()
            elif (data['role'] == '2'):
                try:
                    data['password'] = message.text
                    await message.reply('Повторите пароль')
                    print("password check 1") 
                    await FSMregister.next()
                except Exception as ex:
                    await message.reply('Ошибка ' + str(ex))
                    await state.finish()      

async def users_password_repeating(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        print("password check 2") 
        if (data['password'] == message.text):
            await message.reply('Пароли совпадают')
            data['password'] = str(hashlib.sha256(message.text.encode()).hexdigest())
            await db.insert_groups_info(name=data['name'], password=data['password'])
            print(data['name'], data['password'])
        else:
            await message.reply('Пароли не совпадают')
            FSMregister.password.set()



def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_start, commands=['reg'])
    dp.register_message_handler(user_name_set, state=FSMregister.name, content_types=types.ContentTypes.TEXT)
    #dp.register_callback_query_handler(user_role_set)
    dp.register_callback_query_handler(text='btn_regular_user', callback=user_role_regular_set, state=FSMregister.role)
    dp.register_callback_query_handler(text='btn_owner', callback=user_role_owner_set , state=FSMregister.role)
    dp.register_message_handler(users_group_set, state=FSMregister.group, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(users_password_check, state=FSMregister.password, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(users_password_repeating, state=FSMregister.password_repeat, content_types=types.ContentTypes.TEXT)
    
