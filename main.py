import asyncio
from typing import Any, Awaitable, Callable, Dict
import logging
from aiogram import Dispatcher, Router, types

from utility import debug_print
# ??? from aiogram.contrib.middlewares.base import BaseMiddleware
# ?? from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from classes import bot
from handlers import main_menu, chat_menu, system_menu, ai, media
#from db.init_db import create_all_tables

async def on_start():
#    await create_all_tables()
    print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Starting\n')

async def on_shutdown():
    print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Shutdown\n')
#     await bot.close()
#     await db_pool.close()

class ThrottleWhileThinking(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: types.Message, data: Dict[str, Any]) -> Any:
        state = data.get("state")
#        debug_print("state: ", state)

        state_data = await state.get_data()
#        debug_print("state_data: ", state_data)

        if state_data.get("is_thinking") == True:
#        True: # "is_thinking" not in data:
            return await event.reply("Please be patient, I'm thinking...")

        return await handler(event, data)

    # if "is_thinking" not in data:
    #     data = await state.update_data(is_thinking = False)
    # else:
    #     print("______is_thinking in data______\n")
    # if data["is_thinking"]:
    #     await message.reply("I'm still thinking at the first question, please be patient")
    #     return

# async def on_process_message(self, message: types.Message, *args):
#     if '-g' in message.text.lower():
#         message.text = message.text.lower().replace('-g', '').replace('г', 'ґ')

router = Router()

def configure_sqlalchemy_logging():
    # Disable SQLAlchemy logging
    logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

    # Ensure no handlers are attached to these loggers
    for handler in logging.getLogger('sqlalchemy').handlers:
        logging.getLogger('sqlalchemy').removeHandler(handler)

    for handler in logging.getLogger('sqlalchemy.engine').handlers:
        logging.getLogger('sqlalchemy.engine').removeHandler(handler)

    # Add NullHandler to prevent propagation
    logging.getLogger('sqlalchemy').addHandler(logging.NullHandler())
    logging.getLogger('sqlalchemy.engine').addHandler(logging.NullHandler())

    # Disable propagation to prevent messages from bubbling up to the root logger
    logging.getLogger('sqlalchemy').propagate = False
    logging.getLogger('sqlalchemy.engine').propagate = False




##########################################################################################################################################################
# Main
##########################################################################################################################################################
async def main():
    # Call the configuration function
    configure_sqlalchemy_logging()



#    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp  = Dispatcher()
    dp.message.middleware(ThrottleWhileThinking())
    dp.include_routers(router, media.router, main_menu.router, chat_menu.router, system_menu.router, ai.router)

    await bot.delete_webhook(drop_pending_updates=True)

# ??? NOT working on_startup, on_shutdown calls
    await dp.start_polling(bot, on_startup=on_start, on_shutdown=on_shutdown)

##########################################################################################################################################################
if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # logging.basicConfig()
    # logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
    # logging.getLogger('sqlalchemy.engine').addHandler(logging.NullHandler())
    asyncio.run(main())
