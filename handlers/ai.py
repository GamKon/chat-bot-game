from time import sleep
from aiogram import Router, html
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums.chat_action import ChatAction
# from aiogram.methods import SendChatAction
#from aiogram import Bot
from utility        import debug_print

from models.llm_awq_gptq     import llm_answer_from_model
from models.llm_gguf    import llm_answer_from_gguf

from models.openai_chatgpt  import gpt_3_5_turbo_1106
from models.playgroundai    import playground_v2_1024px_aesthetic
from models.OpenDalleV1_1   import OpenDalleV1_1

from handlers.main_menu     import main_menu
from classes                import UIStates, bot
from db.queries             import *
from templating             import chat_template
from keyboards.keyboards    import get_chat_kb

router = Router()

##########################################################################################################################################################
# Chat options
##########################################################################################################################################################

##########################################################################################################################################################
# App logic
# Send to LLM
#@router.message() NONE ???
@router.message(UIStates.chat)
async def send_to_llm(message: Message, state: FSMContext, message_to_llm: str = "") -> None:

    # TODO Use Sync to Async wrapper to avoid blocking
    # dp.message.middleware(ai.ai_middleware)
    # asgiref.sync.sync_to_async
    # #Try to stop accepting messages while LLM is thinking
    # data = await state.get_data()
    # if "is_thinking" not in data:
    #     data = await state.update_data(is_thinking = False)
    # else:
    #     print("______is_thinking in data______\n")
    # if data["is_thinking"]:
    #     await message.reply("I'm still thinking at the first question, please be patient")
    #     return

    # Emoji "Thinking..."
    emoji_message = await message.answer("🤔", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

    current_user_model = await select_user_llm_model(message.from_user.id)

    # Set maximum answer length max_new_tokens
    current_user_system_prompt = await select_system_prompt(user_id = message.from_user.id)
    max_new_tokens = current_user_system_prompt[5]
    if max_new_tokens <= 20 and max_new_tokens >= 2048:
        debug_print("Defaulting max_new_tokens to 256, in DB it's out of range:", max_new_tokens)
        max_new_tokens = 256

    # Set status "Typing..."
    #async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):

    ###########################################################
    # Get User input
    # TODO make seperate function instead of checking for 'state' if coming from voice transcript Whisper
    current_state = await state.get_state()
    if current_state == "UIStates:confirm_send_transcript":
        message_to_llm = message_to_llm
    else:
        message_to_llm = message.text
    debug_print("User input before templating: message_to_llm", message_to_llm)

    # Template whole string to send depending on format
    prompt_to_llm = await chat_template(message_to_llm, message, format_to = current_user_model[2], use_names = current_user_model[3])

    ###########################################################
    # Prepare prompt for LLM
    # make messages list from DB in STRING format

    ###########################################################
    # Send prompt to LLM
    # 5 tries to handle recoverable model Errors
    for i in range(1, 3):
        try:
            # Stop accepting messages while LLM is thinking
            # data = await state.update_data(is_thinking = True)
            # TODO Use Sync to Async wrapper to avoid blocking

            ###########################################
            # Chat-GPT 3.5
            if current_user_model[0] == "gpt-3.5-turbo-1106":
                llm_answer = await gpt_3_5_turbo_1106(prompt_to_llm)
            ###########################################
            # GGUF model format
            elif ".gguf" in current_user_model[0]:
                llm_answer, num_tokens = await llm_answer_from_gguf(
                                                    prompt_to_llm,
                                                    current_user_model,
                                                    max_new_tokens
                                                )
            ###########################################
            # AWQ and GPTQ model formats
            elif ("AWQ" in current_user_model[0]) or ("GPTQ" in current_user_model[0]):
                num_tokens = [""]
                llm_answer = await llm_answer_from_model(
                                        prompt_to_llm,
                                        current_user_model,
                                        max_new_tokens
                                    )
            break
        except (RuntimeError, ValueError) as e:
            # Print error message
            if i < 2:
                await message.answer("Still thinking...\n" + html.quote(str(e)) + "\nRetry #" + str(i))
            else:
                await message.answer("Nothing came to my mind, sorry (\n" + html.quote(str(e)), reply_markup = get_chat_kb())
                return
            sleep(5)
        except (TypeError, NameError, Exception) as e:
            await message.answer("Nothing came to my mind, sorry (\n" + html.quote(str(e)), reply_markup = get_chat_kb())
            return

    # No need any more. TEST it!
    # Remove AI name from answer if any
    # if current_user_system_prompt[2] != "":
    #     llm_answer = str(llm_answer.split(f"{current_user_system_prompt[2]}:",1)[-1]).lstrip()
    #     debug_print("Splitting AI name from answer", current_user_system_prompt[2])
    # llm_answer = llm_answer.strip()


    # Summarize llm_answer
    summ_llm_answer = await summarize_text( text    = llm_answer,
                                            model   = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
                                            max_new_tokens = 128 )

    # Save to DB
    await add_message(user_id = message.from_user.id, author = "user", content = message_to_llm, summ_content = "")
    await add_message(user_id = message.from_user.id, author = "ai", content = llm_answer, summ_content = summ_llm_answer)
    await emoji_message.delete()
#    await message.edit_text("💡")
    #await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    if len(llm_answer) > 4096:
        llm_answer = llm_answer[:4000] + "...truncated..."
    try:
        await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    except Exception as e:
        await message.answer("Error! Can't send message\n" + html.quote(str(e)), reply_markup = get_chat_kb())
    # Illustrate if 'game' in Model.name
    if 'game' in current_user_system_prompt[4].lower():
        print("!!--- Gonna Illustrate ---!!")
        try:
            await illustrate(message, state, summ_llm_answer, current_user_system_prompt[4].lower())
        except Exception as e:
            await message.answer("Error! Can't illustrate\n" + html.quote(str(e)), reply_markup = get_chat_kb())

##########################################################################################################################################################
# Summarize text
async def summarize_text(text: str, model: str = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ", max_new_tokens: int = 1000) -> str:
    string_to_summarize  = "Summarize this: '" + text + "'. Very short summary:"
#    debug_print("String to summarize", string_to_summarize)
    summarized_text = await llm_answer_from_model(string_to_summarize,
                                                [model],
                                                max_new_tokens)
#    debug_print("Summarized text", summarized_text)
    return summarized_text

##########################################################################################################################################################
# Illustrate the answer
async def illustrate(message: Message, state: FSMContext, summ_llm_answer: str, game_type: str) -> None:
    num_inference_steps = 70

    emoji_message       = await message.answer("🎨", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

    picture_description = game_type.replace("game", "") + " " + str(summ_llm_answer.split("\n")[0]).strip()
    debug_print("Picture description", picture_description)

    # playground accepts only 77 tokens
    result_image_path   = await OpenDalleV1_1(prompt = picture_description, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)

    await emoji_message.delete()

    try:
        await message.answer_photo(result_image, picture_description[:980])
    except Exception as e:
        await message.answer(f"Error! Can't send image\n'{picture_description}'\n{html.quote(str(e))}", reply_markup = get_chat_kb())


    emoji_message       = await message.answer("🎨", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
    result_image_path   = await playground_v2_1024px_aesthetic(prompt = picture_description, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)

    await emoji_message.delete()
    try:
        await message.answer_photo(result_image)
    except Exception as e:
        await message.answer(f"Error! Can't send second image\n'{picture_description}'\n{html.quote(str(e))}", reply_markup = get_chat_kb())

    # Anime model
    # result_image_path   = await animagine_xl_2_0(prompt = picture_description, file_path="data/generated_images", n_steps=num_inference_steps)

    await main_menu(message, state)
