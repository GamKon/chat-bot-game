import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from models.Mistral_7B_Instruct_v0_2_GPTQ import Mistral_7B_Instruct

##########################################################################################################################################################
# Variables
TOKEN = getenv('TELEGRAM_BOT_TOKEN')

router = Router()

##########################################################################################################################################################
# Classes
class ChatStates(StatesGroup):
    chat     = State()
    drop     = State()
    repeat   = State()
    reset    = State()

class SystemStates(StatesGroup):
    mode     = State()
    model    = State()
    language = State()


##########################################################################################################################################################
# Commands
@router.message(CommandStart())
async def command_start( message: Message, state: FSMContext ) -> None:
    await state.set_state( ChatStates.chat )

    keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Yes"),
                        KeyboardButton(text="No"),
                    ]
                ],
                resize_keyboard=True,
            )
    await message.answer("I want you play a game!", reply_markup=keyboard)




##########################################################################################################################################################
# Chat
@router.message(ChatStates.chat)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(chat_user_input = message.text)
#    await state.set_state(ChatStates.drop)
    llm_answer_str, num_tokens, num_words = Mistral_7B_Instruct(message, state)
    await message.answer(f"{llm_answer_str}, {num_tokens}, {num_words}")

##########################################################################################################################################################
# Handlers





async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
