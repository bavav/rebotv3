import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from shared.app.config import settings
from shared.app.logger import configure_logging, get_logger
from shared.app.rabbitmq import RabbitMQClient

configure_logging(settings.log_level)
logger = get_logger(__name__)

async def main():
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    rabbit = RabbitMQClient(settings.rabbitmq_url)
    await rabbit.connect()
    logger.info("Gateway started")

    @dp.message()
    async def handle_message(message: types.Message):
        # Публикуем сообщение в очередь
        await rabbit.publish({
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "text": message.text or "",
            "message_id": message.message_id,
            "date": message.date.isoformat(),
        })
        logger.info("Message published", chat_id=message.chat.id)

    try:
        await dp.start_polling(bot)
    finally:
        await rabbit.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())