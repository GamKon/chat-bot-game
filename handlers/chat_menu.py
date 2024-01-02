from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
#from aiogram.enums import ParseMode

from keyboards.keyboards import get_confirm_kb, get_chat_kb
from classes import UIStates
from handlers.main_menu import main_menu
from handlers.ai import send_to_llm
from db.queries import *

router = Router()

##########################################################################################################################################################
# Chat options
##########################################################################################################################################################

##########################################################################################################################################################
# Repear last question
@router.message(Command("repeat"))
@router.message(UIStates.menu, F.text.casefold() == "🔁 repeat last")
async def chat_repeat_question(message: Message, state: FSMContext) -> None:
    try:
        # Get user's last question from DB
        last_question = await select_last_question(user_id = message.from_user.id)
        # Delete last dialogue from DB
        await delete_last_two_messages(user_id = message.from_user.id)
        # Send last question to LLM
# TODO make another def to call send_to_llm from anywhere
        await state.set_state( UIStates.confirm_send_transcript )
        await send_to_llm(message, state, last_question[0])
#        await message.answer("<i>Let me think again...</i>", reply_markup=get_chat_kb(), parse_mode="HTML")
    except (TypeError) as e:
        await message.answer("<i>Chat is empty </i>🤐", reply_markup=get_chat_kb(), parse_mode="HTML")
    await state.set_state( UIStates.chat )

##########################################################################################################################################################
# Clear last dialogue
@router.message(Command("clear"))
@router.message(UIStates.menu, F.text.casefold() == "✏️ clear last")
async def chat_clear_last_dialog(message: Message, state: FSMContext) -> None:
    try:
        await delete_last_two_messages(user_id = message.from_user.id)
        await message.answer("<i>Last dialogue is cleared</i>", reply_markup=get_chat_kb(), parse_mode="HTML")
    except (TypeError) as e:
        await message.answer("<i>Chat is empty </i>🤐", reply_markup=get_chat_kb(), parse_mode="HTML")
    await state.set_state( UIStates.chat )

##########################################################################################################################################################
# Show history
@router.message(Command("show"))
@router.message(UIStates.menu, F.text.casefold() == "🗒️ show history")
async def chat_show_history(message: Message, state: FSMContext) -> None:
    current_user_system_prompt = await select_system_prompt(message.from_user.id)
    roles = [current_user_system_prompt[1], current_user_system_prompt[2]]
    user_role_name      = "User:" if roles[0] == "" else f"{roles[0]}:"
    assistant_role_name = "AI:"   if roles[1] == "" else f"{roles[1]}:"
    try:
        messages_history = await select_user_chat_history(user_id = message.from_user.id)
        for prompt in messages_history:
            # Check for message's Author form Messages table (user, ai)
            if prompt[0].lower() == "user":
                dialog = f"<b><i>{user_role_name}</i></b>\n{prompt[1]}"
            elif prompt[0].lower() == "ai":
                # Remove assistant role name from prompt if AI added it
                if assistant_role_name != "":
                    assistant_prompt = prompt[1].replace(assistant_role_name, "", 1)
                else:
                    assistant_prompt = prompt[1]
                # Add ai message to prompt
                dialog = f"<b><i>{assistant_role_name}</i></b>\n{assistant_prompt}"
            await message.answer(dialog, reply_markup=get_chat_kb(), parse_mode="HTML")
                              #html.quote()
        if messages_history  == []:
            await message.answer("<i>Chat is empty </i>🤐", reply_markup=get_chat_kb(), parse_mode="HTML")
    except:
        await message.answer("Something went wrong 👾\nPlease try again later", reply_markup=get_chat_kb())
    await state.set_state( UIStates.chat )


##########################################################################################################################################################
# Repeat last question
# TODO Add logic to send last question to LLM
# @router.message(UIStates.menu, F.text.casefold() == "repeat question")
# async def chat_repeat_question(message: Message, state: FSMContext) -> None:
#     await delete_last_message(user_id = message.from_user.id)
#     await message.answer("Sure, I'll answer again.")
#     await send_to_llm(message, state)
#     await state.set_state( UIStates.chat )
##########################################################################################################################################################
# Reset confirm
@router.message(Command("erase"))
@router.message(UIStates.menu, F.text.casefold() == "🚧 clear chat")
async def chat_reset_confirm(message: Message, state: FSMContext) -> None:
    await message.answer("⚠️ <b>All history will be deleted!</b> ⚠️", reply_markup = get_confirm_kb(), parse_mode="HTML")
    await state.set_state( UIStates.menu_confirm )
##########################################################################################################################################################
# Reset chat
@router.message(UIStates.menu_confirm)#, F.text.casefold() == "✅ Ok")
async def chat_reset(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == "✅ ok":
        await delete_all_messages(user_id = message.from_user.id)
        await message.answer("<i>Cleared ☠️ You may start over.</i>", reply_markup=get_chat_kb(), parse_mode="HTML")
        await state.set_state( UIStates.chat )
    else:
        await message.answer("👍 Cancel. Keep going.", reply_markup=get_chat_kb())
        await state.set_state( UIStates.chat )
