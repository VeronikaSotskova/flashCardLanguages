from pydantic_settings import BaseSettings, SettingsConfigDict

MEDIA = 'media/'


class Settings(BaseSettings):
    # db settings
    DB_USER: str
    DB_HOST: str
    DB_PORT: int
    DB_PASSWORD: str
    DB_NAME: str

    # services creds
    GIPHY_KEY: str
    TELEGRAM_KEY: str
    UNSPLASH_ACCESS_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file="../../.env")


settings = Settings()
