from aiogram.types import Message
from classes import bot
from db.queries import select_user_settings, select_system_prompt
from aiogram.enums import ParseMode
#from keyboards.keyboards import get_chat_kb
#from handlers.main_menu import main_menu

##########################################################################################################################################################
# Pin User settings
async def pin_user_settings(message: Message) -> None:
    user_settings = await select_user_settings(user_id = message.from_user.id)
    print(f"Your settings:\n{user_settings}")
    user_settings_message = await message.answer(f"<i>Persona: </i><b>{user_settings[0]}</b>; \n<i>model: </i><b>{user_settings[1]}</b>;  \n\n<i>AI setup</i>:  \n{user_settings[2]}\n\n <i>AI name:     </i><b>{user_settings[4]}</b>\n<i>User name:  </i><b>{user_settings[3]}</b>", parse_mode=ParseMode.HTML)
    await bot.unpin_all_chat_messages(message.chat.id)
    await bot.pin_chat_message(message.chat.id, user_settings_message.message_id, disable_notification = True)
    # await main_menu(message, state = None)
##########################################################################################################################################################

##########################################################################################################################################################
# Emoji numbers
def get_emoji_number(number: int) -> str:
    emoji_numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return emoji_numbers[number]
##########################################################################################################################################################
def get_number_emoji(emoji: str) -> int:
    emoji_numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return emoji_numbers.index(emoji)
