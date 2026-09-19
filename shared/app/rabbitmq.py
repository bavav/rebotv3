import json
import aio_pika
from tenacity import retry, stop_after_attempt, wait_exponential
from aiogram.types import TelegramObject

class RabbitMQPublisher:
    """Публикует сообщения в fanout exchange (используется в Gateway)."""

    def __init__(self, url: str, exchange_name: str):
        self.url = url
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        # Объявляем долговечный fanout exchange
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )

    async def publish(self, event: TelegramObject,event_type: str):
        if not self.connection or self.connection.is_closed:
            await self.connect()
        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(event).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "event_type": event_type  # <--- Вот ваш payload / метаданные!
                },
            ),
            routing_key="",  # для fanout routing_key игнорируется
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


class RabbitMQConsumer:
    """Подписывается на очередь с auto_delete, привязанную к fanout exchange."""

    def __init__(self, url: str, exchange_name: str, queue_name: str):
        self.url = url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        # Чтобы сообщения не раздавались без ack
        await self.channel.set_qos(prefetch_count=1)

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )

        # Объявляем очередь с auto_delete=True.
        # Все реплики этого сервиса объявляют одну и ту же очередь с одинаковыми параметрами.
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            auto_delete=True,
        )

        # Привязываем очередь к exchange
        await self.queue.bind(self.exchange)

    async def consume(self, callback):
        await self.queue.consume(callback)

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()