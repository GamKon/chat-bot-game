from time import sleep
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums.chat_action import ChatAction
# from aiogram.methods import SendChatAction
#from aiogram import Bot

from models.Mistral_7B_Instruct_v0_2 import Mistral_7B_Instruct
from models.Mixtral_8x7B_Instruct_v0_1 import Mixtral_8x7B_Instruct

from classes import UIStates
from classes import bot
from db.queries import *

router = Router()

##########################################################################################################################################################
# Chat options
##########################################################################################################################################################

##########################################################################################################################################################
# App logic
# Send to LLM
#@router.message() NONE ???
@router.message(UIStates.chat)
async def send_to_llm(message: Message, state: FSMContext) -> None:
    # ???
    await state.update_data(chat_user_input = message.text)
    bot_message = await message.answer("Let me think...")
    ###########################################################
    # Prepare prompt for LLM
    # make messages list from DB in STRING format
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        system_role_prompt = await select_system_prompt(message.from_user.id)
        print(f"*** System prompt ***:\n{system_role_prompt[0]}")
        messages_history = await select_user_chat_history(user_id = message.from_user.id)
        print(f"*** Messages ***:\n{messages_history}")
        prompt_to_llm = "<s>[INST] <<SYS>>\n" + system_role_prompt[0] + "\n<</SYS>>\n\n"
        for prompt in messages_history:
            # TODO add custom role names
            if prompt[0] == "user":
                prompt_to_llm += prompt[1] + " [/INST] "
            else:
                prompt_to_llm += prompt[1] + "</s>[INST] "
        prompt_to_llm += message.text + " [/INST]"
        ###########################################################
        # Send prompt to LLM
        current_user_model = await select_user_llm_model(message.from_user.id)
        # 10 tries to handle ValueError: Found modules on cpu/disk.
        for i in range(1, 10):
            try:
                if current_user_model[0] == "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ":
                    # async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id, action = "typing"):
                    llm_answer = await Mistral_7B_Instruct(str(prompt_to_llm))
                elif current_user_model[0] == "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ":
                    # async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id, action = "typing"):
                    llm_answer = await Mixtral_8x7B_Instruct(str(prompt_to_llm))
                else:
                    llm_answer = "Error! No model selected\n" + str(current_user_model)
                    await bot_message.edit_text(llm_answer)
                    return
                break
            except (ValueError, RuntimeError) as e:
                # Print error message
                if i < 9:
                    await message.answer("Still thinking...\n" + str(e) + "\nRetry #"+str(i))
                else:
                    await message.answer("Nothing came to my mind, sorry (\n" + str(e))
                    return
                sleep(5)
        # Save to DB
        await add_message(user_id = message.from_user.id, role = "user", content = message.text)
        await add_message(user_id = message.from_user.id, role = "assistant", content = llm_answer)
        await bot_message.edit_text(llm_answer)

# ##########################################################################################################################################################
# For future use for templates in conversational pipeline
# ###########################################################
#     # Prepare prompt for LLM
#     # make messages list from DB in JSON format
#     system_role_prompt = await select_system_prompt(message.from_user.id)
#     print(f"*** System prompt ***:\n{system_role_prompt[0]}")
#     messages_history = await select_user_chat_history(user_id = message.from_user.id)
#     print(f"*** Messages ***:\n{messages_history}")
#     prompt_to_llm.append({"role": "system", "prompt": system_role_prompt[0]})
#     for prompt in messages_history:
#         prompt_to_llm.append({"role": prompt[0], "prompt": prompt[1]})
#     prompt_to_llm.append({"role": "user", "prompt": message.text})
#     ###########################################################


##########################################################################################################################################################
    # TODO: Add chat action
    # Want to set status TYPING to chat, but it doesn't work
    # ??? Not working
    # async with ChatActionSender.typing(bot = Bot, chat_id=message.chat.id):
    #     await message.answer(f"1!!!!!!!!!!!!!")
    # #     # Do something...
    # #     sleep(15)
    #     sleep(15)
    #     await message.answer(f"2!!!!!!!!!!!!!")

# Doesn't work
    # async with ChatActionSender.typing(chat_id=message.chat.id):
    #     # Do something...
    #     sleep(15)
    #     await message.answer(f"!!!!!!!!!!!!!")

# use of ChatActionSender
    # await ChatActionSender("typing")
    # sleep(15)

#    async with ChatActionSender.typing(bot=Bot, chat_id=message.chat.id):
        # Do something...
        # Perform some long calculations
    #await message.answer_chat_action("typing")

    # async def answer(message: types.Message):
    #     await message.answer_chat_action("typing")
    #     await message.answer("Hi!")
