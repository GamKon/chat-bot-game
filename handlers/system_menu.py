from aiogram import Router, html, F
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.formatting import Bold, as_numbered_list, Text, as_line
from aiogram.filters import Command
from aiogram.enums import ParseMode
from keyboards.keyboards import *
from classes import UIStates
from handlers.main_menu import main_menu
from db.queries import *
from classes import bot
from utility import pin_user_settings, get_number_emoji, get_emoji_number
from aiogram.types import CallbackQuery
from aiogram import html

router = Router()

##########################################################################################################################################################
# System options
##########################################################################################################################################################

##########################################################################################################################################################
# Change chat setting
##########################################################################################################################################################
# Change chat personality
@router.message(Command("pers"))
@router.message(UIStates.sys, F.text.casefold() == "💃 ai personality")
async def sys_change_chat_persona(message: Message, state: FSMContext) -> None:
    current_persona = await select_system_prompt(user_id = message.from_user.id)
    await message.answer(f"<b><i>Current system prompt:</i></b>\n{current_persona[0]}\n\n<b><i>Persona:</i></b> {current_persona[4]}\n<b><i>AI name:</i></b> {current_persona[2]}\n<b><i>User name:</i></b> {current_persona[1]}", parse_mode=ParseMode.HTML)

    system_prompts_available = await select_all_system_prompts(user_id = message.from_user.id)

    list_models = "<b><i>Please, choose AI personality</i></b>\n\n"
    for i in range(len(system_prompts_available)):
        list_models += f"{html.quote(get_emoji_number(i+1))} - <b>{html.quote(system_prompts_available[i][0])}</b>\n"
    await message.answer(list_models, reply_markup = get_system_chat_mode_kb(), parse_mode=ParseMode.HTML)
    await state.set_state( UIStates.sys_mode )
##########################################################################################################################################################
# Choose chat personality
@router.message(UIStates.sys_mode)
async def sys_choose_chat_persona(message: Message, state: FSMContext) -> None:
    if message.text in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]:
        system_prompts_available = await select_all_system_prompts(user_id = message.from_user.id)

        await update_user_ai_persona(user_id = message.from_user.id,
                                     prompt_id = system_prompts_available[get_number_emoji(message.text)-1][2])
        await pin_user_settings(message)
#        await main_menu(message, state)

    elif message.text.casefold() == "✍️ edit current":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        print(f"current_persona:\n{current_persona}")
        print("---------------------------------------------------------------")
#        if str(current_persona[3]) in ["1", "2"]:
##            await message.answer("It's read only, try #3 - #9", reply_markup = get_chat_kb())
 #           #await state.set_state( UIStates.chat )
 #           return
        #await message.answer(f"Current persona is:\n{current_persona[0]}")
        #await state.set_state(UIStates.chat)

        await message.answer(f"<b><i>Current system prompt:</i></b>\n{current_persona[0]}\n\n<b><i>Persona:</i></b> {current_persona[4]}\n<b><i>AI name:</i></b> {current_persona[2]}\n<b><i>User name:  </i></b> {current_persona[1]}", parse_mode=ParseMode.HTML, reply_markup = edit_system_prompt_kb())
        await message.answer("<i>Use buttons ⬆️ to edit personality.</i>", reply_markup = get_chat_kb(), parse_mode=ParseMode.HTML)
#        await state.set_state( UIStates.edit_system_prompt )
#        await edit_user_system_prompt(message, state)
#        await message.answer("Please edit system prompt", reply_markup = edit_system_prompt_kb())
        #await edit_user_system_prompt(message, state)
    # else:
    #     await message.answer("Canceled", reply_markup = get_chat_kb())
    await main_menu(message, state)

##########################################################################################################################################################
# Edit chat personality
@router.callback_query(F.data == "edit_system_prompt")
async def edit_user_system_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b><i>Enter new system prompt</i></b>", parse_mode=ParseMode.HTML, reply_markup = cancel_kb())
    #await UIStates.edit_system_prompt.set()
    await state.set_state( UIStates.edit_system_prompt_prompt )
