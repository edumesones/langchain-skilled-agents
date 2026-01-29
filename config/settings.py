"""Application settings using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # LLM Providers
    # ==========================================================================
    openrouter_api_key: str = Field(default="", description="OpenRouter API Key")
    huggingface_token: str = Field(
        default="",
        description="HuggingFace Token (for Novita via router.huggingface.co)",
    )

    # ==========================================================================
    # Default Model Settings
    # ==========================================================================
    default_llm_provider: Literal["openrouter", "huggingface_novita"] = Field(
        default="openrouter",
        description="Default LLM provider",
    )
    default_llm_model: str = Field(
        default="google/gemini-2.0-flash-exp:free",
        description="Default LLM model",
    )
    default_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Default temperature",
    )
    default_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=128000,
        description="Default max tokens",
    )

    # ==========================================================================
    # Application Settings
    # ==========================================================================
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(default=True, description="Debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level",
    )

    # ==========================================================================
    # Data Settings
    # ==========================================================================
    data_output_path: Path = Field(
        default=Path("data/synthetic/output"),
        description="Path to synthetic data output",
    )
    synthetic_customers: int = Field(default=1000, description="Number of customers")
    synthetic_transactions: int = Field(default=100000, description="Number of transactions")
    synthetic_alerts: int = Field(default=200, description="Number of alerts")

    # ==========================================================================
    # UI Settings
    # ==========================================================================
    gradio_server_name: str = Field(default="0.0.0.0", description="Gradio server name")
    gradio_server_port: int = Field(default=7860, description="Gradio server port")
    gradio_share: bool = Field(default=False, description="Enable Gradio sharing")

    # ==========================================================================
    # Security
    # ==========================================================================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for sessions",
    )
    allowed_origins: str = Field(
        default="http://localhost:7860,http://127.0.0.1:7860",
        description="Allowed CORS origins",
    )

    # ==========================================================================
    # Computed Properties
    # ==========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent

    @property
    def skills_path(self) -> Path:
        """Get skills directory path."""
        return self.project_root / "skills"

    @property
    def data_path(self) -> Path:
        """Get data directory path."""
        return self.project_root / "data"

    @property
    def data_dir(self) -> Path:
        """Alias for data_path (used by tools)."""
        return self.data_path


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
