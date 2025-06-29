# config/settings.py
"""Global settings and configuration management."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables

load_dotenv()


class Settings:
    """Global settings class for the test framework."""

    # === ĐƯỜNG DẪN THỦ MỤC ===
    ROOT_DIR = Path(__file__).parent.parent  # Thư mục gốc của project
    DATA_DIR = ROOT_DIR / "data"  # Thư mục chứa test data (Excel, JSON)
    REPORTS_DIR = ROOT_DIR / "reports"  # Thư mục chứa báo cáo HTML
    LOGS_DIR = ROOT_DIR / "logs"  # Thư mục chứa log files
    screenshotS_DIR = REPORTS_DIR / "screenshots"  # Thư mục chứa ảnh chụp màn hình

    # === CẤU HÌNH BROWSER ===
    BROWSER: str = os.getenv("BROWSER", "chrome")
    HEADLESS: bool = os.getenv("HEADLESS") == "True"
    # HEADLESS: bool = False
    WINDOW_SIZE: str = os.getenv("WINDOW_SIZE", "1920,1080")

    # === THỜI GIAN CHỜ ===
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "20"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

    # === THÔNG TIN WEBSITE TEST ===
    BASE_URL: str = os.getenv("BASE_URL", "https://lab.connect247.vn/ucrm-ver3/")
    TEST_ENV: str = os.getenv("TEST_ENV", "staging")

    # === THÔNG TIN ĐĂNG NHẬP ===
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "testuser")
    DEFAULT_PASSWORD: str = os.getenv("DEFAULT_PASSWORD", "testpass123")

    # === SELENIUM GRID (Chạy test trên nhiều máy) ===
    # USE_GRID: bool = os.getenv("USE_GRID", "false").lower() == "true"
    # GRID_URL: str = os.getenv("GRID_URL", "http://localhost:4444/wd/hub")

    # === CẤU HÌNH LOG ===
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/test.log")

    # === CHẠY SONG SONG ===
    PARALLEL_WORKERS: int = int(os.getenv("PARALLEL_WORKERS", "4"))

    SCREENSHOT_TIMEOUT = 5

    @classmethod
    def get_window_size(cls) -> tuple[int, int]:
        """
        Chuyển đổi '1920,1080' thành (1920, 1080)

        Returns:
            Tuple chứa width và height
        """
        try:
            width, height = cls.WINDOW_SIZE.split(",")
            return int(width.strip()), int(height.strip())
        except (ValueError, AttributeError):
            # Fallback to default if parsing fails
            return 1920, 1080

    @classmethod
    def get_test_data_path(cls, filename: str) -> Path:
        """
        Lấy đường dẫn đầy đủ đến file test data

        Args:
            filename: Tên file test data

        Returns:
            Path object đến file test data
        """
        return cls.DATA_DIR / filename

    @classmethod
    def get_screenshot_path(cls, filename: str) -> Path:
        """
        Lấy đường dẫn đầy đủ đến file screenshot

        Args:
            filename: Tên file screenshot

        Returns:
            Path object đến file screenshot
        """
        return cls.screenshotS_DIR / filename

    @classmethod
    def get_report_path(cls, filename: str) -> Path:
        """
        Lấy đường dẫn đầy đủ đến file report

        Args:
            filename: Tên file report

        Returns:
            Path object đến file report
        """
        return cls.REPORTS_DIR / filename

    @classmethod
    def get_log_path(cls, filename: str) -> Path:
        """
        Lấy đường dẫn đầy đủ đến file log

        Args:
            filename: Tên file log

        Returns:
            Path object đến file log
        """
        return cls.LOGS_DIR / filename

    @classmethod
    def validate_settings(cls) -> None:
        """
        Kiểm tra tính hợp lệ của các cài đặt quan trọng

        Raises:
            ValueError: Nếu có cài đặt không hợp lệ
        """
        errors = []

        # Kiểm tra BASE_URL
        if not cls.BASE_URL or cls.BASE_URL == "https://example.com":
            errors.append("BASE_URL must be set to a valid URL")

        # Kiểm tra browser
        supported_browsers = ["chrome", "firefox", "edge", "safari"]
        if cls.BROWSER not in supported_browsers:
            errors.append(f"Unsupported browser: {cls.BROWSER}. Supported: {supported_browsers}")

        # Kiểm tra timeout values
        if cls.IMPLICIT_WAIT <= 0:
            errors.append("IMPLICIT_WAIT must be positive")

        if cls.EXPLICIT_WAIT <= 0:
            errors.append("EXPLICIT_WAIT must be positive")

        if cls.PAGE_LOAD_TIMEOUT <= 0:
            errors.append("PAGE_LOAD_TIMEOUT must be positive")

        # Kiểm tra parallel workers
        if cls.PARALLEL_WORKERS <= 0:
            errors.append("PARALLEL_WORKERS must be positive")

        # Kiểm tra log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"Invalid LOG_LEVEL: {cls.LOG_LEVEL}. Valid levels: {valid_log_levels}")

        # Kiểm tra window size format
        try:
            cls.get_window_size()
        except Exception:
            errors.append("WINDOW_SIZE must be in format 'width,height' (e.g., '1920,1080')")

        if errors:
            raise ValueError("Settings validation failed:\n" + "\n".join(f"- {error}" for error in errors))

    @classmethod
    def get_environment_info(cls) -> dict:
        """
        Lấy thông tin về môi trường test hiện tại

        Returns:
            Dictionary chứa thông tin môi trường
        """
        return {
            "browser": cls.BROWSER,
            "headless": cls.HEADLESS,
            "base_url": cls.BASE_URL,
            "test_env": cls.TEST_ENV,
            "window_size": cls.WINDOW_SIZE,
            "implicit_wait": cls.IMPLICIT_WAIT,
            "explicit_wait": cls.EXPLICIT_WAIT,
            "page_load_timeout": cls.PAGE_LOAD_TIMEOUT,
            "use_grid": cls.USE_GRID,
            "grid_url": cls.GRID_URL if cls.USE_GRID else None,
            "log_level": cls.LOG_LEVEL,
            "parallel_workers": cls.PARALLEL_WORKERS,
        }

    @classmethod
    def update_setting(cls, key: str, value: any) -> None:
        """
        Cập nhật một cài đặt cụ thể

        Args:
            key: Tên cài đặt
            value: Giá trị mới
        """
        if hasattr(cls, key.upper()):
            setattr(cls, key.upper(), value)
            print(f"✅ Updated {key.upper()} = {value}")
        else:
            print(f"❌ Setting {key.upper()} not found")

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Reset tất cả cài đặt về giá trị mặc định"""
        # Reload environment variables
        load_dotenv(override=True)

        # Reset to default values
        cls.BROWSER = os.getenv("BROWSER", "chrome").lower()
        cls.HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
        cls.WINDOW_SIZE = os.getenv("WINDOW_SIZE", "1920,1080")
        cls.IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
        cls.EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "20"))
        cls.PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
        cls.BASE_URL = os.getenv("BASE_URL", "https://example.com")
        cls.TEST_ENV = os.getenv("TEST_ENV", "staging")
        cls.DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "testuser")
        cls.DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "testpass123")
        cls.USE_GRID = os.getenv("USE_GRID", "false").lower() == "true"
        cls.GRID_URL = os.getenv("GRID_URL", "http://localhost:4444/wd/hub")
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        cls.LOG_FILE = os.getenv("LOG_FILE", "logs/test.log")
        cls.PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", "2"))

        print("✅ Settings reset to defaults")


# Initialize settings on import
try:
    # Settings.create_directories()
    Settings.validate_settings()
    print(f"✅ Settings initialized successfully, {os.getenv("HEADLESS")}")
except Exception as e:
    print(f"⚠️  Settings initialization warning: {e}")


# Convenience functions
def get_data_path(filename: str) -> Path:
    """Convenience function to get test data path."""
    return Settings.get_test_data_path(filename)


def get_screenshot_path(filename: str) -> Path:
    """Convenience function to get screenshot path."""
    return Settings.get_screenshot_path(filename)


def get_report_path(filename: str) -> Path:
    """Convenience function to get report path."""
    return Settings.get_report_path(filename)
