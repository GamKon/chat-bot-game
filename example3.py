#vbnet
#In this code, we have defined two states groups `ChatStates` and `SystemStates`
# with three states each: `option1`, `option2`, and `option3`.
# We use the `state` parameter in our handlers to track the current state and transition between them
# as the user interacts with the bot.

import os
import aiogram
from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

##########################################################################################################################################################
# Variables
#HELP_MESSAGE = os.getenv('HELP_MESSAGE')
TOKEN        = os.getenv('TELEGRAM_BOT_TOKEN')

router = Router()
bot = Bot(token=TOKEN)
storage = MemoryStorage()

##########################################################################################################################################################
# Classes
class ChatStates(StatesGroup):
    option1 = State()
    option2 = State()
    option3 = State()

class SystemStates(StatesGroup):
    option1 = State()
    option2 = State()
    option3 = State()

##########################################################################################################################################################
# Commands
@router.message(CommandStart())
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    chat_button = InlineKeyboardButton("Chat", callback_data="chat")
    system_button = InlineKeyboardButton("System", callback_data="system")
    markup.add(chat_button, system_button)
    await message.answer("Welcome! Choose an option.", reply_markup=markup)

##########################################################################################################################################################
# Handlers
@router.callback_query(F.data == "chat")
async def chat_handler(callback_query: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Option 1", callback_data="chat_option1")
    button2 = InlineKeyboardButton("Option 2", callback_data="chat_option2")
    button3 = InlineKeyboardButton("Option 3", callback_data="chat_option3")
    markup.add(button1, button2, button3)
    await bot.answer_callback_query(callback_query.id, text="Select an option:", show_alert=False, reply_markup=markup)
    await state.set_state(ChatStates.option1)

@router.callback_query(F.data.startswith("chat_option"), state=ChatStates.option1)
async def chat_option_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChatStates.option2)
    if callback_query.data == "chat_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "chat_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

@router.callback_query(F.data.startswith("chat_option"), state=ChatStates.option2)
async def chat_option_handler2(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChatStates.option3)
    if callback_query.data == "chat_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "chat_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

@router.callback_query(F.data.startswith("chat_option"), state=ChatStates.option3)
async def chat_option_handler3(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "chat_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "chat_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

@router.callback_query(F.data == "system")
async def system_handler(callback_query: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Option 1", callback_data="system_option1")
    button2 = InlineKeyboardButton("Option 2", callback_data="system_option2")
    button3 = InlineKeyboardButton("Option 3", callback_data="system_option3")
    markup.add(button1, button2, button3)
    await bot.answer_callback_query(callback_query.id, text="Select an option:", show_alert=False, reply_markup=markup)
    await state.set_state(SystemStates.option1)

@router.callback_query(F.data.startswith("system_option"), state=SystemStates.option1)
async def system_option_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SystemStates.option2)
    if callback_query.data == "system_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "system_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

@router.callback_query(F.data.startswith("system_option"), state=SystemStates.option2)
async def system_option_handler2(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SystemStates.option3)
    if callback_query.data == "system_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "system_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

@router.callback_query(F.data.startswith("system_option"), state=SystemStates.option3)
async def system_option_handler3(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "system_option1":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 1.")
    elif callback_query.data == "system_option2":
        await bot.answer_callback_query(callback_query.id, text="You selected Option 2.")
    else:
        await bot.answer_callback_query(callback_query.id, text="You selected Option 3.")

##########################################################################################################################################################
# MAIN
##########################################################################################################################################################
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        types.BotCommand("start", "Start the bot")
    ])
    await bot.setup(storage)
    await bot.run(router)
##########################################################################################################################################################
if __name__ == "__main__":
    run = asyncio.run(main())
