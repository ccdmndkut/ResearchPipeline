import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/research_db",
        env="DATABASE_URL"
    )
    REDIS_URL: Optional[str] = Field(
        default="redis://localhost:6379",
        env="REDIS_URL"
    )
    VECTOR_DB_URL: Optional[str] = Field(
        default="http://localhost:8000",
        env="VECTOR_DB_URL"
    )

    # Model Configuration
    ORCHESTRATOR_MODEL: str = Field(default="gpt-4", env="ORCHESTRATOR_MODEL")
    AGENT_MODEL: str = Field(default="gpt-4", env="AGENT_MODEL")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    MAX_TOKENS: int = Field(default=2000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Cache Configuration
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")

    # Research Configuration
    MAX_SEARCH_RESULTS: int = Field(default=20, env="MAX_SEARCH_RESULTS")
    MAX_AGENTS_PARALLEL: int = Field(default=3, env="MAX_AGENTS_PARALLEL")
    REQUEST_TIMEOUT: int = Field(default=300, env="REQUEST_TIMEOUT")

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"
    TEMP_DIR: Path = PROJECT_ROOT / "temp"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # External APIs
    ARXIV_API_URL: str = Field(
        default="http://export.arxiv.org/api/query",
        env="ARXIV_API_URL"
    )
    PUBMED_API_URL: str = Field(
        default="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
        env="PUBMED_API_URL"
    )
    SEMANTIC_SCHOLAR_API_URL: str = Field(
        default="https://api.semanticscholar.org/graph/v1/",
        env="SEMANTIC_SCHOLAR_API_URL"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()