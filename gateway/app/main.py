import asyncio
from aiogram import Bot, Dispatcher, types,Router
from aiogram.types import ChatMemberUpdated
from shared.app.config import settings
from shared.app.logger import configure_logging, get_logger
from shared.app.rabbitmq import RabbitMQPublisher

configure_logging(settings.log_level)
logger = get_logger(__name__)


async def main():
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    publisher = RabbitMQPublisher(settings.rabbitmq_url, settings.rabbitmq_exchange)
    await publisher.connect()
    logger.info("Gateway started")
    
    
    @dp.update.outer_middleware()
    async def handle_message(handler, event: types.TelegramObject, data: dict):
        if not isinstance(event, types.Update):
            return

        event_type = event.event_type
        specific_event = getattr(event, event_type)
        if hasattr(specific_event, "model_dump"):
            # ✅ Опускаем поля, которые не были явно заданы, и приводим к JSON‑типам
            event = specific_event.model_dump(exclude_unset=True, mode='json')
        else:
            return

        await publisher.publish(event, event_type)
        logger.info("Message published", chat_id=specific_event.chat.id if event_type == "message" else 0,event_type=event_type)
        
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=[
    "message",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "chosen_inline_result",
    "callback_query",
    "shipping_query",
    "pre_checkout_query",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
    "chat_boost",
    "removed_chat_boost"
])  # Пустой список = все типы
    finally:
        await publisher.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())