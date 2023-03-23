from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



######################## REGISTRATION BUTTONS ########################
reg_move_mkp = InlineKeyboardMarkup(row_width=2)
#button_back = InlineKeyboardButton(text="Назад", callback_data="btn_back")
button_cancel = InlineKeyboardButton(text="Отмена", callback_data="btn_cancel")
reg_move_mkp.row(button_cancel)

role_chosing_mkp = InlineKeyboardMarkup(row_width=2)
role_btn_stud = InlineKeyboardButton(text="Участник", callback_data="btn_regular_user")
role_btn_owner = InlineKeyboardButton(text="Староста", callback_data="btn_owner")
role_chosing_mkp.row(role_btn_stud, role_btn_owner)
role_chosing_mkp.row(button_cancel)


# нужны кнопки для отмены и возврата 



######################## ADMIN BUTTONS ########################