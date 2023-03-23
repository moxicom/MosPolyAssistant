import asyncio

import hashlib

from aiogram import types, Dispatcher
from start_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboards as keyboards
from Db import db_functions as db
from handlers import general



class FSMregister(StatesGroup):
    name = State()
    role = State()
    group = State()
    password = State()
    password_repeat = State()

async def cancel_reg_btn(callback: types.CallbackQuery, state:FSMContext):
    print('Operation canceled')
    await callback.message.answer("Вы отменили процесс регистрации")
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id= callback.message.chat.id, message_id= callback.message.message_id, reply_markup=None)
    await state.finish()

# FROZEN!
# async def back_reg_btn(callback: types.CallbackQuery, state:FSMContext):
#     print('Operation backed')
#     await callback.message.answer("Вы перешли на предыдущий этап регистрации")
#     await callback.answer()
#     await bot.edit_message_reply_markup(chat_id= callback.message.chat.id, message_id= callback.message.message_id, reply_markup=None)
#     await FSMregister.previous()
#     await FSMregister.previous()

async def send_virtual_message():
    await bot.process_update(types.Update(message='aboba'))


async def register_start(message: types.Message):
    exist = await general.check_user_existence(message)
    if (not exist):
        await message.reply("Отлично, как вас зовут? (Пример: Иванов И)")
        print('----register_start----')  
        await FSMregister.name.set()
    else:
        message.reply("Вы уже зарегестрированы :) \n Если что-то ищете, то напишите /help")


async def user_name_set(message: types.Message, state: FSMContext):
    # ТУТ НАДО ВСТАВИТЬ ПРОВЕРКУ НА ИМЯ
    async with state.proxy() as data:
        data['name'] = message.text
    
    await bot.send_message(message.from_user.id, "Отлично, укажите вашу роль.\n\t Если выберете старосту, то вы создаете новую группу. \
                        \n\tИначе - присоединяетесь к существующей", reply_markup=keyboards.role_chosing_mkp)
    await FSMregister.next()
    

############### ROLES: 0 - basic member, 1 - modder, 2 - owner (староста)

async def user_role_owner_set(callback: types.CallbackQuery, state:FSMContext):
    print("role set 2") 
    async with state.proxy() as data:
        data['role'] = '2'
    await callback.message.answer("Вы выбрали роль старосты, теперь придумайте название группы",reply_markup=keyboards.reg_move_mkp)
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id= callback.message.chat.id, message_id= callback.message.message_id, reply_markup=None)
    await FSMregister.next()


async def user_role_regular_set(callback: types.CallbackQuery, state:FSMContext):
    print("role set 0") 
    async with state.proxy() as data:
        data['role'] = '0'
    await callback.message.answer("Вы выбрали роль обычного пользователя, теперь введите название группы",reply_markup=keyboards.reg_move_mkp)
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id= callback.message.chat.id, message_id= callback.message.message_id, reply_markup=None)
    await FSMregister.next()


async def users_group_set(message: types.Message, state: FSMContext): #FSM group
    print("group set started...")
    async with state.proxy() as data:
        if (data['role'] == '0'):
            try:
                fetch = await db.fetch_groups_info(group_name= message.text)
                if ( len(fetch) != 0):
                    data['group'] = message.text
                    await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                    await message.reply('Группа найдена, введите пароль', reply_markup=keyboards.reg_move_mkp)
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем не найдена, введите еще раз' , reply_markup=keyboards.reg_move_mkp)
                    await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                    await FSMregister.group.set()
            except Exception as ex : 
                await message.reply('Ошибка ' + str(ex))
                await state.finish()
        elif (data['role'] == '2'):
            try:
                fetch = await db.fetch_groups_info(group_name = message.text)
                if ( len(fetch) == 0):
                    data['group'] = message.text
                    await message.reply('Корректное название группы. Придумайте и введите пароль для новой группы', reply_markup=keyboards.reg_move_mkp)
                    await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем уже существует, введите другое название', reply_markup=keyboards.reg_move_mkp)
                    await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                    await FSMregister.group.set()
            except Exception as ex : 
                await message.reply('Ошибка ' + str(ex))
                await state.finish()

    # обработчик кнопки отмена
    # кнопка вернуться назад и тп (кста кнопки отмена должны быть везде, а кнопка назад на всех кроме user_name_set)

async def users_password_check(message: types.Message, state: FSMContext): #FSM password
    async with state.proxy() as data:
            if (data['role'] == '0'):
                try:
                    group_info_fetch = await db.fetch_groups_info(group_name = data['group'])
                    print('---users_password_check (role 0)--- \n', group_info_fetch)
                    if (hashlib.sha256(message.text.encode()).hexdigest() == group_info_fetch[0][2]): 
                        await message.answer('Пароль верный')
                        await message.answer(f'{data["name"]} {data["group"]}')
                        await db.insert_users(name = data['name'], group_id = group_info_fetch[0][0], tg_id=message.from_user.id)
                        user_id = (await db.fetch_users(tg_id=message.from_user.id))[0][0]
                        await db.insert_groups_members(member_id=user_id,group_id=group_info_fetch[0][0],role=int(data['role']))
                        await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                        await state.finish()
                    else:
                        await message.answer('Пароль неверный\nВведите пароль снова', reply_markup=keyboards.reg_move_mkp)
                        await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                except Exception as ex:
                    await message.reply('Ошибка ' + str(ex))
                    await state.finish()
            elif (data['role'] == '2'):
                try:
                    data['password'] = message.text
                    await message.reply('Повторите пароль', reply_markup=keyboards.reg_move_mkp)
                    await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
                    await FSMregister.next()
                except Exception as ex:
                    await message.reply('Ошибка ' + str(ex))
                    await state.finish()      

async def users_password_repeating(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        print("---password repeating check started....---") 
        if (data['password'] == message.text):
            await message.reply('Пароли совпадают.\nНовая группа успешно создана')
            await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
            data['password'] = str(hashlib.sha256(message.text.encode()).hexdigest())
            await db.insert_groups_info(group_name=data['group'], password=data['password'])

            group_id = (await db.fetch_groups_info(group_name = data['group']))[0][0]
            await db.insert_users(name = data['name'], group_id = group_id, tg_id=message.from_user.id)

            user_id = (await db.fetch_users(tg_id=message.from_user.id))[0][0]
            await db.insert_groups_members(member_id=user_id,group_id=group_id,role=int(data['role']))
            
            print('users_password_repeating finish\n', data['name'], data['password'])
            await state.finish()
        else:
            await message.reply('Пароли не совпадают. Введите новый пароль', reply_markup=keyboards.reg_move_mkp)
            await bot.edit_message_reply_markup(chat_id= message.chat.id, message_id= message.message_id - 1, reply_markup=None)
            await FSMregister.password.set()



def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_start, commands=['reg'])
    dp.register_message_handler(user_name_set, state=FSMregister.name, content_types=types.ContentTypes.TEXT)
    #dp.register_callback_query_handler(user_role_set)
    dp.register_callback_query_handler(text='btn_regular_user', callback=user_role_regular_set, state=FSMregister.role)
    dp.register_callback_query_handler(text='btn_owner', callback=user_role_owner_set , state=FSMregister.role)
    dp.register_message_handler(users_group_set, state=FSMregister.group, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(users_password_check, state=FSMregister.password, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(users_password_repeating, state=FSMregister.password_repeat, content_types=types.ContentTypes.TEXT)

    dp.register_callback_query_handler(text='btn_cancel', callback=cancel_reg_btn, state='*')
    #dp.register_callback_query_handler(text='btn_back', callback=back_reg_btn, state='*')
    
