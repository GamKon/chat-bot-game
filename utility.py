from aiogram.types import Message
from aiogram import html
from classes import bot
from db.queries import select_user_settings
from aiogram.enums import ParseMode

##########################################################################################################################################################
# Pin User settings
async def pin_user_settings(message: Message, to_pin: bool = True) -> None:
    user_settings = await select_user_settings(user_id = message.from_user.id)
    debug_print("User settings", user_settings)
    try:
        user_settings_message = await message.answer(html.code("Persona:") +
                                                    f" <b>{user_settings[0]}</b>\n" +
                                                    html.code("Model:") +
                                                    f" <b>{user_settings[1]}</b>\n" +
                                                    html.code("Personality:") +
                                                    html.pre(f"{user_settings[2]}") +
                                                    f"\n" + html.code("Chat    #: ") +
                                                    f"<b>{user_settings[5]}</b>\n" +
                                                    html.code("Bot  name: ") +
                                                    f"<b>{user_settings[4]}</b>\n" +
                                                    html.code("Your name: ") +
                                                    f"<b>{user_settings[3]}</b>",
                                                    parse_mode=ParseMode.HTML)
        if to_pin:
            await bot.unpin_all_chat_messages(message.chat.id)
            await bot.pin_chat_message(message.chat.id, user_settings_message.message_id, disable_notification = True)
    except Exception as e:
        await message.answer("Something went wrong 👾\nPlease try again later")
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

##########################################################################################################################################################
# Debug print
def debug_print(header: str, content = "#No Value#") -> None:
        print("\n######################################################################")
        print(f"# {header}")
        print("######################################################################")
        print(content)
        print("######################################################################\n")
