from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Data Centar API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if all(
            [
                self.POSTGRES_SERVER,
                self.POSTGRES_USER,
                self.POSTGRES_PASSWORD,
                self.POSTGRES_DB,
            ]
        ):
            return PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        return "sqlite:///./datacentar.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
