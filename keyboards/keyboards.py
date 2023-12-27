from aiogram.types          import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utility                import get_emoji_number

def get_chat_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button( text="📝 Chat menu" )
    kb.button( text="🔧 System settings" )
    kb.adjust(2)
    return kb.as_markup(resize_keyboard = True, input_field_placeholder = "What's next?")

def get_chat_options_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button( text = "🗒️ Show history" )
    kb.button( text = "✏️ Clear last dialogue" )
    # kb.button( text = "Repeat question" )
    kb.button( text = "🚧 Clear chat" )
    kb.button( text = "❌ Cancel" )
    kb.adjust(4)
    return kb.as_markup(resize_keyboard = True, onetime_keyboard = False, input_field_placeholder = "Choose option")

def get_system_options_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="💃 AI personality")
    kb.button(text="🤖 AI Model")
    # kb.button(text="Format")
    # kb.button(text="Language")
    kb.button(text="❌ Cancel")
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=False)

def get_system_chat_mode_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(1, 10):
        kb.button(text=get_emoji_number(i))
    # kb.button(text="Show")
    kb.button(text="✍️ Edit current")
    kb.button(text="❌ Cancel")
    kb.adjust(4, 4, 3)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=True)

def get_system_model_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(1, 4):
        kb.button(text=get_emoji_number(i))
    kb.button(text="❌ Cancel")
#    kb.adjust(2,2,2)
    return kb.as_markup(resize_keyboard=True, onetime_keyboard=False)

def get_confirm_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="✅ Ok")
    kb.button(text="❌ Cancel")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder = "Please confirm")

def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ Cancel")
    return kb.as_markup(resize_keyboard=True, input_field_placeholder = "Please confirm")

##########################################################################################################################################################
##########################################################################################################################################################
# InlineKeyboards
def edit_system_prompt_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Edit prompt", callback_data="edit_system_prompt"))
    kb.add(InlineKeyboardButton(text="AI name", callback_data="edit_ai_name"))
    kb.add(InlineKeyboardButton(text="User name", callback_data="edit_user_name"))
    kb.add(InlineKeyboardButton(text="Persona name", callback_data="edit_save_slot"))
    kb.add(InlineKeyboardButton(text="Answer length", callback_data="max_answer_lenght"))
    kb.adjust(3, 2)
    return kb.as_markup()
