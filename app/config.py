from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    open_api_key: str
    llm_model: str = "gpt-4o-mini"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
