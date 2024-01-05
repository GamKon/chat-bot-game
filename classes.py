from os import getenv
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from aiogram.enums import ParseMode

TOKEN = getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

##########################################################################################################################################################
# Classes
class UIStates(StatesGroup):
    chat         = State()
    menu         = State()
    menu_confirm = State()
    sys          = State()
    sys_mode     = State()
    sys_ai_model = State()
    db_error     = State()
    waiting_ai_answer            = State()
    edit_system_prompt           = State()
    edit_system_prompt_confirm   = State()
    confirm_send_transcript      = State()
    edit_system_prompt_prompt    = State()
    edit_system_prompt_username  = State()
    edit_system_prompt_ai_name   = State()
    edit_system_prompt_save_name = State()
    edit_max_answer_length       = State()
    generate_image1              = State()
    generate_image2              = State()
    generate_image3              = State()
    summarize_text               = State()
    chat_user_chat               = State()
