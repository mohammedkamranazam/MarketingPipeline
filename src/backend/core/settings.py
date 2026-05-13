from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Marketing Pipeline API", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql+psycopg://mp_user:mp_password@localhost:5432/marketing_pipeline",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    object_storage_endpoint: str = Field(
        default="http://localhost:8333",
        alias="OBJECT_STORAGE_ENDPOINT",
    )
    object_storage_bucket: str = Field(
        default="marketing-pipeline-local",
        alias="OBJECT_STORAGE_BUCKET",
    )
    object_storage_region: str = Field(default="local", alias="OBJECT_STORAGE_REGION")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    default_local_model: str = Field(default="qwen2.5:7b", alias="DEFAULT_LOCAL_MODEL")

    enable_cloud_llm_fallback: bool = Field(default=False, alias="ENABLE_CLOUD_LLM_FALLBACK")
    enable_authenticated_crawling: bool = Field(
        default=False,
        alias="ENABLE_AUTHENTICATED_CRAWLING",
    )
    enable_captcha_solver: bool = Field(default=False, alias="ENABLE_CAPTCHA_SOLVER")
    enable_auto_export: bool = Field(default=False, alias="ENABLE_AUTO_EXPORT")

    @property
    def enable_docs(self) -> bool:
        return self.app_env != "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
