
# Replace 'YOUR_API_TOKEN' with your actual API token
bot_token = '6563361196:AAG7Oi8aUhKs4Ox2AVZM-ZVtjducNNmNsZM'

import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from libgen_api import LibgenSearch

def get_book(keyword):
    s = LibgenSearch()
    title_filters = {"Language": "English"}
    results = s.search_title_filtered(keyword, title_filters, exact_match=False)
    item_to_download = results[0]
    download_links = s.resolve_download_links(item_to_download)
    return([item_to_download,download_links.get('GET')])


def get_all_books(keyword):
    s = LibgenSearch()
    title_filters = {"Language": "English"}
    results = s.search_title_filtered(keyword, title_filters, exact_match=False)
    res = []
    for item in results :
        item_to_download = item
        download_links = s.resolve_download_links(item_to_download)
        res.append([item_to_download,download_links.get('GET')])
    return(res)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text("I can download books ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("/download ")
    await update.message.reply_text("/downloadall ")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text("Use /help command ")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download first book in search result"""
    chat_id = update.message.chat_id
    msg = update.message.text
    data = msg.split(' ',1)[1]
    res = get_book(data)
    print(res)
    await update.message.reply_text(f" ID :- { res[0]['ID'] }")
    await update.message.reply_text(f" Author :- { res[0]['Author'] }")
    await update.message.reply_text(f" Title:- { res[0]['Title'] }")
    await update.message.reply_text(f" Language:- { res[0]['Language'] }")
    await update.message.reply_text(f" Extension:- { res[0]['Extension'] }")
    await update.message.reply_text(f" Size:- { res[0]['Size'] }")
    await update.message.reply_text(f" Link:- { res[1] }")

    context.bot.send_document(chat_id,InputFile(open(res[1]),'rb') )


async def download_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    data = msg.split(' ',1)[1]
    res = get_all_books(data)
    print(res)
    for item in res :
        await update.message.reply_text(f" ID :- { item[0]['ID'] }")
        await update.message.reply_text(f" Author :- { item[0]['Author'] }")
        await update.message.reply_text(f" Title:- { item[0]['Title'] }")
        await update.message.reply_text(f" Language:- { item[0]['Language'] }")
        await update.message.reply_text(f" Extension:- { item[0]['Extension'] }")
        await update.message.reply_text(f" Size:- { item[0]['Size'] }")
        await update.message.reply_text(f" Link:- { item[1] }")
        await update.message.reply_text(f"-----------------------------------")



def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("download", download))
    application.add_handler(CommandHandler("downloadall", download_all))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
