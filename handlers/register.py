import hashlib
import logging

from aiogram import types, Dispatcher
from config import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboards as keyboards
from Db import db_groups_info as db_groups_info
from Db import db_users as db_users
from Db import db_groups_members as db_groups_members
from handlers import general


class FSMregister(StatesGroup):
    name = State()
    role = State()
    group = State()
    password = State()
    password_repeat = State()

async def cancel_reg_btn(callback: types.CallbackQuery, state: FSMContext):
    logging.info('|register/cancel_reg_btn| Operation canceled')
    await callback.message.answer("Вы отменили процесс регистрации")
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await state.finish()


async def register_start(message: types.Message):
    """
    Checking the existence of a user in the database.
    In case of unexistence, the registration process begins.
    """
    exist = await general.check_user_existence(message.from_user.id)
    if not exist:
        await message.reply("Отлично, как вас зовут? (Пример: Иванов И)")
        logging.info('|register/register_start| Step register_start has begun...')
        await FSMregister.name.set()
    else:
        await message.reply("Вы уже зарегистрированы :) \n Если что-то ищете, то напишите /help")


async def user_name_set(message: types.Message, state: FSMContext):
    """
    User's choice of name.
    And checking for length and compliance with existing commands.
    """
    if len(message.text) > 255 :
        await message.reply("Данное имя слишком длинное (больше 255 символов), введите корректное имя (Пример: Иванов И).")
        await FSMregister.name.set()    
        return

    if message.text[0] == "/":
        await message.reply("Ваше имя не должно начинаться с /, введите корректное имя (Пример: Иванов И).")
        await FSMregister.name.set()    
        return
    
    async with state.proxy() as data:
        logging.info('|register/user_name_set| User name set to ' + message.text)
        data['name'] = message.text

    await bot.send_message(message.from_user.id, "Отлично, укажите вашу роль.\n\t ➡️При выборе роли старосты, вы перейдете к созданию новой группы. \
                        \n\t ➡️При выборе роли участника, вы присоединитесь к существующей.", reply_markup=keyboards.role_chosing_mkp)
    await FSMregister.next()


############### ROLES: 0 - basic member, 1 - modder, 2 - owner (староста)

async def user_role_owner_set(callback: types.CallbackQuery, state: FSMContext):
    logging.info('|register/user_role_owner_set| User role set 2 (Owner)')
    async with state.proxy() as data:
        data['role'] = '2'
    await callback.message.answer("Вы выбрали роль старосты, теперь придумайте название группы",
                                  reply_markup=keyboards.reg_move_mkp)
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await FSMregister.next()


async def user_role_regular_set(callback: types.CallbackQuery, state: FSMContext):
    logging.info('|register/user_role_regular_set| User role set 0 (Basic member)')
    async with state.proxy() as data:
        data['role'] = '0'
    await callback.message.answer("Вы выбрали роль обычного пользователя, теперь введите название группы",
                                  reply_markup=keyboards.reg_move_mkp)
    await callback.answer()
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await FSMregister.next()


async def user_group_set(message: types.Message, state: FSMContext):  # FSM group
    """
    Splitting the path to join a group or create it. 
    Depends on the user role.
    """
    logging.info('|register/user_group_set| Group set started...')
    async with state.proxy() as data:
        if data['role'] == '0':
            try:
                fetch = await db_groups_info.fetch_groups_info(group_name=message.text)
                if len(fetch) != 0:
                    data['group'] = message.text
                    await message.reply('Группа найдена, введите пароль.', reply_markup=keyboards.reg_move_mkp)
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем не найдена, введите еще раз.',
                                        reply_markup=keyboards.reg_move_mkp)
                    await FSMregister.group.set()
            except Exception as ex:
                await message.reply('Ошибка ' + str(ex))
                logging.warning('|register/user_group_set| An error has occurred: ' + str(ex))
                await state.finish()
        elif data['role'] == '2':
            try:
                fetch = await db_groups_info.fetch_groups_info(group_name=message.text)
                if len(message.text) > 255:
                    await message.reply("Данное имя слишком длинное (больше 255 символов), введите корректное название.")
                    await FSMregister.group.set()    
                    return 
                elif message.text[0] == "/":
                    await message.reply("Название группы не должно начинаться с /, введите корректное название.")
                    await FSMregister.group.set()    
                    return
                elif len(fetch) == 0:
                    data['group'] = message.text
                    await message.reply('Корректное название группы. Придумайте и введите пароль для новой группы.',
                                        reply_markup=keyboards.reg_move_mkp)
                    await FSMregister.next()
                else:
                    await message.reply('Группа с таким именем уже существует, введите другое название.',
                                        reply_markup=keyboards.reg_move_mkp)
                    await FSMregister.group.set()
            except Exception as ex:
                await message.reply('Ошибка ' + str(ex))
                logging.warning('|register/user_group_set| An error has occurred: ' + str(ex))
                await state.finish()


