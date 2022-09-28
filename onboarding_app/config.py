from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(
        ...,
        env="SECRET_KEY",
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(
        default=3600, env="ACCESS_TOKEN_EXPIRE_SECONDS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
