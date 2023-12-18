#This code defines a bot with a start command, which will show an inline keyboard with three buttons - "Chat", "System" and "Print\_state". The first two buttons change the `current_state` variable, and the third button shows the value of the `current_state` variable.
#You need to replace YOUR\_BOT\_TOKEN with actual token of your bot.

import os
import aiogram.utils.markdown as md
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN   = os.getenv('TELEGRAM_BOT_TOKEN')
bot     = Bot(token="TOKEN")
dp      = Dispatcher(bot)

# Define the states
CHAT_STATE = 'chat'
SYSTEM_STATE ='system'
STATE_NONE = None

current_state = STATE_NONE

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup().row(
        InlineKeyboardButton('Chat', callback_data='chat'),
        InlineKeyboardButton('System', callback_data='system'),
        InlineKeyboardButton('Print State', callback_data='print_state')
    )
    await message.answer("Hello! Welcome to the bot.", reply_markup=keyboard)

@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    global current_state
    action = callback_query.data

    if action == 'chat':
        current_state = CHAT_STATE
    elif action =='system':
        current_state = SYSTEM_STATE
    elif action == 'print_state':
        await bot.answer_callback_query(callback_query.id, f"Current state is {current_state}")

if __name__ == "__main__":
    executor.start_polling(dp)
