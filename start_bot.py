import logging
import asyncio
from handlers import start_interaction, register
from keyboards.admin import list_of_group, change_password, tags
from config import bot, dp

# token = '5555273889:AAFh3yk1-P5brLJQ79Ip5_JbDydkJhAGUpc'
token = '5983840222:AAH5nLq35iCpMvSRBsD6v8p5TqhL_kmLSXU'

logging.basicConfig(level=logging.INFO)

start_interaction.start_interactions_handlers(dp)
register.register_handlers(dp)
change_password.change_password_handlers(dp)
list_of_group.list_of_group_handlers(dp)
tags.tags_handlers(dp)
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
