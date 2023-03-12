from aiogram.utils import executor
from start_bot import dp


def on_startup():
    print("Bot was started")


# other.register_handlers_other(dp)
# admin.register_handlers_admin(dp)
# lient.register_handlers_client(dp)
# moder.register_handlers_client(dp) (Нужно ли?)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup()) # нужен ли skip_updates ? 