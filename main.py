import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, PicklePersistence, CallbackQueryHandler

from commands import start, button, help







##########################################################################################################################################################
# MAIN
def main():
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Create a persistence object
    bot_persistence = PicklePersistence(filepath='data/chat/chat_history')

    # Variables
    HELP_MESSAGE        = os.getenv('HELP_MESSAGE')
    TELEGRAM_BOT_TOKEN  = os.getenv('TELEGRAM_BOT_TOKEN')

    chat_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).persistence(persistence=bot_persistence).build()

    # Handlers
    chat_bot.add_handler(CommandHandler("start", start))
    chat_bot.add_handler(CallbackQueryHandler(button))
    chat_bot.add_handler(CommandHandler("help", help))

# Run the bot until the user presses Ctrl-C
    chat_bot.run_polling(allowed_updates=Update.ALL_TYPES)

##########################################################################################################################################################
if __name__ == '__main__':
    main()

##########################################################################################################################################################
