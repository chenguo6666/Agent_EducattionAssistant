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
    llm_api_key: str = ""
    llm_model: str = "Pro/Qwen/Qwen2.5-7B-Instruct"
    llm_base_url: str = "https://api.siliconflow.cn/v1"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_api_key: str = ""
    embedding_model: str = ""
    embedding_base_url: str = ""
    vector_store_provider: str = "sqlite"
    vector_store_url: str = ""
    vector_store_api_key: str = ""
    vector_store_collection: str = "education_agent_chunks"
    retrieval_top_k: int = 4
    retrieval_candidate_limit: int = 24
    retrieval_keyword_weight: float = 0.35
    retrieval_vector_weight: float = 0.65

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
