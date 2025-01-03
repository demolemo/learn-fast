import logging

from summarize import summarize_text_pipeline
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am a Bot that will help you learn faster. Send me a lecture file and I will create a summary and quiz you on it on it.')
    return None


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please send me a lecture file and I will create a summary and quiz you on it.')
    return None


async def summarize_lecture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('we are here')
    if update.message.audio:
        file_id = update.message.audio.file_id
        file_blob = await context.bot.get_file(file_id)
        custom_path = 'temp_audio_file.mp3'
    elif update.message.video:
        file_id = update.message.video.file_id
        file_blob = await context.bot.get_file(file_id)
        custom_path = 'temp_video_file.mp4'
        # TODO: extract audio from video
    else:
        await update.message.reply_text('Please send me a lecture file and I will create a summary and quiz you on it.')
        return None
    
    await update.message.reply_text('Your file is being processed. This may take a few minutes.')
    logger.info(f'Downloading file from Telegram: {file_id}')
    await file_blob.download_to_drive(custom_path=custom_path)
    summarize_text_pipeline(custom_path)
    os.remove(custom_path)
    return None



def main() -> None:
    telegram_token = '7791275125:AAHLefvzf8xqMg9Wh5Tw5ZaJKmjB7Yyl_Gg'
    application = Application.builder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(MessageHandler(filters.AUDIO, summarize_lecture))
    application.add_handler(MessageHandler(filters.VIDEO, summarize_lecture))
    application.add_handler(MessageHandler(filters.TEXT, summarize_lecture))

    application.run_polling()

if __name__ == "__main__":
    main()