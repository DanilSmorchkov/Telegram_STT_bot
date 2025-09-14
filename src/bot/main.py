from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import aiohttp
import os
from loguru import logger

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/transcribe")
LANGUAGES = {
    "🇷🇺 Русский": "ru",
    "🇺🇸 English": "en",
    "🇫🇷 Français": "fr"
}
MODEL = "whisper-small"


class STTBot:
    def __init__(self, token: str):
        self._token = token
        self.application = Application.builder().token(self._token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("language", self.language))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text))

    @staticmethod
    def _get_language_keyboard():
        keyboard = [[lang] for lang in LANGUAGES.keys()]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        logger.info(f"User {user.id} started the bot.")

        await update.message.reply_text(
            "🎤 Привет! Я преобразую голосовые сообщения в текст.\n"
            "Выбери язык для распознавания:",
            reply_markup=self._get_language_keyboard()
        )

    async def language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Выбери язык для распознавания:",
            reply_markup=self._get_language_keyboard()
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user_id = update.message.from_user.id

        if text in LANGUAGES:
            language_code = LANGUAGES[text]
            context.user_data['language'] = language_code

            await update.message.reply_text(
                f"✅ Язык установлен: {text}\n"
                f"Теперь отправь голосовое сообщение для распознавания!",
                reply_markup=None
            )
            logger.info(f"User {user_id} set language to {language_code}")
        else:
            await update.message.reply_text(
                "Пожалуйста, выбери язык из предложенных вариантов:",
                reply_markup=self._get_language_keyboard()
            )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        voice = update.message.voice
        language = context.user_data.get('language', 'ru')  # Default to Russian if not set
        logger.info(f"User {user.id} sent a voice message. Language: {language}")

        await update.message.reply_text("🎤 Обрабатываю голосовое сообщение...")

        try:
            voice_file = await voice.get_file()
            audio_data = await voice_file.download_as_bytearray()

            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('file', audio_data, filename='voice.ogg', content_type='audio/ogg')

                async with session.post(
                        f"{API_URL}?language={language}&model_name={MODEL}",
                        data=form_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        text = result["transcription"]
                        await update.message.reply_text(f"📝 **Текст:**\n{text}")
                    else:
                        await update.message.reply_text("❌ Ошибка при обработке аудио")

        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке")

    def run(self):
        logger.info("Starting Telegram bot...")
        self.application.run_polling()


if __name__ == "__main__":
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")

    bot = STTBot(bot_token)
    bot.run()
