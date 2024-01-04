from aiogram import Router, F
from classes import UIStates
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Bot

from handlers.main_menu             import main_menu
from keyboards.keyboards            import *
from models.openai_whisper_large_v3 import openai_whisper_large_v3
from handlers.ai                    import send_to_llm
from utility                        import debug_print
from models.llm                     import llm_answer_from_model

from models.playgroundai            import playground_v2_1024px_aesthetic
from models.OpenDalleV1_1           import OpenDalleV1_1
from models.stable_diffusion        import stable_diffusion_xl_base_1_0, stable_diffusion_xl_base_refiner_1_0
#from models.Falconsai_text_summarization import text_summarization
from models.AWQ_Mistral_7B_Instruct_v0_2 import AWQ_Mistral_7B_Instruct_pipe

router = Router()

##########################################################################################################################################################
# Voice message
@router.message(F.voice)
async def download_voice(message: Message, state: FSMContext, bot: Bot):
    await bot.download(
        message.voice,
# TODO save file to memory only
        destination=f"data/voice/{message.voice.file_id}.ogg",
    )
    transcript = openai_whisper_large_v3(f"data/voice/{message.voice.file_id}.ogg")
    data = await state.update_data(transcript = transcript)
    # Save transcript to state
    await state.set_state( UIStates.confirm_send_transcript )
    await message.answer(f"<i>It looks like you said:</i>\n\n{transcript}\n\n<i>Send it to the chat?</i>", reply_markup = get_confirm_kb())
# Send transcript to LLM
@router.message(UIStates.confirm_send_transcript)
async def send_transcript(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == "✅ ok":
#        await message.answer("Sent", reply_markup = get_chat_kb())
        # Get transcript from state
        data = await state.get_data()
        message_to_llm = data["transcript"]
        print(f"message.text from transcript:\n{message_to_llm.strip()}")
        await send_to_llm(message, state, message_to_llm.strip())
    else:
        await message.answer("<i>Canceled</i>", reply_markup = get_chat_kb())
    await state.set_state( UIStates.chat )

##########################################################################################################################################################
# Generate Image with dataautogpt3/OpenDalleV1.1
@router.message(Command("image1"))
async def generate_image(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.generate_image1 )
    await message.answer("<i>What should I draw?</i>", reply_markup = cancel_kb(), parse_mode = "HTML")
@router.message(UIStates.generate_image1)
async def generate_image(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        await state.set_state( UIStates.chat )
        emoji_message = await message.answer("🎨", reply_markup = get_chat_kb())
        num_inference_steps = 60
        result_image_path = await OpenDalleV1_1(prompt = message.text, file_path="data/generated_images", n_steps=num_inference_steps)
        result_image = FSInputFile(result_image_path)
        await emoji_message.delete()
        await message.answer_photo(result_image, message.text[:70])
    await main_menu(message, state)

##########################################################################################################################################################
# Generate Image with Playground AI
@router.message(Command("image2"))
async def generate_image(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.generate_image2 )
    await message.answer("<i>What should I draw?</i>", reply_markup = cancel_kb(), parse_mode = "HTML")
@router.message(UIStates.generate_image2)
async def generate_image(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        await state.set_state( UIStates.chat )
        emoji_message = await message.answer("🎨", reply_markup = get_chat_kb())
        num_inference_steps = 60
        result_image_path = await playground_v2_1024px_aesthetic(prompt = message.text, file_path="data/generated_images", n_steps=num_inference_steps)
        result_image = FSInputFile(result_image_path)
        await emoji_message.delete()
        await message.answer_photo(result_image, message.text[:70])
    await main_menu(message, state)

##########################################################################################################################################################
# Generate Image with stabilityai/stable-diffusion-xl-base-1.0
@router.message(Command("image3"))
async def generate_image(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.generate_image3 )
    await message.answer("<i>What should I draw?</i>", reply_markup = cancel_kb(), parse_mode = "HTML")
@router.message(UIStates.generate_image3)
async def generate_image(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        await state.set_state( UIStates.chat )
        emoji_message = await message.answer("🎨", reply_markup = get_chat_kb())
        num_inference_steps = 60
        result_image_path = await stable_diffusion_xl_base_refiner_1_0(prompt = message.text, file_path="data/generated_images", n_steps=num_inference_steps)
        result_image = FSInputFile(result_image_path)
        await emoji_message.delete()
        await message.answer_photo(result_image, message.text[:70])
    await main_menu(message, state)

##########################################################################################################################################################
# Summarize text
@router.message(Command("summ"))
async def summarize_what(message: Message, state: FSMContext) -> None:
    await state.set_state( UIStates.summarize_text )
    await message.answer("<i>Gimme the text!</i>", reply_markup = cancel_kb(), parse_mode = "HTML")
@router.message(UIStates.summarize_text)
async def summarize_text(message: Message, state: FSMContext) -> None:
    if message.text.casefold() != "❌ cancel":
        emoji_message = await message.answer("✍️", reply_markup = get_chat_kb())
        message_to_llm = f"Summarize this: '{message.text}'. Summary:"
        print(f"message.text to summarize:\n{message_to_llm.strip()}")
        summary = await llm_answer_from_model(message_to_llm,
                                                ["TheBloke/Mistral-7B-Instruct-v0.2-AWQ"],
                                                max_new_tokens=128)
        #await send_to_llm(message, state, message_to_llm.strip())
        await emoji_message.delete()

        # await state.set_state( UIStates.chat )

        # summary = await text_summarization(prompt = message.text, max_length=550, min_length=10, do_sample=False)
        # await emoji_message.delete()
        await message.answer(summary)
    await main_menu(message, state)
