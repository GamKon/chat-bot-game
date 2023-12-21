from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.keyboards import get_confirm_kb
from classes import UIStates
from handlers.main_menu import main_menu
from handlers.ai import send_to_llm
from db.queries import *

router = Router()

##########################################################################################################################################################
# Chat options
##########################################################################################################################################################

##########################################################################################################################################################
# Clear last dialogue
@router.message(UIStates.menu, F.text.casefold() == "clear last dialogue")
async def chat_clear_last_dialog(message: Message, state: FSMContext) -> None:
    await delete_last_two_messages(user_id = message.from_user.id)
    await message.answer("Last dialogue is cleared")
    await state.set_state( UIStates.chat )
    await main_menu(message, state)
##########################################################################################################################################################
# Repeat last question
@router.message(UIStates.menu, F.text.casefold() == "repeat question")
async def chat_repeat_question(message: Message, state: FSMContext) -> None:
    await delete_last_message(user_id = message.from_user.id)
    await message.answer("Sure, I'll answer again.")
    await send_to_llm(message, state)
    await state.set_state( UIStates.chat )
    await main_menu(message, state)
##########################################################################################################################################################
# Reset confirm
@router.message(UIStates.menu, F.text.casefold() == "clear chat")
async def chat_reset_confirm(message: Message, state: FSMContext) -> None:
    await message.answer("All previuos context will be deleted!", reply_markup = get_confirm_kb())
    await state.set_state( UIStates.menu_confirm )
##########################################################################################################################################################
# Reset chat
@router.message(UIStates.menu_confirm)#, F.text.casefold() == "ok")
async def chat_reset(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == "ok":
        await delete_all_messages(user_id = message.from_user.id)
        await message.answer("Cleared. You may start over.")
        await state.set_state( UIStates.chat )
        await main_menu(message, state)
    else:
        await message.answer("Chat is not reset.")
        await state.set_state( UIStates.chat )
        await main_menu(message, state)
