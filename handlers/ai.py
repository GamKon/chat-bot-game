from time import sleep
from aiogram import Router, html
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums.chat_action import ChatAction
# from aiogram.methods import SendChatAction
#from aiogram import Bot
from utility import debug_print
from models.llm import llm_answer_from_model

from models.GPTQ_Mistral_7B_Instruct_v0_2   import Mistral_7B_Instruct, Mistral_7B_Instruct_pipeline
from models.GPTQ_Mixtral_8x7B_Instruct_v0_1 import GPTQ_Mixtral_8x7B_Instruct, GPTQ_Mixtral_8x7B_Instruct_pipeline
from models.AWQ_dolphin_2_2_yi_34b          import AWQ_Dolphin_2_2_yi_34b_pipe
from models.AWQ_Mixtral_8x7B_Instruct_v0_1  import AWQ_Mixtral_8x7B_Instruct_pipe, AWQ_Mixtral_8x7B_Instruct
from models.AWQ_Mistral_7B_Instruct_v0_2    import AWQ_Mistral_7B_Instruct_pipe
from models.AWQ_Guanaco_13B                 import AWQ_Guanaco_13B_Uncensored_AWQ, AWQ_Guanaco_13B_Uncensored_AWQ_pipe
from models.Mistral_7B_Instruct_v0_2        import Mistral_7B_Instruct_pipe
from models.AWQ_LLaMA2_13B_Psyfighter2      import AWQ_LLaMA2_13B_Psyfighter2
from models.AWQ_LLaMA2_13B_Tiefighter       import AWQ_LLaMA2_13B_Tiefighter
from models.Aurora_Nights_70B_v1_0_AWQ      import AWQ_Aurora_Nights_70B_v1_0, AWQ_Aurora_Nights_70B_v1_0_pipe
from models.WizardLM_33B_V1_0_AWQ           import WizardLM_33B_V1_0_AWQ, WizardLM_33B_V1_0_AWQ_pipe
from models.Pygmalion_2_13B_AWQ             import Pygmalion_2_13B_AWQ
from models.openai_chatgpt                  import gpt_3_5_turbo_1106
from models.playgroundai                    import playground_v2_1024px_aesthetic
from models.OpenDalleV1_1                   import OpenDalleV1_1
from models.stable_diffusion                import stable_diffusion_xl_base_1_0, stable_diffusion_xl_base_refiner_1_0
from models.Linaqruf_animagine_xl_2_0       import animagine_xl_2_0

from handlers.main_menu             import main_menu

from classes import UIStates, bot
from db.queries import *
from templating import chat_template
from keyboards.keyboards import get_chat_kb

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
    prompt_to_llm = await chat_template(message_to_llm, message, format_to = current_user_model[2])

    ###########################################################
    # Prepare prompt for LLM
    # make messages list from DB in STRING format

    ###########################################################
    # Send prompt to LLM
    # 5 tries to handle recoverable model Errors
    for i in range(1, 7):
        try:
                # Stop accepting messages while LLM is thinking
                # data = await state.update_data(is_thinking = True)
                # TODO Use Sync to Async wrapper to avoid blocking

            ###########################################
            # Get llm_answer from LLM

            ###########################################
            # Chat-GPT 3.5
            if current_user_model[0] == "gpt-3.5-turbo-1106":
                llm_answer = await gpt_3_5_turbo_1106(prompt_to_llm)
            else:
                llm_answer = await llm_answer_from_model(prompt_to_llm,
                                                         current_user_model,
#                                                         current_user_system_prompt,
                                                         max_new_tokens)
#                                                         message,
#                                                         state)
                # llm_answer = await AWQ_Mistral_7B_Instruct_pipe(prompt_to_llm, max_new_tokens)
            ###########################################
            # Mixtral-8x7B-Instruct
            # elif current_user_model[0] == "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ":
            #     # GPTQ quantized
            #     llm_answer = await GPTQ_Mixtral_8x7B_Instruct_pipeline(prompt_to_llm, max_new_tokens)
            ###########################################
            # # Dolphin-2_2-yi-34b-AWQ
            # elif current_user_model[0] == "TheBloke/dolphin-2_2-yi-34b-AWQ":
            #     llm_answer = await AWQ_Dolphin_2_2_yi_34b_pipe(prompt_to_llm, max_new_tokens)
            ###########################################
            # LLaMA2_13B_Psyfighter2-AWQ
            # elif current_user_model[0] == "TheBloke/LLaMA2-13B-Psyfighter2-AWQ":
            #     llm_answer = await AWQ_LLaMA2_13B_Psyfighter2(prompt_to_llm, max_new_tokens)
            # ###########################################
            # # LLaMA2_13B_Tiefighter-AWQ
            # elif current_user_model[0] == "TheBloke/LLaMA2-13B-Tiefighter-AWQ":
            #     llm_answer = await AWQ_LLaMA2_13B_Tiefighter(prompt_to_llm, max_new_tokens)
            ###########################################
            # Aurora-Nights-70B-v1.0-AWQ
            # elif current_user_model[0] == "TheBloke/Aurora-Nights-70B-v1.0-AWQ":
            #     llm_answer = await AWQ_Aurora_Nights_70B_v1_0_pipe(prompt_to_llm, max_new_tokens)
            ###########################################
            # WizardLM-33B-V1.0-Uncensored-AWQ
            # elif current_user_model[0] == "TheBloke/WizardLM-33B-V1.0-Uncensored-AWQ":
            #     llm_answer = await WizardLM_33B_V1_0_AWQ(prompt_to_llm, max_new_tokens)
            ###########################################
            # Pygmalion-2-13B-AWQ
