import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, InlineQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import logging

# Load environment variables from .env
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the bot token from the .env file
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Function to handle /start command
async def start(update: Update, context):
    await update.message.reply_text('Hello! I can provide word definitions. Use the inline mode to search for a word!')

# Function to handle inline queries
async def inline_query(update: Update, context):
    query = update.inline_query.query

    # Check if there's a query input
    if not query:
        return
    
    # Placeholder result for now (you'll replace this with dictionary API results later)
    results = [
        InlineQueryResultArticle(
            id="1",
            title="Sample Result",
            input_message_content=InputTextMessageContent("This is a sample result!")
        )
    ]

    await update.inline_query.answer(results)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
   print(f'update {update} caused error {context.error}')



if __name__ == '__main__':
    print("starting bot...")
    # Create the application and pass in the bot token
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))

    # Add inline query handler
    application.add_handler(InlineQueryHandler(inline_query))

    #Errors
    application.add_error_handler(error)

    print('Polling....')
    application.run_polling(poll_interval=5)