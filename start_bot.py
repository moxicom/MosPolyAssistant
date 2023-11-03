import logging
import asyncio
from handlers import start_interaction, register, client

from config import bot, dp
from handlers.common import tag_system
from handlers.admin import change_password, list_of_group, basics, tags, group_delete, attachments


token = '<token>'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Create a file handler
file_handler = logging.FileHandler('MosPolyAssistant.log', mode='w')
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Get root handler and set handler for it
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)





attachments.temp_attachments_handler(dp)





### BASIC HANDLERS FOR EVERYONE
start_interaction.start_interactions_handlers(dp)
register.register_handlers(dp)
tag_system.tag_system_handlers(dp)
###

### ADMIN HANDLERS

basics.admin_basic_handlers(dp)
change_password.change_password_handlers(dp)
list_of_group.list_of_group_handlers(dp)
tags.tags_handlers(dp)
group_delete.group_delete_handlers(dp)
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