# Start to add user question by itself on long input
            # elif current_user_model[0] == "TheBloke/Pygmalion-2-13B-AWQ":
            #     llm_answer = await Pygmalion_2_13B_AWQ(prompt_to_llm, max_new_tokens)





                # Other not working models

                # This IS NOT expected if you are initializing MixtralForCausalLM from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).
                # You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
                # OC is not multiple of cta_N = 64
                # llm_answer = await AWQ_Mixtral_8x7B_Instruct(prompt_to_llm)
                # llm_answer = await AWQ_Mixtral_8x7B_Instruct_pipe(prompt_to_llm)


                # not working "Skipping module injection for FusedLlamaMLPForQuantizedModel as currently not supported with use_triton=False.""
                #llm_answer = await GPTQ_Wizard_Vicuna_13B(prompt_to_llm)

                # TypeError: object str can't be used in 'await' expression
                #llm_answer = await GPTQ_Mixtral_8x7B_Instruct(prompt_to_llm)

#             else:
#                 await emoji_message.delete()
#                 await message.answer("Error! No model selected\n" + str(current_user_model))
# #                    llm_answer = "Error! No model selected\n" + str(current_user_model)
#                 #await emoji_message.edit_text(llm_answer)
#                 return
            break
        except (ValueError, RuntimeError) as e:
            # Print error message
            if i < 6:
                await message.answer("Still thinking...\n" + str(e) + "\nRetry #"+str(i))
            else:
                await message.answer("Nothing came to my mind, sorry (\n" + str(e), reply_markup = get_chat_kb())
                return
            sleep(6)
    # Remove AI name from answer if any
    # if current_user_system_prompt[2] != "":
    #     llm_answer = str(llm_answer.split(f"{current_user_system_prompt[2]}:",1)[-1]).lstrip()
    #     debug_print("Splitting AI name from answer", current_user_system_prompt[2])
    # llm_answer = llm_answer.strip()
    # Save to DB
    await add_message(user_id = message.from_user.id, author = "user", content = message_to_llm)
    await add_message(user_id = message.from_user.id, author = "ai", content = llm_answer)
    await emoji_message.delete()
#    await message.edit_text("💡")
    #await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    # Illustrate if 'game' in Model.name
    if 'game' in current_user_system_prompt[4].lower():
        print("!!--- Gonna Illustrate ---!!")
        await illustrate(message, state, llm_answer)

##########################################################################################################################################################

##########################################################################################################################################################
# Illustrate the answer
async def illustrate(message: Message, state: FSMContext, llm_answer: str) -> None:
    max_new_tokens      = 128
    num_inference_steps = 60

    emoji_message       = await message.answer("🎨", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

    # Summarize llm_answer for picture description
    description_prompt  = "Summaryze what is on the picture. Picture: '"
    picture_description = await llm_answer_from_model(description_prompt + llm_answer + "' Very short summary:",
                                                ["TheBloke/Mistral-7B-Instruct-v0.2-AWQ"],
                                                max_new_tokens)
#    picture_description = await AWQ_Mistral_7B_Instruct_pipe(description_prompt + llm_answer + "' Very short summary:", max_new_tokens)

    picture_description_cut = str(picture_description.split("\n")[0]).strip()
    debug_print("Summarized picture description", picture_description_cut)

    # playground accepts only 77 tokens
    result_image_path   = await OpenDalleV1_1(prompt = picture_description_cut, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)
    await emoji_message.delete()
    await message.answer_photo(result_image, picture_description_cut[:980]+"\nOpenDalle V1.1")

    # Try different styles
    # result_image_path   = await OpenDalleV1_1(prompt = "drawing, " + picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    # result_image        = FSInputFile(result_image_path)
    # await message.answer_photo(result_image, "OD drawing")

    # result_image_path   = await OpenDalleV1_1(prompt = "fiction, " + picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    # result_image        = FSInputFile(result_image_path)
    # await message.answer_photo(result_image, "OD fiction")

#     result_image_path   = await animagine_xl_2_0(prompt = picture_description_cut2, file_path="data/generated_images", n_steps=80)
# #    result_image_path   = await stable_diffusion_xl_base_1_0(prompt = picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
#     result_image        = FSInputFile(result_image_path)
# #    await emoji_message.delete()
#     await message.answer_photo(result_image, "animagine_xl_2_0")

    result_image_path   = await playground_v2_1024px_aesthetic(prompt = picture_description_cut, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)
    await message.answer_photo(result_image, "Playground V2 aesthetic")

    # Try different styles
    # result_image_path   = await playground_v2_1024px_aesthetic(prompt = "drawing, " + picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    # result_image        = FSInputFile(result_image_path)
    # await message.answer_photo(result_image, "pg drawing")

    # result_image_path   = await playground_v2_1024px_aesthetic(prompt = "fiction, " + picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    # result_image        = FSInputFile(result_image_path)
    # await message.answer_photo(result_image, "pg fiction")

    await main_menu(message, state)