async def user_password_check(message: types.Message, state: FSMContext):  # FSM password
    async with state.proxy() as data:
        if data['role'] == '0':
            ## IF ROLE IS BASIC USER
            try:
                group_info_fetch = await db_groups_info.fetch_groups_info(group_name=data['group'])
                logging.info('|register/user_password_check| User_password_check (role 0) %s', group_info_fetch[0])
                if hashlib.sha256(message.text.encode()).hexdigest() == group_info_fetch[0][2]:
                    
                    # Saving information in the database about new user
                    await db_users.insert_users(name=data['name'], group_id=group_info_fetch[0][0], tg_id=message.from_user.id)
                    user_id = (await db_users.fetch_users(tg_id=message.from_user.id))[0][0]
                    await db_groups_members.insert_groups_members(
                        member_id=user_id,
                        group_id=group_info_fetch[0][0],
                        role=int(data['role'])
                    )
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text=f'ОТЛИЧНО, {data["name"]}! Вы присоединились к группе {data["group"]}',
                        reply_markup=keyboards.client_functions_mkp
                    )
                    await state.finish()
                else:
                    await message.answer('Пароль неверный\nВведите пароль снова', reply_markup=keyboards.reg_move_mkp)
            except Exception as ex:
                await message.reply('Ошибка ' + str(ex))
                logging.warning('|register/user_password_check| An error has occurred: ' + str(ex))
                await state.finish()
        elif data['role'] == '2':
            try:
                data['password'] = message.text
                await message.reply('Повторите пароль', reply_markup=keyboards.reg_move_mkp)
                await FSMregister.next()
            except Exception as ex:
                await message.reply('Ошибка ' + str(ex))
                logging.warning('|register/user_password_check| An error has occurred: ' + str(ex))
                await state.finish()


async def user_password_repeating(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logging.info('|register/user_password_repeating| Password repeating check started...')
        if data['password'] == message.text:
            await message.reply('Пароли совпадают.\nНовая группа успешно создана')
            try: 
                # Saving information in the database about new group and user
                data['password'] = str(hashlib.sha256(message.text.encode()).hexdigest())
                await db_groups_info.insert_groups_info(group_name=data['group'], password=data['password'])

                group_id = (await db_groups_info.fetch_groups_info(group_name=data['group']))[0][0]
                await db_users.insert_users(name=data['name'], group_id=group_id, tg_id=message.from_user.id)

                user_id = (await db_users.fetch_users(tg_id=message.from_user.id))[0][0]
                await db_groups_members.insert_groups_members(member_id=user_id, group_id=group_id, role=int(data['role']))

                logging.info('|register/user_password_repeating| User_password_repeating finish ' + data['name'] + ' ' + data['password'])

                # sending a message to created user with `admin_functions_mkp` keyboard
                await bot.send_message(chat_id=message.chat.id, text="Выбери, что ты хочешь сделать",
                                    reply_markup=keyboards.admin_functions_mkp)
                await state.finish()
            except Exception as ex:
                await message.reply('Ошибка ' + str(ex))
                logging.warning('|register/user_password_repeating| An error has occurred: ' + str(ex))
                await state.finish()
        else:
            await message.reply('Пароли не совпадают. Введите новый пароль', reply_markup=keyboards.reg_move_mkp)
            await FSMregister.password.set()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_start, commands=['reg'])
    dp.register_message_handler(user_name_set, state=FSMregister.name, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(user_group_set, state=FSMregister.group, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(user_password_check, state=FSMregister.password, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(user_password_repeating, state=FSMregister.password_repeat,  content_types=types.ContentTypes.TEXT)
        
    dp.register_callback_query_handler(text='btn_regular_user', callback=user_role_regular_set, state=FSMregister.role)
    dp.register_callback_query_handler(text='btn_owner', callback=user_role_owner_set, state=FSMregister.role)
    dp.register_callback_query_handler(text='btn_cancel', callback=cancel_reg_btn, state='*')
