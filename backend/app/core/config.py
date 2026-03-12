from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Education Assistant AI Agent"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str = "sqlite:///./education_agent.db"
    jwt_secret_key: str = "change-this-secret-in-local-env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    uploads_dir: str = "./uploads"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
