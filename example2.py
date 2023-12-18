#This code creates a Telegram bot using the aiogram library. When the bot receives a /start command, it displays a main menu with two buttons: "Chat" and "System". Clicking on either button opens a submenu with three subcategories.
#The `@dp.callback_query_handlers` are used to handle the user's selection of a subcategory. The first handler checks if the user has selected a subcategory under the "Chat" category, and the second handler checks if the user has selected a subcategory under the "System" category. Depending on the user's selection, the corresponding message is displayed.

import os
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_chat = types.KeyboardButton('Chat')
    button_system = types.KeyboardButton('System')
    keyboard.add(button_chat, button_system)
    await message.answer("Welcome! Please choose a category.", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('chat'))
async def process_chat_category(call: types.CallbackQuery):
    if call.data == 'chat':
        keyboard = types.InlineKeyboardMarkup()
        button_subcat1 = types.InlineKeyboardButton('Subcategory 1', callback_data='chat_subcat1')
        button_subcat2 = types.InlineKeyboardButton('Subcategory 2', callback_data='chat_subcat2')
        button_subcat3 = types.InlineKeyboardButton('Subcategory 3', callback_data='chat_subcat3')
        keyboard.add(button_subcat1, button_subcat2, button_subcat3)
        await bot.edit_message_text("Please choose a subcategory.",
                                   chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('chat_subcat'))
async def process_chat_subcategory(call: types.CallbackQuery):
    if call.data == 'chat_subcat1':
        await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 1 selected.")
    elif call.data == 'chat_subcat2':
        await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 2 selected.")
    elif call.data == 'chat_subcat3':
        await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 3 selected.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('system'))
async def process_system_category(call: types.CallbackQuery):
    if call.data =='system':
        keyboard = types.InlineKeyboardMarkup()
        button_subcat1 = types.InlineKeyboardButton('Subcategory 1', callback_data='system_subcat1')
        button_subcat2 = types.InlineKeyboardButton('Subcategory 2', callback_data='system_subcat2')
        button_subcat3 = types.InlineKeyboardButton('Subcategory 3', callback_data='system_subcat3')
        keyboard.add(button_subcat1, button_subcat2, button_subcat3)
        await bot.edit_message_text("Please choose a subcategory.",
                                   chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('system_subcat'))
async def process_system_subcategory(call: types.CallbackQuery):
    if call.data =='system_subcat1':
        await bot.answer_callback_query
    @dp.callback_query_handler(lambda c: c.data and c.data.startswith('system_subcat'))
    async def process_system_subcategory(call: types.CallbackQuery):
        if call.data =='system_subcat1':
            await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 1 selected.")
        elif call.data =='system_subcat2':
            await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 2 selected.")
        elif call.data =='system_subcat3':
            await bot.answer_callback_query(callback_query_id=call.id, text="Subcategory 3 selected.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


