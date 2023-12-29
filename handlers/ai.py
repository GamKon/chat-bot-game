from time import sleep
from aiogram import Router, html
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums.chat_action import ChatAction
# from aiogram.methods import SendChatAction
#from aiogram import Bot

from models.GPTQ_Mistral_7B_Instruct_v0_2   import Mistral_7B_Instruct, Mistral_7B_Instruct_pipeline
from models.GPTQ_Mixtral_8x7B_Instruct_v0_1 import GPTQ_Mixtral_8x7B_Instruct, GPTQ_Mixtral_8x7B_Instruct_pipeline
from models.AWQ_dolphin_2_2_yi_34b          import AWQ_Dolphin_2_2_yi_34b_pipe
from models.AWQ_Mixtral_8x7B_Instruct_v0_1  import AWQ_Mixtral_8x7B_Instruct_pipe, AWQ_Mixtral_8x7B_Instruct
from models.AWQ_Mistral_7B_Instruct_v0_2    import AWQ_Mistral_7B_Instruct_pipe
from models.Mistral_7B_Instruct_v0_2        import Mistral_7B_Instruct_pipe
from models.GPTQ_Wizard_Vicuna_13B_Uncensored_SuperHOT_8K import GPTQ_Wizard_Vicuna_13B
from models.openai_chatgpt                  import gpt_3_5_turbo_1106
from models.playgroundai                    import playground_v2_1024px_aesthetic
from models.OpenDalleV1_1                   import OpenDalleV1_1
from models.stable_diffusion                import stable_diffusion_xl_base_1_0

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

    # #Try to stop accepting messages while LLM is thinking
    # data = await state.get_data()
    # print("-----------------!!!!!!!-BEGIN-!!!!-DATA\n")
    # print(data)
    # if "is_thinking" not in data:
    #     data = await state.update_data(is_thinking = False)
    # else:
    #     print("______is_thinking in data______\n")
    # if data["is_thinking"]:
    #     await message.reply("I'm still thinking at the first question, please be patient")
    #     return
    # # ???

    emoji_message = await message.answer("🤔", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
    current_user_model = await select_user_llm_model(message.from_user.id)

    # Set maximum answer length max_new_tokens
    try:
        data = await state.get_data()
        if "max_new_tokens" in data and data["max_new_tokens"] >= 20 and data["max_new_tokens"] <= 2048:
            max_new_tokens = data["max_new_tokens"]
            print(f"\n\nmax_new_tokens from context data= {max_new_tokens}\n\n")
        elif current_user_model[3] >= 20 and current_user_model[3] <= 2048:
            max_new_tokens = current_user_model[3]
            print(f"\n\nmax_new_tokens from Model table = {max_new_tokens}\n\n")
        else:
            max_new_tokens = 256
            print(f"\n\nmax_new_tokens from default = {max_new_tokens}\n\n")
    except:
        print("\n\nmax_new_tokens error, defaulting to 256\n\n")
        max_new_tokens = 256

    # Status "Typing..."
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        ###########################################################
        # Prepare prompt for LLM
        # make messages list from DB in STRING format
        # Set what names to template as "user" and "assistant" roles
        current_user_system_prompt = await select_system_prompt(message.from_user.id)
# roles = [current_user_system_prompt[1], current_user_system_prompt[2]]
        #roles = ["", ""]
        # template to model table

        current_state = await state.get_state()
        print(f"current_state!!!!!!!!!!!!{current_state}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if current_state == "UIStates:confirm_send_transcript":
            message_to_llm = message_to_llm
        else:
            message_to_llm = message.text
        print(f"message_to_llm!!!!!!!!!!!!{message_to_llm}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        prompt_to_llm = await chat_template(message_to_llm, message, format_to = current_user_model[2])#, roles = roles)

        ###########################################################
        # Send prompt to LLM
        # 5 tries to handle model Errors
        for i in range(1, 7):
            try:
                ###########################################
                # Mistral_7B_Instruct
                if current_user_model[0] == "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ":
                    # Try to stop accepting messages while LLM is thinking
                    # data = await state.update_data(is_thinking = True)
                    # print("-----------------!!!!!!!-!!!!!!BEFORE!!!!!DATA\n")
                    # print(data)

                    # AWQ quantized
                    llm_answer = await AWQ_Mistral_7B_Instruct_pipe(prompt_to_llm, max_new_tokens)

                    # Original
#                    llm_answer = await Mistral_7B_Instruct_pipe(prompt_to_llm, max_new_tokens)


                    #llm_answer = await Mistral_7B_Instruct_pipeline(prompt_to_llm)
                    #llm_answer = await Mistral_7B_Instruct(prompt_to_llm)

                    # data = await state.update_data(is_thinking = False)
                    # print("-----------------!!!!!!!-!!!!!!AFTER!!!!!DATA\n")
                    # print(data)
                ###########################################
                # Mixtral-8x7B-Instruct
                elif current_user_model[0] == "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ":
                    # GPTQ quantized
                    llm_answer = await GPTQ_Mixtral_8x7B_Instruct_pipeline(prompt_to_llm, max_new_tokens)
                ###########################################
                # Dolphin-2_2-yi-34b-AWQ
                elif current_user_model[0] == "TheBloke/dolphin-2_2-yi-34b-AWQ":
                    print("!!!current_user_model[2]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(current_user_model[2])

                    llm_answer = await AWQ_Dolphin_2_2_yi_34b_pipe(prompt_to_llm, max_new_tokens)
                    print("!!! llm_answer !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(f"--{llm_answer}--")

                    # Remove LLM role name from answer
                    if current_user_system_prompt[2] != "":
                        llm_answer = str(llm_answer.splitlines()[-1])
                                         #(f"{current_user_system_prompt[2]}:")[-1])

                    print("!!!current_user_model[2]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(current_user_system_prompt[2])
                    print("!!! llm_answer !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print(f"--{llm_answer}--")
                ###########################################
                # Chat-GPT 3.5
                elif current_user_model[0] == "gpt-3.5-turbo-1106":
                    llm_answer = await gpt_3_5_turbo_1106(prompt_to_llm)



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

                else:
                    await emoji_message.delete()
                    await message.answer("Error! No model selected\n" + str(current_user_model))
#                    llm_answer = "Error! No model selected\n" + str(current_user_model)
                    #await emoji_message.edit_text(llm_answer)
                    return
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
    if current_user_system_prompt[2] != "":
        llm_answer = str(llm_answer.split(f"{current_user_system_prompt[2]}:",1)[-1]).lstrip()
        print(f"\n!!! split {current_user_system_prompt[2]} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                                     #(f"{current_user_system_prompt[2]}:")[-1])

    # Save to DB
    await add_message(user_id = message.from_user.id, author = "user", content = message_to_llm)
    await add_message(user_id = message.from_user.id, author = "ai", content = llm_answer)
    await emoji_message.delete()
#    await message.edit_text("💡")
    #await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    print(f"current_user_system_prompt[4].lower()!!!!!!!!!!!!\n{current_user_system_prompt[4].lower()}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # Illustrate if 'game' in Model.name
    if 'game' in current_user_system_prompt[4].lower():
        print("!!--- Gonna Illustrate ---!!")
        await illustrate(message, state, llm_answer)

##########################################################################################################################################################

##########################################################################################################################################################
# Illustrate the answer
async def illustrate(message: Message, state: FSMContext, llm_answer: str) -> None:
    max_new_tokens      = 128
    num_inference_steps = 70
    emoji_message       = await message.answer("🎨", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))
    #description_prompt  =
    # "Short 77 tokens summarise what is on this picture. Start with {who is on the picture} continue with {what are they doing} and finish with {where it is}. Mark beginning and end with two asterisks. The picture description start: **{"
    description_prompt  = "Give me very short 65 words summary who is on this picture and what is happening: '"
    picture_description = await AWQ_Mistral_7B_Instruct_pipe(description_prompt + llm_answer + "' Summary:", max_new_tokens)



    picture_description_cut = str(picture_description.split("Summary:")[-1])
    print(f"\npicture_description_cut!!!!!!!!!!!!\n{picture_description_cut}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    picture_description_cut2 = str(picture_description_cut.split("\n")[0]).strip()
    print(f"\npicture_description_cut2!!!!!!!!!!!!\n{picture_description_cut2}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")



#    picture_description_split = picture_description.split("**")
#    print(f"\npicture_description_split!!!!!!!!!!!!\n{picture_description_split}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
#    while len(picture_description_split[-1]) < 10:
#        picture_description_split.pop(-1)
#    picture_description_split_2 = picture_description_split[-1]
#    print(f"\npicture_description_split_2!!!!!!!!!!!!\n{picture_description_split_2}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    # playground accepts only 77 tokens

    result_image_path   = await OpenDalleV1_1(prompt = picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)
    await emoji_message.delete()
    await message.answer_photo(result_image, "OpenDalleV1_1\n" + picture_description_cut2[:980])

    result_image_path   = await playground_v2_1024px_aesthetic(prompt =  picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)
#    await emoji_message.delete()
    await message.answer_photo(result_image, "playground_v2_1024px_aesthetic")

    result_image_path   = await stable_diffusion_xl_base_1_0(prompt = "hentai " + picture_description_cut2, file_path="data/generated_images", n_steps=num_inference_steps)
    result_image        = FSInputFile(result_image_path)
#    await emoji_message.delete()
    await message.answer_photo(result_image, "stable_diffusion_xl_base_1_0")

    await main_menu(message, state)
