from aiogram import types, Dispatcher
from start_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import main_keyboards as markups;


class FSMAdmin(StatesGroup):
    name = State()
    role = State()
    group = State()
    password = State()


async def register_start(message: types.Message):
    await message.reply("Отлично, как вас зовут? (Пример: Иванов И)")
    print("1")  
    await FSMAdmin.name.set()


async def user_name_set(message: types.Message, state: FSMContext):
    # ТУТ НАДО ВСТАВИТЬ ПРОВЕРКУ НА ИМЯ
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(message.from_user.id, "Отлично, укажите вашу роль.\n\t Если выберете старосту, то вы создаете новую группу. \
                        \n\tИначе - присоединяетесь к существующей", reply_markup=markups.role_chosing_mkp)
    await FSMAdmin.next()
    

############### ROLES: 0 - basic member and 1 - owner (староста)    

async def user_role_owner_set(callback: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['role'] = '1'
    await callback.message.answer("Вы выбрали роль старосты, теперь придумайте название группы")
    await callback.answer()
    await FSMAdmin.next()


async def user_role_regular_set(callback: types.CallbackQuery, state:FSMContext):
    print("role set") 
    async with state.proxy() as data:
        data['role'] = '0'
    await callback.message.answer("Вы выбрали роль обычного пользователя, теперь введите название группы")
    await callback.answer()
    await FSMAdmin.next()


async def users_group_set(message: types.Message, state: FSMContext): #FSM group
    print("group set")
    _data = state.proxy()
    #if (data['role'] == '1')
        # ТУТ НУЖНА ПРОВЕРКА НА СУЩЕСТВОВАНИЕ ГРУППЫ. ЕСЛИ СУЩЕСТВУЕТ, ТО НАПИСАТЬ, ЧТО СУЗЕСТВУЕТ И ВЕРНУТЬСЯ в user_group_set
        # ЕСЛИ не СУЩЕСТВУЕТ, ТО СЕЙВИМ ИМЯ В ДАТЕ
        # async with state.proxy() as data:
        #     data['group'] = ИМЯ
    #elif (data['role'] == '0')
        # тут надо короче проверить существование группы.
        # если она существует, то надо просить пароль
        # ЕСЛИ НЕ СУЩЕСТВУЕТ, то НАПИСАТЬ, ЧТО СУЗЕСТВУЕТ И ВЕРНУТЬСЯ в user_group_set
    # обработчик кнопки отмена
    # кнопка вернуться назад и тп (кста кнопки отмена должны быть везде, а кнопка назад на всех кроме user_name_set)

    # ТО ЧТО НиЖе ЭТО ПО РОФЛУ ДЛЯ ТЕСТОВ
    if True:
        await message.answer("Такая группа действительно существует. Вы угадали название")
        async with state.proxy() as data:
            data['group'] = message.text
        await message.answer("Введите пароль")
        await FSMAdmin.next()
    
    #если не существует
    else:
        await message.answer("Такой группы не существует, попробуйте ввести название заново")
        await FSMAdmin.group.set()


async def users_password_check(message: types.Message, state: FSMContext): #FSM password
    async with state.proxy() as data:
            data['password'] = message.text

    #ЕСЛИ ПАРОЛЬ СОВПАЛ
    if True:
        await message.answer("Пароль верный!")
        await message.answer(f'{data["name"]} {data["group"]}')
        await state.finish()
    #ЕСЛИ НЕ СОВПАЛ
    else:
        message.answer("Пароль не подошел. Попробуйте еще раз")
        FSMAdmin.password.set()


# --------------------------- РЕГИСТРАЦИЯ ДЛЯ АДМИНА ------------------------------


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(register_start, commands=['reg'])
    dp.register_message_handler(user_name_set, state=FSMAdmin.name, content_types=types.ContentTypes.TEXT)
    #dp.register_callback_query_handler(user_role_set)
    dp.register_callback_query_handler(text='btn_regular_user', callback=user_role_regular_set, state=FSMAdmin.role)
    dp.register_callback_query_handler(text='btn_owner', callback=user_role_owner_set , state=FSMAdmin.role)
    dp.register_message_handler(users_group_set, state=FSMAdmin.group, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(users_password_check, state=FSMAdmin.password, content_types=types.ContentTypes.TEXT)
    
