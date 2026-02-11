"""Logging setup and utilities."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(
    config_path: str = "config/logging.yaml",
    default_level: int = logging.INFO,
    env_key: str = "LOG_LEVEL",
) -> None:
    """Setup logging configuration.

    Args:
        config_path: Path to logging configuration file
        default_level: Default logging level if config not found
        env_key: Environment variable for log level override
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Check for environment variable override
    level_name = os.getenv(env_key, None)
    if level_name:
        default_level = getattr(logging, level_name.upper(), default_level)

    # Load logging configuration from YAML
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # Fallback to basic configuration
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)


def log_function_call(func):
    """Decorator to log function calls with arguments.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function
    """

    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(
            f"Calling {func.__name__} with args={args} kwargs={kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise

    return wrapper


def log_exceptions(logger: Optional[logging.Logger] = None):
    """Decorator to log exceptions from functions.

    Args:
        logger: Logger to use (if None, uses function's module logger)

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in {func.__name__}: {type(e).__name__}: {e}"
                )
                raise

        return wrapper

    return decorator
