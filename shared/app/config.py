from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Инфраструктура
    rabbitmq_url: str = "amqp://admin:admin123@rabbitmq:5672/"
    rabbitmq_exchange: str = "bot_events"   # имя fanout exchange
    log_level: str = "INFO"

    # Telegram
    telegram_bot_token: str

settings = Settings()