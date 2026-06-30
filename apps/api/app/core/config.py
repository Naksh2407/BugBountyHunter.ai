from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://autofix:autofix@localhost/autofix"
    GITHUB_TOKEN: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()