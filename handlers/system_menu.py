from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Bold, as_numbered_list, Text, as_line
from aiogram.filters import Command

from keyboards.keyboards import *
from classes import UIStates
from handlers.main_menu import main_menu
from db.queries import *
from classes import bot
from utility import pin_user_settings
router = Router()

##########################################################################################################################################################
# System options
##########################################################################################################################################################

##########################################################################################################################################################
# Change chat setting
##########################################################################################################################################################
# Change chat personality
@router.message(Command("pers"))
@router.message(UIStates.sys, F.text.casefold() == "ai personality")
async def sys_change_chat_persona(message: Message, state: FSMContext) -> None:
    current_persona = await select_system_prompt(user_id = message.from_user.id)
    await message.answer(f"Current system prompt is:\n{current_persona[0]}")

    system_prompts_available = await select_all_system_prompts(user_id = message.from_user.id)

    list_models = "Please, choose AI personality\n\n"
    for i in range(len(system_prompts_available)):
        list_models += f"{i+1}. {system_prompts_available[i][0]}\n"
    await message.answer(list_models, reply_markup = get_system_chat_mode_kb())
    await state.set_state( UIStates.sys_mode )
##########################################################################################################################################################
# Choose chat personality
@router.message(UIStates.sys_mode)
async def sys_choose_chat_persona(message: Message, state: FSMContext) -> None:
    if message.text in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        system_prompts_available = await select_all_system_prompts(user_id = message.from_user.id)

        await update_user_ai_persona(user_id = message.from_user.id,
                                     prompt_id = system_prompts_available[int(message.text)-1][2])
        await pin_user_settings(message)
        await main_menu(message, state)
    # elif message.text.casefold() == "show":
    #     current_persona = await select_system_prompt(user_id = message.from_user.id)
    #     await message.answer(f"Current persona is:\n{current_persona[0]}")
    #     return
    elif message.text.casefold() == "edit current":
        current_persona = await select_system_prompt(user_id = message.from_user.id)
        print(f"current_persona:\n{current_persona}")
        print("---------------------------------------------------------------")
        if str(current_persona[3]) in ["1", "2"]:
            await message.answer("It's read only, try #3 - #9", reply_markup = get_chat_kb())
            #await state.set_state( UIStates.chat )
            return
        #await message.answer(f"Current persona is:\n{current_persona[0]}")
        await state.set_state(UIStates.edit_system_prompt)
        await message.answer("Please enter new system prompt", reply_markup = cancel_kb())
        #await edit_user_system_prompt(message, state)
    else:
        await message.answer("Canceled", reply_markup = get_chat_kb())
        await state.set_state( UIStates.chat )
##########################################################################################################################################################
# Edit chat personality
@router.message(UIStates.edit_system_prompt)
async def edit_user_system_prompt(message: Message, state: FSMContext) -> None:
    #current_persona = await select_system_prompt(user_id = message.from_user.id)
    #await message.answer(f"Current persona is:\n{current_persona[0]}")
#    await message.answer("Please enter new system prompt", reply_markup = get_confirm_kb())
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n{message.text}\n!!!!!!!!!!!!")
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n{message.text.casefold()}\n!!!!!!!!!!!!")
    print(len(message.text))

    if message.text.casefold() == "cancel":
        await message.answer("Canceled", reply_markup = get_chat_kb())
        await state.set_state( UIStates.chat )

    elif len(message.text) > 0 :
        await edit_system_prompt(user_id = message.from_user.id, prompt_text = message.text)
        await pin_user_settings(message)
        await main_menu(message, state)
    else:
        await message.answer("Can't be empty", reply_markup = get_chat_kb())
    await state.set_state( UIStates.chat )

##########################################################################################################################################################
# LLM Model change
##########################################################################################################################################################
# Change LLM model
@router.message(Command("model"))
@router.message(UIStates.sys, F.text.casefold() == "ai model")
async def sys_change_llm_model(message: Message, state: FSMContext) -> None:
    # Print current
    current_llm = await select_user_llm_model(user_id = message.from_user.id)
    await message.answer(f"Current model is:is: #{current_llm[1]}\n{current_llm[0]}")
    # give  a list of available models
    models_available = await select_all_models()
    list_models = "Please, choose AI model:\n\n"
    for i in range(len(models_available)-1):
        list_models += f"{i+1}. {models_available[i][1]}\n\n"
    await message.answer(list_models, reply_markup = get_system_model_kb())
    await state.set_state( UIStates.sys_ai_model )

##########################################################################################################################################################
# Choose LLM model
@router.message(UIStates.sys_ai_model)
async def sys_choose_llm_model(message: Message, state: FSMContext) -> None:
    models_available = await select_all_models()
    if message.text in ["1", "2", "3"]:
        await update_user_llm_model(user_id = message.from_user.id, model_id = int(message.text))
        await message.answer(f"I'm:\n{models_available[int(message.text)-1][0]}", reply_markup = get_chat_kb())
    elif message.text.casefold() == "35":
        await update_user_llm_model(user_id = message.from_user.id, model_id = 35)
    else:
        await message.answer("Canceled", reply_markup = get_chat_kb())
    await pin_user_settings(message)
    await main_menu(message, state)
    #await state.set_state( UIStates.chat )

# Depreciated
# ##########################################################################################################################################################
# # Prompt format change
# ##########################################################################################################################################################
# # Change prompt templating format
# @router.message(UIStates.sys, F.text.casefold() == "format")
# async def sys_change_template_format(message: Message, state: FSMContext) -> None:
#     # Print current
#     current_llm = await select_user_llm_model(user_id = message.from_user.id)
#     await message.answer(f"Current template format:\n{current_llm[2]}\n\nChoose new template format:\n1 - Mistral\n2 - ChatML\n3 - json\n* if you don't know what it is, don't change - use Mistral", reply_markup = get_template_format_kb())
#     # give  a list of available models
#     await state.set_state( UIStates.sys_template_format )
# ##########################################################################################################################################################
# # Choose prompt template formatl
# @router.message(UIStates.sys_template_format)
# async def sys_choose_llm_model(message: Message, state: FSMContext) -> None:
#     #models_available = await select_all_models()
#     if message.text.casefold() in ["mistral", "chatml", "json"]:
#         await update_user_template_format(user_id = message.from_user.id, prompt_format = message.text)
#         await message.answer(f"Done. Format is: {message.text}", reply_markup = get_chat_kb())
#     else:
#         await message.answer("Canceled", reply_markup = get_chat_kb())
#     await main_menu(message, state)



##########################################################################################################################################################
# Change language
##########################################################################################################################################################
# @router.message(UIStates.sys, F.text.casefold() == "language")
# async def chat_reset_confirm(message: Message, state: FSMContext) -> None:
#     await message.answer("English only, sorry.", reply_markup = get_chat_kb())
#     await state.set_state( UIStates.chat )

##########################################################################################################################################################


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

