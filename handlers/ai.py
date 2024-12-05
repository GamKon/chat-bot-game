from time import sleep
import asyncio
from aiogram import Router, html
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
# from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums.chat_action import ChatAction
# from aiogram.methods import SendChatAction
#from aiogram import Bot
from utility        import debug_print, pin_user_settings, num_tokens_from_string

from models.llm_awq_gptq     import llm_answer_from_model
from models.llm_gguf         import llm_answer_from_gguf
from models.openai_chatgpt   import gpt_3_5_turbo_1106
from models.playgroundai     import playground_v2_5_1024px_aesthetic
from models.OpenDalleV1_1    import OpenDalleV1_1, ProteusV0_2
from models.stable_diffusion import stable_diffusion_xl_base_1_0

from handlers.main_menu      import main_menu, command_start
from classes                 import UIStates
from db.queries              import *
from templating              import chat_template
from templating_rag          import chat_template_rag
from keyboards.keyboards     import get_chat_kb
from rag                     import *

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

    # Stop accepting messages while LLM is thinking
    data = await state.get_data()
    if "is_thinking" not in data:
        data = await state.update_data(is_thinking = False)

    current_user_model = await select_user_llm_model(message.from_user.id)
#    debug_print("current_user_model4", current_user_model[4])
    max_context_window = current_user_model[4]

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

    # Check if user input is None or Empty
    if message_to_llm == None:
        debug_print("User input is None, ignoring")
        return
    if len(message_to_llm) == 0:
        debug_print("User input is Empty, ignoring")
        return

    ###########################################################
    # Prepare prompt for LLM

    # Before using RAG. Just plain SELECT all messages form history
    # make messages list from DB in STRING format
    # Template whole string to send depending on format
###    prompt_to_llm = await chat_template(message_to_llm, message, format_to = current_user_model[2], use_names = current_user_model[3])

    ###########################################################
    # RAG: make messages list from Pinecone DB in STRING format
    # Template whole string to send depending on format

    # TODO find a way to count how many tokens in the string
    max_tokens_to_llm = int(max_context_window) - int(max_new_tokens)
    debug_print("max_tokens_to_llm", max_tokens_to_llm)
    num_tokens_to_llm = num_tokens_from_string(message_to_llm, "cl100k_base")
    debug_print("num_tokens in message_to_llm", num_tokens_to_llm)

    current_chat = await select_user_chat_id(user_id = message.from_user.id)
    namespace = str(message.from_user.id)+"_"+str(current_chat[0])

# TODO: remember optimal top_k for not to query all of them at every templating

    # How many vectors are stored in namespace
    try:
        top_k = get_num_vectors(namespace)
        total_vectors_in_db = top_k
        debug_print(f"Total vectors in namespace {namespace}", top_k)
        if top_k == 0: top_k = 1
    except Exception as e:
        debug_print("Error getting number of vectors", e)
        await message.reply("Error getting number of vectors (\n" + html.quote(str(e)), reply_markup = get_chat_kb())
        top_k = 1

    # Set how many last messages to add to the end of message_to_llm
    depth = 3

    # # Get how many vectors (top_k) to retrieve from Pinecone to fit context window
    # data = await state.get_data()
    # if "top_k" in data:
    #     stored_top_k = data["top_k"]
    #     debug_print("Stored top_k", stored_top_k)
    #     if stored_top_k < top_k and top_k > depth:
    #         top_k = stored_top_k + depth
    # debug_print("Optimal Top_k", top_k)

