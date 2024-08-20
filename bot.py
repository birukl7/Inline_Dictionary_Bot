import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, InlineQueryHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import httpx
import asyncio
from spellchecker import SpellChecker
from collections import defaultdict

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
DICTIONARY_API_URL = os.getenv("DICTIONARY_API_URL")

# Simple in-memory cache with a maximum size
cache = defaultdict(lambda: None)

# Single instance of HTTP client
http_client = httpx.AsyncClient(timeout=1.5)

# Initialize the spell checker
spell = SpellChecker()

# Function to handle /start command
async def start(update: Update, context):
    await update.message.reply_text('Hello! I can provide word definitions. Send me a word to get started!')

# Function to handle /help command
async def help(update: Update, context):
    await update.message.reply_text('Contact @birukl_777 for any inqueries.')

# Function to fetch word definitions and pronunciation from the Free Dictionary API
async def fetch_definition(word):
    if cache[word]:
        return cache[word]

    url = f"{DICTIONARY_API_URL}{word}"
    try:
        response = await http_client.get(url)
        response.raise_for_status()
        data = response.json()

        definitions = [
            {
                "definition": definition["definition"],
                "part_of_speech": meaning.get("partOfSpeech", ""),
                "example": definition.get("example", ""),
                "audio": data[0]["phonetics"][0].get("audio", "")  # Fetch the pronunciation audio URL
            }
            for meaning in data[0]["meanings"]
            for definition in meaning["definitions"]
        ]
        cache[word] = definitions
        return definitions

    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

# Function to handle inline queries
async def inline_query(update: Update, context):
    query = update.inline_query.query.strip().lower()

    if not query:
        return

    # Spell check the input query
    corrected_query = spell.correction(query) if len(query) > 3 else query

    # Fetch the definitions for the corrected query
    definitions = await fetch_definition(corrected_query)

    if not definitions:
        results = [
            InlineQueryResultArticle(
                id="0",
                title="No definitions found!",
                input_message_content=InputTextMessageContent(
                    "Sorry, no definitions were found for this word.",
                    parse_mode="Markdown"
                ),
                description="Try searching for another word.",
            )
        ]
    else:
        results = [
            InlineQueryResultArticle(
                id=str(i),
                title=f"{corrected_query} ({definition['part_of_speech']})",
                input_message_content=InputTextMessageContent(
                    f"*{corrected_query.capitalize()}* (_{definition['part_of_speech']}_): \n{definition['definition']}",
                    parse_mode="Markdown"
                ),
                description=f"{definition['definition'][:50]}..."
            )
            for i, definition in enumerate(definitions)
        ]

        # If the query was corrected, add a message about the correction
        if query != corrected_query:
            results.insert(
                0,
                InlineQueryResultArticle(
                    id="correction",
                    title=f"Did you mean: {corrected_query}?",
                    input_message_content=InputTextMessageContent(
                        f"Showing results for *{corrected_query}* instead of *{query}*.",
                        parse_mode="Markdown"
                    ),
                    description=f"Corrected from {query} to {corrected_query}",
                )
            )

    await update.inline_query.answer(results, cache_time=1)

# Function to handle messages sent directly to the bot
async def handle_message(update: Update, context):
    message_text = update.message.text.strip().lower()
    if len(message_text.split()) > 1:
        await update.message.reply_text("Please enter a single word to get its definition.")
        return
    
    # Spell check the message text
    corrected_query = spell.correction(message_text) if len(message_text) > 2 else message_text

    # Fetch the definitions and pronunciation for the corrected query
    definitions = await fetch_definition(corrected_query)

    if not definitions:
        await update.message.reply_text("Sorry, no definitions were found for this word.")
    else:
        # Create a message with all definitions
        message_parts = []
        for i, definition in enumerate(definitions):
            # Create a button for pronunciation
            keyboard = []
            if definition["audio"]:
                keyboard = [[InlineKeyboardButton("🔊 Pronunciation", callback_data=f"pronounce_{corrected_query}_{i}")]]
            
            # Format the part with bullet points for subsequent definitions
            if i == 0:
                part = f"*{corrected_query.capitalize()}* (_{definition['part_of_speech']}_): \n{definition['definition']}"
            else:
                part = f"• {definition['definition']}"

            message_parts.append(part)
        
        # Join all parts into a single message
        full_message = "\n".join(message_parts)
        await update.message.reply_text(
            full_message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )


# Function to handle pronunciation button click
async def pronounce(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Extract word and definition index from callback data
    _, word, index = query.data.split('_')
    index = int(index)  # Ensure index is an integer
    definitions = await fetch_definition(word)

    if index < len(definitions):
        audio_url = definitions[index].get("audio", "")
        if audio_url:
            # Send the audio directly to the user using their user ID
            await context.bot.send_audio(chat_id=query.from_user.id, audio=audio_url)
        else:
            await query.message.reply_text("Sorry, no pronunciation audio available.")
    else:
        await query.message.reply_text("Invalid pronunciation request.")

# Error handler
async def error(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")

# Run the bot
if __name__ == '__main__':
    print("Starting bot...")
    
    # Create the application and pass in the bot token
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",help))

    # Add message handler for direct messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add inline query handler
    application.add_handler(InlineQueryHandler(inline_query))

    # Add callback query handler for pronunciation
    application.add_handler(CallbackQueryHandler(pronounce, pattern=r'^pronounce_'))

    # Errors
    application.add_error_handler(error)

    print('Polling...')
    application.run_polling()

    # Ensure http_client is closed properly on exit
    asyncio.run(http_client.aclose())
