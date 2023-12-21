from aiogram.types          import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_chat_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button( text="Chat menu" )
    kb.button( text="System settings" )
    kb.adjust(2)
    return kb.as_markup(resize_keyboard = True, input_field_placeholder = "What's next?")

def get_chat_options_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button( text = "Clear last dialogue" )
    kb.button( text = "Repeat question" )
    kb.button( text = "Clear chat" )
    kb.button( text = "Cancel" )
    kb.adjust(4)
    return kb.as_markup(resize_keyboard = True, onetime_keyboard = False, input_field_placeholder = "Choose option")

def get_system_options_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="AI personality")
    kb.button(text="AI Model")
    kb.button(text="Language")
    kb.button(text="Cancel")
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=False)

def get_system_chat_mode_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(1, 7):
        kb.button(text=str(i))
    kb.button(text="Cancel")
    kb.adjust(4,3)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=False)

def get_system_model_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(1, 3):
        kb.button(text=str(i))
    kb.button(text="Cancel")
#    kb.adjust(2,2,2)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=False)

def get_confirm_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ok")
    kb.button(text="Cancel")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder = "Please confirm")


##########################################################################################################################################################
# Classic way to build keyboard
    # keyboard = [[
    #     KeyboardButton(text = "Clear last QA"),
    #     KeyboardButton(text = "Repeat question"),
    #     KeyboardButton(text = "Start over"),
    #     KeyboardButton(text = "Cancel")
    # ]]
    # reply_markup = ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True, onetime_keyboard=True)
    # await message.answer("Chat menu", reply_markup=reply_markup)

# Inline moves with the text
    # builder = InlineKeyboardBuilder()
    # builder.add(InlineKeyboardButton(text="Clear last QA", callback_data="drop_last"))
    # builder.add(InlineKeyboardButton(text="Repeat question", callback_data="repeat_last"))
    # builder.add(InlineKeyboardButton(text="Start over", callback_data="reset"))
    # builder.add(InlineKeyboardButton(text="Cancel", callback_data="cancel"))
    # await message.answer("Chat menu", reply_markup=builder.as_markup(onetime_keyboard=True))
