from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    SECRET_KEY: str = Field(
        ...,
        env="SECRET_KEY",
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(
        default=3600, env="ACCESS_TOKEN_EXPIRE_SECONDS"
    )
    POSTGRES_URL: PostgresDsn = Field(
        default="postgresql://user:password@db:5431/onboarding_app",
        env="POSTGRES_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
