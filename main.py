from aiogram.utils import executor
from start_bot import dp

from handlers import register
from handlers import start_interaction


def on_startup():
    print("Bot was started")


start_interaction.start_interaction_handlers(dp)
register.register_handlers(dp)


# other.register_handlers_other(dp)
# admin.register_handlers_admin(dp)
# lient.register_handlers_client(dp)
# moder.register_handlers_client(dp) (Нужно ли?)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup()) # нужен ли skip_updates ? 

# created:
# /start - call check_user_existence()
# /reg - start registration