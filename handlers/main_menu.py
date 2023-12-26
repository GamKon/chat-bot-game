#from os import getenv
#import asyncpg
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Text, Bold
from aiogram.methods import PinChatMessage
from aiogram import Bot

from keyboards.keyboards import *
from db.queries import *
from classes import UIStates
from utility import pin_user_settings
from handlers.ai import send_to_llm
from models.openai_whisper_large_v3 import openai_whisper_large_v3

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
    # data = await state.update_data(is_thinking = False)
    # print("-----------------!!!!!!!-!!!!!!!START!!!!DATA\n")
    # print(data)
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
                                    model_id    = 1)
            print(f"User: {message.from_user.username} added to DB")
            await add_default_user_prompts(user_id = message.from_user.id)
        content = Text("Hello, ", Bold(message.from_user.first_name), "!\n\nI'm a chatbot that can talk to you in different roles. You can give me any personality you like.\nCurrent settings:")
        await message.answer(**content.as_kwargs())

        # Get detailed user status
        result = await user_status(user_id = message.from_user.id)
        if result != None:
            await pin_user_settings(message)
            await main_menu(message, state)
        else:
            # print("-----------1")
            # await add_default_user_prompts(user_id = message.from_user.id)
            # print("-----------1")
            print("Error! User has no status")
            raise Exception("User has no status")

    except Exception as e:
        print(e)
        await state.set_state( UIStates.db_error )
        await message.answer("⛔ Something went wrong, please try again later", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
        return

    #await main_menu(message, state)

##########################################################################################################################################################
# Main menu
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.chat)
    await message.answer("<i>Talk to me </i>😏", reply_markup = get_chat_kb(), parse_mode = "HTML")
##########################################################################################################################################################
# Chat Menu
@router.message(Command("menu"))
@router.message(F.text.casefold() == "📝 chat menu")
async def chat_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.menu)
    await message.answer("<i>Choose option</i>", reply_markup = get_chat_options_kb(), parse_mode = "HTML")

##########################################################################################################################################################
# System Menu
@router.message(Command("sys"))
@router.message(F.text.casefold() == "🔧 system settings")
async def chat_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(UIStates.sys)
    await message.answer("<i>Choose option</i>", reply_markup = get_system_options_kb(), parse_mode = "HTML")

##########################################################################################################################################################
# Cancel
@router.message(Command("cancel"))
@router.message(UIStates.sys,           F.text.casefold() == "❌ cancel")
@router.message(UIStates.menu,          F.text.casefold() == "❌ cancel")
@router.message(UIStates.menu_confirm,  F.text.casefold() == "❌ cancel")
@router.message(UIStates.sys_mode,      F.text.casefold() == "❌ cancel")
@router.message(UIStates.sys_ai_model,  F.text.casefold() == "❌ cancel")
@router.message(UIStates.edit_system_prompt_prompt,  F.text.casefold() == "❌ cancel")
@router.message(UIStates.edit_system_prompt_username,  F.text.casefold() == "❌ cancel")
@router.message(UIStates.edit_system_prompt_ai_name,  F.text.casefold() == "❌ cancel")
@router.message(UIStates.edit_system_prompt_save_name,  F.text.casefold() == "❌ cancel")

async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.chat )
    await message.answer("<i>Canceled</i>", reply_markup = get_chat_kb(),parse_mode = "HTML")

##########################################################################################################################################################
# DB Error
@router.message(UIStates.db_error)
async def db_error(message: Message, state: FSMContext) -> None:
    await message.answer("Please use /start to start over", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

##########################################################################################################################################################
# Voice message
@router.message(F.voice)
async def download_voice(message: Message, state: FSMContext, bot: Bot):
    await bot.download(
        message.voice,
# TODO save file to memory only
        destination=f"data/voice/{message.voice.file_id}.ogg",
    )
    transcript = openai_whisper_large_v3(f"data/voice/{message.voice.file_id}.ogg")
    data = await state.update_data(transcript = transcript)
    # Save transcript to state
    await state.set_state( UIStates.confirm_send_transcript )
    await message.answer(f"<i>It looks like you said:</i>\n\n{transcript}\n\n<i>Send it to the chat?</i>", reply_markup = get_confirm_kb())
# Send transcript to LLM
@router.message(UIStates.confirm_send_transcript)
async def send_transcript(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == "✅ ok":
#        await message.answer("Sent", reply_markup = get_chat_kb())
        # Get transcript from state
        data = await state.get_data()
        message_to_llm = data["transcript"]
        print(f"message.text from transcript:\n{message_to_llm.strip()}")
        await send_to_llm(message, state, message_to_llm.strip())
    else:
        await message.answer("<i>Canceled</i>", reply_markup = get_chat_kb())
    await state.set_state( UIStates.chat )
