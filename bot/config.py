from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    BOT_TOKEN: str
    SUPER_ADMIN_IDS: str = ""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Bazada maxfiy ma'lumotlarni (masalan har bir do'konning Billz API
    # kaliti) SHIFRLAB saqlash uchun asosiy kalit (bot/utils/crypto.py).
    # Yaratish: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = ""

    # Billz.io (POS/ombor tizimi) bilan mahsulotlarni sinxronlash uchun.
    # Kalit bu yerda emas — har bir do'kon o'zining kalitiga ega (bazada,
    # MarketModel.billz_secret_key), chunki Billz'da har bir do'kon
    # alohida akkaunt.
    BILLZ_SYNC_ENABLED: bool = False
    BILLZ_SYNC_INTERVAL_MINUTES: int = 10
    # Billz'dan tortilgan rasmlarni Telegram file_id'ga aylantirish uchun
    # yuboriladigan chat (masalan alohida yopiq kanal/guruh ID'si). Bo'sh
    # qoldirilsa, birinchi SUPER_ADMIN_IDS ishlatiladi.
    BILLZ_IMAGE_STORAGE_CHAT_ID: int | None = None

    @property
    def super_admin_ids(self) -> list[int]:
        return [int(x) for x in self.SUPER_ADMIN_IDS.split(",") if x.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
