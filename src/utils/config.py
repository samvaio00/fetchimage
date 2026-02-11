"""Configuration management using Pydantic and environment variables."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration from environment variables."""

    # Replit API
    replit_api_url: str = Field(..., alias="REPLIT_API_URL")
    replit_api_key: str = Field(..., alias="REPLIT_API_KEY")

    # Image Source APIs
    unsplash_access_key: Optional[str] = Field(None, alias="UNSPLASH_ACCESS_KEY")
    pexels_api_key: Optional[str] = Field(None, alias="PEXELS_API_KEY")
    pixabay_api_key: Optional[str] = Field(None, alias="PIXABAY_API_KEY")

    # Application Settings
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    environment: str = Field("production", alias="ENVIRONMENT")

    # Database
    database_path: str = Field("./data/state.db", alias="DATABASE_PATH")

    # Scheduling
    schedule_enabled: bool = Field(True, alias="SCHEDULE_ENABLED")
    schedule_interval_hours: int = Field(6, alias="SCHEDULE_INTERVAL_HOURS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class Config:
    """Main configuration class combining env vars and YAML config."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment-based settings
        self.env = AppConfig()

        # Load YAML configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self.yaml_config = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Config file not found: {config_path}")

    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.yaml_config.get("app", {}).get("name", "Image Fetcher Bot")

    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.yaml_config.get("app", {}).get("version", "1.0.0")

    @property
    def batch_size(self) -> int:
        """Get batch size for processing SKUs."""
        return self.yaml_config.get("app", {}).get("batch_size", 50)

    @property
    def scheduler_config(self) -> Dict:
        """Get scheduler configuration."""
        return self.yaml_config.get("scheduler", {})

    @property
    def image_search_config(self) -> Dict:
        """Get image search configuration."""
        return self.yaml_config.get("image_search", {})

    @property
    def keywords_config(self) -> Dict:
        """Get keywords extraction configuration."""
        return self.yaml_config.get("keywords", {})

    @property
    def rate_limits(self) -> Dict:
        """Get rate limits configuration."""
        return self.yaml_config.get("rate_limits", {})

    @property
    def retry_config(self) -> Dict:
        """Get retry configuration."""
        return self.yaml_config.get("retry", {})

    @property
    def state_config(self) -> Dict:
        """Get state management configuration."""
        return self.yaml_config.get("state", {})

    @property
    def logging_config(self) -> Dict:
        """Get logging configuration."""
        return self.yaml_config.get("logging", {})

    @property
    def source_priorities(self) -> Dict[str, int]:
        """Get image source priorities."""
        return self.image_search_config.get("sources", {})

    @property
    def minimum_relevance_score(self) -> float:
        """Get minimum relevance score threshold."""
        return self.image_search_config.get("minimum_relevance_score", 0.6)

    @property
    def validation_config(self) -> Dict:
        """Get image validation configuration."""
        return self.image_search_config.get("validation", {})

    @property
    def allowed_formats(self) -> List[str]:
        """Get allowed image formats."""
        return self.validation_config.get("allowed_formats", ["JPEG", "PNG", "WebP"])

    def get_api_key(self, source: str) -> Optional[str]:
        """Get API key for a specific source.

        Args:
            source: Image source name (unsplash, pexels, pixabay)

        Returns:
            API key or None if not configured
        """
        source_mapping = {
            "unsplash": self.env.unsplash_access_key,
            "pexels": self.env.pexels_api_key,
            "pixabay": self.env.pixabay_api_key,
        }
        return source_mapping.get(source.lower())

    def is_source_enabled(self, source: str) -> bool:
        """Check if an image source is enabled.

        Args:
            source: Image source name

        Returns:
            True if source has API key configured
        """
        return self.get_api_key(source) is not None


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: str = "config/config.yaml") -> Config:
    """Get or create global configuration instance.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: str = "config/config.yaml") -> Config:
    """Reload configuration.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        New Config instance
    """
    global _config
    _config = Config(config_path)
    return _config
