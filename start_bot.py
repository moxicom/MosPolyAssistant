import logging
import asyncio
from handlers import start_interaction, register, client

from config import bot, dp
from handlers.admin import change_password, list_of_group, basics, tags

token = '<token>'

logging.basicConfig(level=logging.INFO)

### BASIC HANDLERS FOR EVERYONE
start_interaction.start_interactions_handlers(dp)
register.register_handlers(dp)
###

### ADMIN HANDLERS
basics.admin_basic_handlers(dp)
change_password.change_password_handlers(dp)
list_of_group.list_of_group_handlers(dp)
tags.tags_handlers(dp)
###

### CLIENT HANDLERS
client.client_handlers(dp)
###


async def main():
    # Start the bot
    logging.info("Starting bot...")
    await dp.start_polling()
    logging.info("Bot stopped.")


if __name__ == '__main__':
    try:
        logging.info("Running main function...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("KeyboardInterrupt detected. Stopping...")