# TODO: Make only one requesd to DB. Reduce the list in memory
    try:
        prompt_to_llm, pop_count = await chat_template_rag(message_to_llm, namespace, message, format_to = current_user_model[2], use_names = current_user_model[3], max_tokens_to_llm = max_tokens_to_llm, top_k = top_k, depth = depth)
        debug_print("prompt_to_llm", prompt_to_llm)
    # # #    debug_print("Prompt to LLM FIRST TRY", prompt_to_llm)
    # #     while prompt_to_llm == "" and top_k > 1:
    # #         top_k -= 1
    # #         debug_print("Top_k reduced to", top_k)
    # #         prompt_to_llm = await chat_template_rag(message_to_llm, namespace, message, format_to = current_user_model[2], use_names = current_user_model[3], max_prompt_to_llm = max_prompt_to_llm, top_k = top_k, depth = depth)
    except Exception as e:
        debug_print("Error templating message from RAG", e)
        await message.reply("Error templating message from RAG (\n" + html.quote(str(e)), reply_markup = get_chat_kb())
        return

    # # Save top_k for next time to message.data
    # data = await state.update_data(top_k = top_k)
    # debug_print("Save top_k", top_k)

    ###########################################################
    # Stop accepting messages while LLM is thinking
    # Set is_thinking to True
    data = await state.update_data(is_thinking = True)

    # Emoji "Thinking..."
    emoji_message = await message.answer("🤔", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

    ###########################################################
    # Send prompt to LLM
    # 2 tries to handle recoverable model Errors
    loop = asyncio.get_event_loop()

    for i in range(1, 3):
        try:
            llm_answer, num_tokens = await loop.run_in_executor(None,
                                                    get_llm_answer,
                                                    prompt_to_llm,
                                                    current_user_model,
                                                    max_new_tokens,
                                                    max_context_window
                                                    )
            break
        except (RuntimeError, ValueError) as e:
            # Print error message
            if i < 2:
                await message.answer("Still thinking...\n" + html.quote(str(e)) + "\nRetry #" + str(i))
            else:
                await emoji_message.delete()
                await message.answer("Nothing came to my mind, sorry (\n" + html.quote(str(e)), reply_markup = get_chat_kb())
                ###########################################################
                # Start accepting messages again
                # Set is_thinking to False
                data = await state.update_data(is_thinking = False)
                return
#   sleep doesn't work here ???
            await asyncio.sleep(3)
        except (TypeError, NameError, Exception) as e:
            await emoji_message.delete()
            await message.answer("Nothing came to my mind, sorry ((\n" + html.quote(str(e)), reply_markup = get_chat_kb())
            ###########################################################
            # Start accepting messages again
            # Set is_thinking to False
            data = await state.update_data(is_thinking = False)
            return

    # No need any more. TEST it!
    # Remove AI name from answer if any
    if current_user_system_prompt[2] != "":
        llm_answer = str(llm_answer.split(f"{current_user_system_prompt[2]}:",1)[-1]).lstrip()
        debug_print("Splitting AI name from answer", current_user_system_prompt[2])
    llm_answer = llm_answer.strip()

    '''
    # No need to summarize as working at RAG
        # Summarize llm_answer if it's longer than 256 characters
        if len(llm_answer) > 256:
            summ_llm_answer = await summarize_text( text    = llm_answer,
                                                    state   = state,
                                                    model   = "mistral-7b-instruct-v0.2.Q3_K_S.gguf",
                                                    max_new_tokens = 170)
            debug_print("Answer summarized. Characters before: ", len(llm_answer))
            debug_print("Characters after summarization: ", len(summ_llm_answer))
            debug_print("Original answer: ", llm_answer)
            debug_print("Summarized answer: ", summ_llm_answer)
            await message.answer(html.quote("Summarized: " + summ_llm_answer + "\n" + str(len(llm_answer))+ " -> " + str(len(summ_llm_answer))))
        else:
            debug_print("Answer is short, no need to summarize. Length: ", len(llm_answer))
        #     summ_llm_answer = llm_answer
    '''

    # cut the answer by paragraphs, "/n/n" symbols
    debug_print("Answer before cutting", llm_answer)
    paragraphs = llm_answer.split("\n\n")
    try:
        result = "".join(paragraphs[:3])
    except IndexError:
        try:
            result = "".join(paragraphs[:2])
        except IndexError:
            result = paragraphs[:1] if paragraphs else ""
    llm_answer = result
    debug_print("Answer after cutting", llm_answer)

    # No summarization for RAG
    summ_llm_answer = llm_answer

    ###########################################################
    # Save to PostgreSQL DB and get messages IDs
    vector_id_user  = await add_message(user_id = message.from_user.id, author = "user", content = message_to_llm, summ_content = "")
    vector_id_ai    = await add_message(user_id = message.from_user.id, author = "ai", content = llm_answer, summ_content = summ_llm_answer)


    ###########################################################
    # Save to Pinecone Vector DB
    # # To store user and ai messages separately
    # store_vector_chat_message([message_to_llm, llm_answer], [vector_id_user, vector_id_ai] ,namespace)

    # To store only user+ai messages in one record
    store_vector_chat_message([message_to_llm + "\n\n" + llm_answer], [vector_id_ai] ,namespace)

#    debug_print("RAG retrieved", get_relevant_chat_history(message_to_llm, namespace,top_k=top_k))

    await emoji_message.delete()
#    await message.edit_text("💡")
    #await message.answer(html.quote(llm_answer), reply_markup = get_chat_kb())
    if len(llm_answer) > 4096:
        llm_answer = llm_answer[:4000] + "...truncated..."
    try:
        await message.answer(html.quote(llm_answer + "\n\n" + "Input, output total tokens:\n" +str(num_tokens) + "\nRAG vectors fetched: " + str(top_k - pop_count) + " out of " + str(total_vectors_in_db)), reply_markup = get_chat_kb())
    except Exception as e:
        await message.answer("Error! Can't send message\n" + html.quote(str(e)), reply_markup = get_chat_kb())

    ###########################################################
    # Illustrate if 'game' in model.name
    if 'game' in current_user_system_prompt[4].lower():
        #debug_print("Gonna Illustrate", summ_llm_answer)
        try:
            picture_description = await summarize_text( text    = llm_answer,
                                                state   = state,
                                                model   = "llama-3-instruct-8b-simpo-q4_k_m.gguf",
                                                max_new_tokens = 90,
                                                draw    = True)
            await illustrate(message, state, picture_description, current_user_system_prompt[4].lower())
        except Exception as e:
            await message.answer("Error! Can't illustrate\n" + html.quote(str(e)), reply_markup = get_chat_kb())

    ###########################################################
    # Start accepting messages again
    # Set is_thinking to False
    data = await state.update_data(is_thinking = False)


def get_llm_answer(prompt_to_llm, current_user_model, max_new_tokens, max_context_window: int = 4096):

    ###########################################
    # Chat-GPT 3.5
    if current_user_model[0] == "gpt-3.5-turbo-1106":
        llm_answer = gpt_3_5_turbo_1106(prompt_to_llm)
    ###########################################
    # GGUF model format
    elif ".gguf" in current_user_model[0]:
        llm_answer, num_tokens = llm_answer_from_gguf(
                                            prompt_to_llm,
                                            current_user_model,
                                            max_new_tokens,
                                            max_context_window
                                        )
    ###########################################
    # AWQ and GPTQ model formats
    elif ("AWQ" in current_user_model[0]) or ("GPTQ" in current_user_model[0]):
        num_tokens = [""]
        llm_answer = llm_answer_from_model(
                                prompt_to_llm,
                                current_user_model,
                                max_new_tokens
                            )
    return llm_answer, num_tokens



##########################################################################################################################################################
# Summarize text
async def summarize_text(text: str, state: FSMContext, model: str = "mistral-7b-instruct-v0.2.Q3_K_S.gguf", max_new_tokens: int = 1024, draw: bool = False) -> str:

    ###########################################################
    # Stop accepting messages while LLM is thinking
    # Set is_thinking to True
    data = await state.update_data(is_thinking = True)

    loop = asyncio.get_event_loop()
    if draw:
        string_to_summarize  = f"Summarize the following game scene into a short, vivid description of what to draw. The description should be no more than 77 tokens.\n Game Scene:\n\n{text}\n\nShort description for drawing:"
#        string_to_summarize  = f"Based on the following game scene description, generate a short description of what to draw:\n\n{text}\n\n50 words description for drawing:"
#        string_to_summarize  = "This is what happening: '" + text + "' Illustrate: "
                                # Focus on who, where then what is happening.
    else:
        string_to_summarize  = "Summarize this: '" + text + "'. Very short summary:"

#    debug_print("String to summarize", string_to_summarize)
    summarized_text, num_tokens = await loop.run_in_executor(None,
#                                                 llm_answer_from_model,
                                                    get_llm_answer,
                                                    string_to_summarize,
                                                    [model],
                                                    max_new_tokens
                                                )
#    debug_print("Summarized text", summarized_text)

    ###########################################################
    # Start accepting messages again
    # Set is_thinking to False
    data = await state.update_data(is_thinking = False)

    return summarized_text

##########################################################################################################################################################
# Illustrate the answer
async def illustrate(message: Message, state: FSMContext, picture_description: str, game_type: str) -> None:

    num_inference_steps = 50
    picture_description = game_type.replace("game", "") + " " + str(picture_description.strip())
    #.split("\n")[0]).strip()

    # if "Illustration" in picture_description:
    #     picture_description = picture_description.split("Illustration")[1].strip()
    #     debug_print("Splitted by 'Illustration:'", picture_description)

    # Show picture description
    #debug_print("Picture description", picture_description)
    await message.answer(picture_description, reply_markup = get_chat_kb())

    loop = asyncio.get_event_loop()

    # Create a dictionary to map function names to functions
    # function_map = {"OpenDalleV1_1": OpenDalleV1_1}
    function_map = {"playground_v2_5_1024px_aesthetic": playground_v2_5_1024px_aesthetic}
    #     "ProteusV0_2": ProteusV0_2,
    #     "OpenDalleV1_1": OpenDalleV1_1,
    #     "playground_v2_5_1024px_aesthetic": playground_v2_5_1024px_aesthetic
    # }
    #txt_to_img_models = ["ProteusV0_2", "OpenDalleV1_1", "playground_v2_5_1024px_aesthetic"]
    txt_to_img_models = ["playground_v2_5_1024px_aesthetic"]
    for model_name in txt_to_img_models:
        try:
            emoji_message = await message.answer("🎨", reply_markup = ReplyKeyboardRemove(remove_keyboard = True))

            model_func          = function_map.get(model_name)
            if model_func:
                result_image_path   = await loop.run_in_executor(None,
                                                        model_func,
                                                        picture_description,
                                                        "data/generated_images",
                                                        num_inference_steps,
                                                        )
                result_image        = FSInputFile(result_image_path)
        except Exception as e:
            await message.answer("Error:\n" + html.quote(str(e)), reply_markup = get_chat_kb())
            continue

        try:
            await emoji_message.delete()
            # await message.answer_photo(result_image, picture_description[:980])
            await message.answer_photo(result_image, model_name)
        except Exception as e:
            await message.answer(f"Error! Can't send image made by {model_name}\n'{picture_description}'\n{html.quote(str(e))}", reply_markup = get_chat_kb())
            continue

    await main_menu(message, state)

##########################################################################################################################################################
# All other messages
@router.message()
async def other_messages(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    debug_print("Current state", current_state)
    if current_state is None:
        await state.set_state(UIStates.chat)

#        await message.answer("Can you repeat, please?", reply_markup = get_chat_kb())
#    await pin_user_settings(message)

#    await pin_user_settings(message)
#    await main_menu(message, state)

#     # await state.set_state(UIStates.chat)
#     # return
        await send_to_llm(message, state)
