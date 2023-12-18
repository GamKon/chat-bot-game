# Description: This file contains all the command handlers for the bot.
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, PicklePersistence, CallbackQueryHandler



##########################################################################################################################################################
# Command handlers
##########################################################################################################################################################

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Print initial prompt", callback_data="1"),
            InlineKeyboardButton("Set initial prompt", callback_data="2"),
        ],
        [InlineKeyboardButton("Show help", callback_data=await help(update, context))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome to the game!\nInitial prompt:\n{os.getenv('INITIAL_PROMPT')}",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


# async def send_to_llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_prompt = str(" ".join(context.args)).strip()
#     bot_answer_text = await bot_ask_mistral(user_prompt, context, update)
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_answer_text)


