#from os import getenv
#import asyncpg
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Text, Bold
from aiogram.methods import PinChatMessage
from aiogram import Bot

from keyboards.keyboards import *
from db.queries import *
from classes import UIStates


router = Router()
##########################################################################################################################################################
# Main menu
##########################################################################################################################################################

##########################################################################################################################################################
# Start and help
@router.message(CommandStart())
#@router.message(CommandHelp())
async def command_start( message: Message, state: FSMContext ) -> None:
    await state.set_state( UIStates.chat )
    try:
        # Check if user exists in DB
        result = await show_user(user_id = message.from_user.id)
        if result == None:
            print("User not found")
            # Add new user with dafaults
            result = await add_user(user_id     = message.from_user.id,
                                    first_name  = message.from_user.first_name,
                                    last_name   = message.from_user.last_name,
                                    username    = message.from_user.username,
                                    language    = "English",
                                    prompt_id   = 1,
                                    model_id    = 1)
            print(f"User: {message.from_user.username} addes to DB")
        content = Text("Hello, ", Bold(message.from_user.first_name), "!")
        await message.answer(**content.as_kwargs())

        # Get detailed user status
        result = await user_status(user_id = message.from_user.id)
        if result != None:
            user_status_message = f"Your current model is:\n{result[5]}\n\nMy system prompt is:\n{result[6]}\n\n"
            await message.answer(user_status_message)
            # pin message
            # ??? how to get bot instance from main.py
            #bot = Bot.get_current()
            #await bot(PinChatMessage(chat_id=message.chat.id, message_id=message.message_id, disable_notification=True))
        else:
            print("Error! User has no status")
            raise Exception("User has no status")

    except Exception as e:
        print(e)
        await state.set_state( UIStates.db_error )
        await message.answer("Something went wrong, please try again later")
        return

    await main_menu(message, state)

##########################################################################################################################################################
# Main menu
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.chat)
    await message.answer("Waiting for a command", reply_markup = get_chat_kb())
##########################################################################################################################################################
# Chat Menu
@router.message(Command("menu"))
@router.message(F.text.casefold() == "chat menu")
async def chat_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.menu)
    await message.answer("Choose option", reply_markup = get_chat_options_kb())

##########################################################################################################################################################
# System Menu
@router.message(Command("sys"))
@router.message(F.text.casefold() == "system settings")
async def chat_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.sys)
    await message.answer("Choose option", reply_markup = get_system_options_kb())

##########################################################################################################################################################
# Cancel
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.chat )
    await main_menu(message, state)
