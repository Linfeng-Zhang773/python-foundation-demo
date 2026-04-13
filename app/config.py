from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM API 配置
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"

    # HTTP请求配置
    request_timeout: float = 30.0
    max_retries: int = 3

    # 日志
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
