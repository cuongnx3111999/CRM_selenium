# utils/logger.py
"""Logging configuration and utilities."""

import logging
import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.settings import Settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


class Logger:
    """Logger utility class for the test framework."""

    _loggers = {}
    _initialized = False

    @classmethod
    def _initialize_logging(cls) -> None:
        """Initialize logging configuration once."""
        if cls._initialized:
            return

        # Create logs directory if it doesn't exist
        log_file = Path(Settings.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Clear any existing handlers
        logging.getLogger().handlers.clear()

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str = "test_framework") -> logging.Logger:
        """Get or create a logger instance."""
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]

    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create a new logger instance."""
        cls._initialize_logging()

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Settings.LOG_LEVEL))

        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        logger.propagate = False

        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        simple_formatter = ColoredFormatter(
            fmt="%(asctime)s [%(levelname)8s] %(message)s",
            datefmt="%H:%M:%S"
        )

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

        # File handler with detailed format
        file_handler = logging.FileHandler(Settings.LOG_FILE, encoding="utf-8")
        file_handler.setLevel(getattr(logging, Settings.LOG_LEVEL))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Error file handler (only errors and above)
        error_log_file = Path(Settings.LOG_FILE).parent / "error.log"
        error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)

        return logger

    @classmethod
    def log_test_start(cls, test_name: str) -> None:
        """Log test start with separator."""
        logger = cls.get_logger()
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING TEST: {test_name}")
        logger.info("=" * 80)

    @classmethod
    def log_test_end(cls, test_name: str, status: str) -> None:
        """Log test end with status."""
        logger = cls.get_logger()
        status_emoji = "✅" if status.upper() == "PASSED" else "❌"
        logger.info(f"{status_emoji} TEST {status.upper()}: {test_name}")
        logger.info("=" * 80)

    @classmethod
    def log_step(cls, step: str) -> None:
        """Log test step."""
        logger = cls.get_logger()
        logger.info(f"📋 STEP: {step}")

    @classmethod
    def log_action(cls, action: str) -> None:
        """Log user action."""
        logger = cls.get_logger()
        logger.info(f"🎯 ACTION: {action}")

    @classmethod
    def log_verification(cls, verification: str, result: bool) -> None:
        """Log verification with result."""
        logger = cls.get_logger()
        result_emoji = "✅" if result else "❌"
        logger.info(f"{result_emoji} VERIFY: {verification}")

    @classmethod
    def log_error(cls, error: str, exception: Exception = None) -> None:
        """Log error with optional exception details."""
        logger = cls.get_logger()
        logger.error(f"💥 ERROR: {error}")
        if exception:
            logger.error(f"Exception details: {str(exception)}")

    @classmethod
    def log_warning(cls, warning: str) -> None:
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(f"⚠️  WARNING: {warning}")

    @classmethod
    def log_debug(cls, debug_info: str) -> None:
        """Log debug information."""
        logger = cls.get_logger()
        logger.debug(f"🔍 DEBUG: {debug_info}")

    @classmethod
    def log_data(cls, data_description: str, data: any) -> None:
        """Log test data."""
        logger = cls.get_logger()
        logger.info(f"📊 DATA: {data_description} = {data}")

    @classmethod
    def log_browser_action(cls, action: str, element: str = None) -> None:
        """Log browser actions."""
        logger = cls.get_logger()
        if element:
            logger.info(f"🌐 BROWSER: {action} on {element}")
        else:
            logger.info(f"🌐 BROWSER: {action}")

    @classmethod
    def log_api_call(cls, method: str, url: str, status_code: int = None) -> None:
        """Log API calls."""
        logger = cls.get_logger()
        if status_code:
            logger.info(f"🔗 API: {method} {url} -> {status_code}")
        else:
            logger.info(f"🔗 API: {method} {url}")

    @classmethod
    def create_test_session_log(cls) -> None:
        """Create a new log file for test session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_log = Path(Settings.LOGS_DIR) / f"test_session_{timestamp}.log"

        # Create session-specific logger
        session_logger = cls.get_logger("test_session")

        # Add session file handler
        session_handler = logging.FileHandler(session_log, encoding="utf-8")
        session_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)8s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        session_handler.setFormatter(formatter)
        session_logger.addHandler(session_handler)

        session_logger.info(f"Test session started at {datetime.now()}")
        session_logger.info(f"Browser: {Settings.BROWSER}")
        session_logger.info(f"Base URL: {Settings.BASE_URL}")
        session_logger.info(f"Environment: {Settings.TEST_ENV}")

    @classmethod
    def cleanup_old_logs(cls, days_to_keep: int = 7) -> None:
        """Clean up log files older than specified days."""
        logs_dir = Path(Settings.LOGS_DIR)
        if not logs_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cls.get_logger().info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    cls.get_logger().warning(f"Failed to delete log file {log_file}: {e}")


# Convenience functions for quick logging
def log_info(message: str) -> None:
    """Quick info logging."""
    Logger.get_logger().info(message)


def log_error(message: str, exception: Exception = None) -> None:
    """Quick error logging."""
    Logger.log_error(message, exception)


def log_warning(message: str) -> None:
    """Quick warning logging."""
    Logger.log_warning(message)


def log_debug(message: str) -> None:
    """Quick debug logging."""
    Logger.log_debug(message)


def log_step(step: str) -> None:
    """Quick step logging."""
    Logger.log_step(step)


def log_action(action: str) -> None:
    """Quick action logging."""
    Logger.log_action(action)
