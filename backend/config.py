from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./pricehunter.db"
    secret_key: str = "pricehunter-secret-2026"
    scrape_api_key: str = "pricehunter-scrape-2026"
    email_sender: str = ""
    email_password: str = ""
    email_receiver: str = ""
    vite_api_url: str = "http://localhost:8000"


settings = Settings()
