from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Bold, as_numbered_list, Text, as_line

from keyboards.keyboards import get_confirm_kb, get_system_chat_mode_kb, get_system_model_kb
from classes import UIStates
from handlers.main_menu import main_menu
from db.queries import select_all_system_prompts, select_all_models, update_user_llm_model, update_user_ai_persona, select_user_settings
from classes import bot
router = Router()

##########################################################################################################################################################
# System options
##########################################################################################################################################################

##########################################################################################################################################################
# Change chat setting
##########################################################################################################################################################
# Change chat personality
@router.message(UIStates.sys, F.text.casefold() == "ai personality")
async def sys_change_chat_persona(message: Message, state: FSMContext) -> None:
    system_prompts_available = await select_all_system_prompts()
    print(f"Available system prompts:\n{system_prompts_available}")
    await message.answer("Please, choose AI personality", reply_markup = get_system_chat_mode_kb())
    for i in range(len(system_prompts_available)):
        await message.answer(f"{i+1}. {system_prompts_available[i][0]}")
    await state.set_state( UIStates.sys_mode )
##########################################################################################################################################################
# Choose chat personality
@router.message(UIStates.sys_mode)
async def sys_choose_chat_persona(message: Message, state: FSMContext) -> None:
    system_prompts_available = await select_all_system_prompts()
    if message.text in ["1", "2", "3", "4", "5", "6"]:
        await update_user_ai_persona(user_id = message.from_user.id, prompt_id = int(message.text))
        await message.answer(f"I'm {system_prompts_available[int(message.text)-1][1]} now")
    else:
        await message.answer("Canceled")
    ##########################################################################################################################################################
    # Pin User settings
    # TODO make it def
    user_settings = await select_user_settings(user_id = message.from_user.id)
    print(f"User settings:\n{user_settings}")
    user_settings_message = await message.answer(f"Persona: {user_settings[0]}; \nmodel: {user_settings[1]}")
    await bot.unpin_all_chat_messages(message.chat.id)
    await bot.pin_chat_message(message.chat.id, user_settings_message.message_id, disable_notification = True)

    await state.set_state( UIStates.chat )
    await main_menu(message, state)

##########################################################################################################################################################
# LLM Model change
##########################################################################################################################################################
# Change LLM model
@router.message(UIStates.sys, F.text.casefold() == "ai model")
async def sys_change_llm_model(message: Message, state: FSMContext) -> None:
    models_available = await select_all_models()
    print(f"Available LLModels:\n{models_available}")
    await message.answer("Please, choose AI model", reply_markup = get_system_model_kb())
    for i in range(len(models_available)):
        await message.answer(f"{i+1}. {models_available[i][1]}")
    await state.set_state( UIStates.sys_ai_model )
    # content = Text(Bold("Please, choose AI from the list:\n"), as_numbered_list( "Mistral-7B-Instruct",
    #                             "Mixtral-8x7B-Instruct",
    #                             "Llama-13B",
    #                             "ChatGPT-4 online"))
    #await message.answer(**content.as_kwargs(), reply_markup = get_system_model_kb())
    #await state.set_state( UIStates.sys_ai_model )
##########################################################################################################################################################
# Choose LLM model
@router.message(UIStates.sys_ai_model)
async def sys_choose_llm_model(message: Message, state: FSMContext) -> None:
    models_available = await select_all_models()
    if message.text in ["1", "2"]:
        await update_user_llm_model(user_id = message.from_user.id, model_id = int(message.text))
        await message.answer(f"I am {models_available[int(message.text)-1][0]} now")
    else:
        await message.answer("Canceled")
    ##########################################################################################################################################################
    # Pin User settings
    # TODO make it def
    user_settings = await select_user_settings(user_id = message.from_user.id)
    print(f"User settings:\n{user_settings}")
    user_settings_message = await message.answer(f"Persona: {user_settings[0]}; \nmodel: {user_settings[1]}")
    await bot.unpin_all_chat_messages(message.chat.id)
    await bot.pin_chat_message(message.chat.id, user_settings_message.message_id, disable_notification = True)

    await state.set_state( UIStates.chat )
    await main_menu(message, state)

    # elif message.text.casefold() == "4":
    #     content = Text("Sorry, ChatGPT-4 not ready yet.\nCurrent model is\n", Bold("Mixtral-8x7B-Instruct"))
    #     await message.answer(**content.as_kwargs())
    #     await state.set_state( UIStates.chat )
    #     await main_menu(message, state)
    # else:
    #     content = Text("Current LLM model is\n", Bold("Mixtral-8x7B-Instruct"))
    #     await message.answer(**content.as_kwargs())
    #     await state.set_state( UIStates.chat )
    #     await main_menu(message, state)
##########################################################################################################################################################


##########################################################################################################################################################
# Change language
##########################################################################################################################################################
@router.message(UIStates.sys, F.text.casefold() == "language")
async def chat_reset_confirm(message: Message, state: FSMContext) -> None:
    await message.answer("English only, sorry.")
    await state.set_state( UIStates.chat )
    await main_menu(message, state)




# Example formatting
'''
content = as_list(
    as_marked_section(
        Bold("Success:"),
        "Test 1",
        "Test 3",
        "Test 4",
        marker="✅ ",
    ),
    as_marked_section(
        Bold("Failed:"),
        "Test 2",
        marker="❌ ",
    ),
    as_marked_section(
        Bold("Summary:"),
        as_key_value("Total", 4),
        as_key_value("Success", 3),
        as_key_value("Failed", 1),
        marker="  ",
    ),
    HashTag("#test"),
    sep="\n\n",
)
'''