##########################################################################################################################################################
@router.message(UIStates.edit_system_prompt_prompt)
async def edit_user_system_prompt_prompt(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        await edit_system_prompt(user_id = message.from_user.id, prompt_text = message.text, user_role_name = current_persona[1], ai_role_name = current_persona[2], save_name=current_persona[4])
        await message.answer(f"<i>Done.</i>")
        await pin_user_settings(message)
        await main_menu(message, state)
   # else:
#        await message.answer("Canceled", reply_markup = get_chat_kb())
   #     await main_menu(message, state)

##########################################################################################################################################################
# Edit your name
@router.callback_query(F.data == "edit_user_name")
async def edit_user_system_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b><i>Enter your name</i></b>", parse_mode=ParseMode.HTML, reply_markup = cancel_kb())
    #await UIStates.edit_system_prompt.set()
    await state.set_state( UIStates.edit_system_prompt_username )
##########################################################################################################################################################
@router.message(UIStates.edit_system_prompt_username)
async def edit_user_system_prompt_username(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        await edit_system_prompt(user_id = message.from_user.id, prompt_text = current_persona[0], user_role_name = message.text, ai_role_name = current_persona[2], save_name=current_persona[4])
        await message.answer(f"<i>Done. Your new name:  </i><b>{message.text}</b>", parse_mode=ParseMode.HTML)
        await main_menu(message, state)
   # else:
#        await message.answer("Canceled", reply_markup = get_chat_kb())
   #     await main_menu(message, state)
##########################################################################################################################################################
# Edit AI name
@router.callback_query(F.data == "edit_ai_name")
async def edit_user_system_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b><i>Enter AI name</i></b>", parse_mode=ParseMode.HTML, reply_markup = cancel_kb())
    #await UIStates.edit_system_prompt.set()
    await state.set_state( UIStates.edit_system_prompt_ai_name )
##########################################################################################################################################################
@router.message(UIStates.edit_system_prompt_ai_name)
async def edit_user_system_prompt_ai_name(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        await edit_system_prompt(user_id = message.from_user.id, prompt_text = current_persona[0], user_role_name = current_persona[1], ai_role_name = message.text, save_name=current_persona[4])
        await message.answer(f"<i>Done. My new chat name:  </i><b>{message.text}</b>", parse_mode=ParseMode.HTML)
        await main_menu(message, state)
   # else:
#        await message.answer("Canceled", reply_markup = get_chat_kb())
   #     await main_menu(message, state)

##########################################################################################################################################################
# Edit Save slot
@router.callback_query(F.data == "edit_save_slot")
async def edit_user_system_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b><i>Enter persona name</i></b>", parse_mode=ParseMode.HTML, reply_markup = cancel_kb())
    #await UIStates.edit_system_prompt.set()
    await state.set_state( UIStates.edit_system_prompt_save_name )
##########################################################################################################################################################
@router.message(UIStates.edit_system_prompt_save_name)
async def edit_user_system_prompt_ai_name(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        await edit_system_prompt(user_id = message.from_user.id, prompt_text = current_persona[0], user_role_name = current_persona[1], ai_role_name = current_persona[2], save_name=message.text)
        await message.answer(f"<i>Done. My persona name:  </i><b>{message.text}</b>", parse_mode=ParseMode.HTML)
        await main_menu(message, state)


##########################################################################################################################################################
# # Message
# @router.message(UIStates.edit_system_prompt)
# async def edit_user_system_prompt(message: Message, state: FSMContext) -> None:
#     await message.answer("Use buttons to change.", reply_markup = edit_system_prompt_kb())
#     await main_menu(message, state)
#     # if message.text.casefold() == "cancel":
#     #     await message.answer("Canceled", reply_markup = get_chat_kb())
#     #     await state.set_state( UIStates.chat )
#     #await state.set_state( UIStates.chat )
# # ai_name

##########################################################################################################################################################
# LLM Model change
##########################################################################################################################################################
# Change LLM model
@router.message(Command("model"))
@router.message(UIStates.sys, F.text.casefold() == "🤖 ai model")
async def sys_change_llm_model(message: Message, state: FSMContext) -> None:
    # Print current
    current_llm = await select_user_llm_model(user_id = message.from_user.id)
    await message.answer(f"<i>Current model:</i>\n<b>{current_llm[0]}</b>")
    # give  a list of available models
    models_available = await select_all_models()
    list_models = "<i>Which AI would you like to try?</i>\n\n"
    for i in range(len(models_available)-1):
        list_models += f"{html.quote(get_emoji_number(i+1))} - <b>{html.quote(models_available[i][1])}</b>\n\n"
    await message.answer(list_models, reply_markup = get_system_model_kb(), parse_mode=ParseMode.HTML)
    await state.set_state( UIStates.sys_ai_model )

##########################################################################################################################################################
# Choose LLM model
@router.message(UIStates.sys_ai_model)
async def sys_choose_llm_model(message: Message, state: FSMContext) -> None:
#    models_available = await select_all_models()
    if message.text in ["1️⃣", "2️⃣", "3️⃣"]:
        await update_user_llm_model(user_id = message.from_user.id, model_id = get_number_emoji(message.text))
#        await message.answer(f"<b><i>Current model:</i></b>\n\n{models_available[get_number_emoji(message.text)-1][0]}", reply_markup = get_chat_kb(), parse_mode=ParseMode.HTML)
        await pin_user_settings(message)
    elif message.text.casefold() == "35":
        await update_user_llm_model(user_id = message.from_user.id, model_id = 35)
        await pin_user_settings(message)
    # else:
    #     await message.answer("Canceled", reply_markup = get_chat_kb())

    await main_menu(message, state)
    #await state.set_state( UIStates.chat )

##########################################################################################################################################################
# Change language
##########################################################################################################################################################
# @router.message(UIStates.sys, F.text.casefold() == "language")
# async def chat_reset_confirm(message: Message, state: FSMContext) -> None:
#     await message.answer("English only, sorry.", reply_markup = get_chat_kb())
#     await state.set_state( UIStates.chat )

##########################################################################################################################################################
