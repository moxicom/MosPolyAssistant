from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

######################## REGISTRATION BUTTONS ########################
reg_move_mkp = InlineKeyboardMarkup(row_width=2)
# button_back = InlineKeyboardButton(text="Назад", callback_data="btn_back")
button_cancel = InlineKeyboardButton(text="Отмена", callback_data="btn_cancel")
reg_move_mkp.row(button_cancel)

role_chosing_mkp = InlineKeyboardMarkup(row_width=2)
role_btn_stud = InlineKeyboardButton(text="Участник", callback_data="btn_regular_user")
role_btn_owner = InlineKeyboardButton(text="Староста", callback_data="btn_owner")
role_chosing_mkp.row(role_btn_stud, role_btn_owner)
role_chosing_mkp.row(button_cancel)

# нужны кнопки для отмены и возврата


######################## ADMIN BUTTONS ########################
admin_functions_mkp = InlineKeyboardMarkup(row_width=2)
change_password = InlineKeyboardButton("Изменить пароль", callback_data="change_password")
list_of_group = InlineKeyboardButton("Список группы", callback_data="list_of_group")
write_message = InlineKeyboardButton("Написать сообщение", callback_data="write_message")
admin_functions_mkp.row(list_of_group, change_password)
admin_functions_mkp.row(write_message)


######################## CLIENT BUTTONS ########################

def get_tag_keyboard(tag_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Вернуться назад", callback_data=f"back_{tag_id}"))
    return keyboard


get_message_markup = InlineKeyboardMarkup(row_width=2)
get_message_button = InlineKeyboardButton("Получить сообщение", callback_data="get_message")
get_message_markup.row(get_message_button)