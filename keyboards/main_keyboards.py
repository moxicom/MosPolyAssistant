from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



######################## REGISTRATION BUTTONS ########################

role_chosing_mkp = InlineKeyboardMarkup(row_width=2)
role_btn_stud = InlineKeyboardButton(text="Участник", callback_data="btn_regular_user")
role_btn_owner = InlineKeyboardButton(text="Староста", callback_data="btn_owner")
role_chosing_mkp.row(role_btn_stud, role_btn_owner)

# нужны кнопки для отмены и возврата 



######################## ADMIN BUTTONS ########################