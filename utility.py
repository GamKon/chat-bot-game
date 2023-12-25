from aiogram.types import Message
from classes import bot
from db.queries import select_user_settings
from keyboards.keyboards import get_chat_kb
#from handlers.main_menu import main_menu

##########################################################################################################################################################
# Pin User settings
async def pin_user_settings(message: Message) -> None:
    user_settings = await select_user_settings(user_id = message.from_user.id)
    print(f"Your settings:\n{user_settings}")
    user_settings_message = await message.answer(f"Persona: {user_settings[0]}; \nmodel: {user_settings[1]}; \n\nAI system prompt:\n{user_settings[2]}")#, reply_markup = get_chat_kb())
    await bot.unpin_all_chat_messages(message.chat.id)
    await bot.pin_chat_message(message.chat.id, user_settings_message.message_id, disable_notification = True)
    # await main_menu(message, state = None)
##########################################################################################################################################################
