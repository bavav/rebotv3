import json

import aio_pika
from tenacity import retry, stop_after_attempt, wait_exponential

class RabbitMQClient:
    def __init__(self, url: str):
        self.url = url
        self.connection: aio_pika.Connection | None = None
        self.channel: aio_pika.Channel | None = None

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        # Объявляем durable очередь
        self.queue = await self.channel.declare_queue(
            "incoming_messages", durable=True
        )

    async def publish(self, message: dict):
        if not self.connection or self.connection.is_closed:
            await self.connect()
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="incoming_messages",
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()