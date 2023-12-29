import asyncio
#import asyncpg
#import logging
#import sys
#from time import sleep
# from os import getenv
#from typing import Any, Dict

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode

#from classes import UIStates
from handlers import main_menu, chat_menu, system_menu, ai, media
#from db.init_db import create_all_tables

from db.init_db import create_all_tables

async def on_start():
#    await create_all_tables()
    print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Starting\n')

async def on_shutdown():
    print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Shutdown\n')
#     await bot.close()
#     await db_pool.close()

# TOKEN = getenv('TELEGRAM_BOT_TOKEN')
# bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
from classes import bot
router = Router()

# async def pin_chat_message(chat_id, message_id):
#     await bot.pin_chat_message(chat_id=chat_id, message_id=message_id)


async def main():
#    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp  = Dispatcher()
    dp.include_routers(router, media.router, main_menu.router, chat_menu.router, system_menu.router, ai.router)

#    dp.message.middleware(ai.ai_middleware)
#asgiref.sync.sync_to_async

# sync_to_async
    await bot.delete_webhook(drop_pending_updates=True)

# ??? NOT working on_startup, on_shutdown calls
    await dp.start_polling(bot, on_startup=on_start, on_shutdown=on_shutdown)

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
