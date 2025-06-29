# utils/driver_manager.py
"""Singleton WebDriver manager với custom download path support"""

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import Settings
from config.browser_config import BrowserConfig
from .logger import Logger


class DriverManager:
    """Singleton class quản lý WebDriver instance với custom download path support"""

    _instance = None
    _driver = None
    _current_page = None
    _current_download_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_driver(self, browser_name: str = None, page_name: str = None) -> WebDriver:
        """
        Lấy hoặc tạo WebDriver instance với custom download path

        Args:
            browser_name (str): Tên browser (chrome, firefox, edge)
            page_name (str): Tên page để set download path (users, login, etc.)

        Returns:
            WebDriver: Driver instance
        """
        # Nếu đổi page, restart driver để áp dụng download path mới
        if page_name and page_name != self._current_page and self._driver is not None:
            Logger.get_logger().info(f"Page changed from '{self._current_page}' to '{page_name}' - restarting driver")
            self.quit_driver()

        if self._driver is None:
            self._driver = self._create_driver(browser_name, page_name)
            self._current_page = page_name

        return self._driver

    def get_driver_with_custom_download(self, download_path: str, browser_name: str = None) -> WebDriver:
        """
        Tạo driver với custom download path cụ thể

        Args:
            download_path (str): Custom download path (absolute hoặc relative)
            browser_name (str): Browser name (chrome, firefox, edge)

        Returns:
            WebDriver: Driver với custom download path
        """
        # Quit driver hiện tại
        self.quit_driver()

        if browser_name is None:
            browser_name = Settings.BROWSER

        browser_name = browser_name.lower()

        # Convert to absolute path và tạo directory nếu chưa có
        abs_download_path = Path(download_path).resolve()
        abs_download_path.mkdir(parents=True, exist_ok=True)

        logger = Logger.get_logger()
        logger.info(f"Creating {browser_name} driver with custom download path: {abs_download_path}")

        if browser_name == "chrome":
            options = self._get_chrome_options_with_download(str(abs_download_path))
            driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
        elif browser_name == "firefox":
            options = self._get_firefox_options_with_download(str(abs_download_path))
            driver = webdriver.Firefox(service=webdriver.FirefoxService(GeckoDriverManager().install()), options=options)
        elif browser_name == "edge":
            options = self._get_edge_options_with_download(str(abs_download_path))
            driver = webdriver.Edge(service=webdriver.EdgeService(EdgeChromiumDriverManager().install()), options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        # Apply standard configurations
        driver.implicitly_wait(Settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)

        if not Settings.HEADLESS:
            driver.maximize_window()

        # Store driver and custom info
        self._driver = driver
        self._current_page = f"custom_{abs_download_path.name}"
        self._current_download_path = str(abs_download_path)

        # Add custom attribute to driver for easy access
        driver.download_directory = abs_download_path

        logger.info(f"✅ Custom download driver created successfully: {abs_download_path}")
        return driver

    def get_driver_with_temp_download(self, prefix: str = "temp_download_", browser_name: str = None) -> WebDriver:
        """
        Tạo driver với temporary download directory

        Args:
            prefix (str): Prefix cho temp directory name
            browser_name (str): Browser name

        Returns:
            WebDriver: Driver với temp download path
        """
        import tempfile

        # Tạo temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))

        logger = Logger.get_logger()
        logger.info(f"Creating driver with temporary download directory: {temp_dir}")

        driver = self.get_driver_with_custom_download(str(temp_dir), browser_name)

        # Mark as temporary for cleanup
        driver.is_temp_download = True
        driver.temp_directory = temp_dir

        return driver

    def _create_driver(self, browser_name: str = None, page_name: str = None) -> WebDriver:
        """Tạo WebDriver instance mới với custom download path"""
        if browser_name is None:
            browser_name = Settings.BROWSER

        browser_name = browser_name.lower()
        logger = Logger.get_logger()

        logger.info(f"Creating {browser_name} driver for page: {page_name}")

        return self._create_local_driver(browser_name, page_name)

    def _create_local_driver(self, browser_name: str, page_name: str = None) -> WebDriver:
        """Tạo local WebDriver với custom download path"""

        # Lấy custom download path nếu có page_name
        download_path = None
        if page_name:
            download_path = self._get_page_download_path(page_name)
            Logger.get_logger().info(f"Setting download path for page '{page_name}': {download_path}")

        if browser_name == "chrome":
            options = self._get_chrome_options_with_download(download_path)
            driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
        elif browser_name == "firefox":
            options = self._get_firefox_options_with_download(download_path)
            driver = webdriver.Firefox(service=webdriver.FirefoxService(GeckoDriverManager().install()), options=options)
        elif browser_name == "edge":
            options = self._get_edge_options_with_download(download_path)
            driver = webdriver.Edge(service=webdriver.EdgeService(EdgeChromiumDriverManager().install()), options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        # Cấu hình timeouts
        driver.implicitly_wait(Settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)

        # Maximize window nếu không headless
        if not Settings.HEADLESS:
            driver.maximize_window()

        # Add download directory attribute if set
        if download_path:
            driver.download_directory = Path(download_path)
            self._current_download_path = download_path

        return driver

    def _get_page_download_path(self, page_name: str) -> str:
        """
        Lấy download path cho page

        Args:
            page_name (str): Tên page

        Returns:
            str: Absolute path đến export folder của page
        """
        base_path = Path(__file__).parent.parent  # CRM_selenium_framework/
        download_dir = base_path / "pages" / page_name / "export_file"

        # Tạo directory nếu chưa có
        download_dir.mkdir(parents=True, exist_ok=True)

        return str(download_dir.absolute())

    def _get_chrome_options_with_download(self, download_path: str = None) -> ChromeOptions:
        """Lấy Chrome options với custom download path"""
        # Bắt đầu với options từ BrowserConfig
        options = BrowserConfig.get_browser_options("chrome")

        # Thêm download preferences nếu có download_path
        if download_path:
            prefs = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }
            options.add_experimental_option("prefs", prefs)
            Logger.get_logger().debug(f"Chrome download preferences set: {prefs}")

        return options

    def _get_firefox_options_with_download(self, download_path: str = None) -> FirefoxOptions:
        """Lấy Firefox options với custom download path"""
        # Bắt đầu với options từ BrowserConfig
        options = BrowserConfig.get_browser_options("firefox")

        # Thêm download preferences nếu có download_path
        if download_path:
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", download_path)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.download.viewableInternally.enabledTypes", "")
            options.set_preference(
                "browser.helperApps.neverAsk.saveToDisk",
                "text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/pdf,application/json,text/plain",
            )
            options.set_preference("pdfjs.disabled", True)  # Disable PDF viewer
            Logger.get_logger().debug(f"Firefox download directory set: {download_path}")

        return options

    def _get_edge_options_with_download(self, download_path: str = None) -> EdgeOptions:
        """Lấy Edge options với custom download path"""
        # Bắt đầu với options từ BrowserConfig
        options = BrowserConfig.get_browser_options("edge")

        # Thêm download preferences nếu có download_path
        if download_path:
            prefs = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }
            options.add_experimental_option("prefs", prefs)
            Logger.get_logger().debug(f"Edge download preferences set: {prefs}")

        return options

    def quit_driver(self):
        """Đóng và cleanup driver"""
        if self._driver:
            try:
                # Cleanup temp directory nếu có
                if hasattr(self._driver, "is_temp_download") and self._driver.is_temp_download:
                    temp_dir = getattr(self._driver, "temp_directory", None)
                    if temp_dir and temp_dir.exists():
                        import shutil

                        shutil.rmtree(temp_dir)
                        Logger.get_logger().info(f"Cleaned up temp download directory: {temp_dir}")

                self._driver.quit()
                Logger.get_logger().info("Driver closed successfully")
            except Exception as e:
                Logger.get_logger().error(f"Error closing driver: {e}")
            finally:
                self._driver = None
                self._current_page = None
                self._current_download_path = None

    def restart_driver(self, browser_name: str = None, page_name: str = None):
        """
        Restart driver với page mới

        Args:
            browser_name (str): Browser name
            page_name (str): Page name cho download path

        Returns:
            WebDriver: New driver instance
        """
        Logger.get_logger().info(f"Restarting driver for page: {page_name}")
        self.quit_driver()
        return self.get_driver(browser_name, page_name)

    def restart_driver_with_custom_download(self, download_path: str, browser_name: str = None):
        """
        Restart driver với custom download path

        Args:
            download_path (str): Custom download path
            browser_name (str): Browser name

        Returns:
            WebDriver: New driver instance
        """
        Logger.get_logger().info(f"Restarting driver with custom download path: {download_path}")
        self.quit_driver()
        return self.get_driver_with_custom_download(download_path, browser_name)

    def get_current_page(self) -> Optional[str]:
        """Lấy page hiện tại"""
        return self._current_page

    def get_current_download_path(self) -> Optional[str]:
        """Lấy download path hiện tại"""
        return self._current_download_path

    def change_page(self, page_name: str, browser_name: str = None) -> WebDriver:
        """
        Thay đổi page và restart driver nếu cần

        Args:
            page_name (str): Page name mới
            browser_name (str): Browser name (optional)

        Returns:
            WebDriver: Driver instance
        """
        if page_name != self._current_page:
            Logger.get_logger().info(f"Changing page from '{self._current_page}' to '{page_name}'")
            return self.restart_driver(browser_name, page_name)
        else:
            return self.get_driver(browser_name, page_name)

    def change_download_path(self, download_path: str, browser_name: str = None) -> WebDriver:
        """
        Thay đổi download path và restart driver

        Args:
            download_path (str): New download path
            browser_name (str): Browser name (optional)

        Returns:
            WebDriver: Driver instance với new download path
        """
        abs_path = str(Path(download_path).resolve())
        if abs_path != self._current_download_path:
            Logger.get_logger().info(f"Changing download path from '{self._current_download_path}' to '{abs_path}'")
            return self.restart_driver_with_custom_download(download_path, browser_name)
        else:
            return self._driver

    def get_download_files(self, pattern: str = "*") -> list[Path]:
        """
        Lấy danh sách file trong download directory hiện tại

        Args:
            pattern (str): File pattern để filter

        Returns:
            list[Path]: Danh sách file paths
        """
        if not self._current_download_path:
            Logger.get_logger().warning("No download path set")
            return []

        download_dir = Path(self._current_download_path)
        if not download_dir.exists():
            return []

        files = list(download_dir.glob(pattern))
        Logger.get_logger().debug(f"Found {len(files)} files with pattern '{pattern}' in {download_dir}")
        return files

    def wait_for_download(self, timeout: int = 30, expected_extension: str = None) -> Optional[Path]:
        """
        Chờ file download hoàn thành trong download directory hiện tại

        Args:
            timeout (int): Timeout in seconds
            expected_extension (str): Expected file extension (e.g., '.csv', '.pdf')

        Returns:
            Optional[Path]: Downloaded file path hoặc None
        """
        if not self._current_download_path:
            Logger.get_logger().error("No download path set - cannot wait for download")
            return None

        download_dir = Path(self._current_download_path)
        files_before = set(download_dir.glob("*")) if download_dir.exists() else set()

        Logger.get_logger().info(f"Waiting for download in: {download_dir}")

        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            if download_dir.exists():
                current_files = set(download_dir.glob("*"))
                new_files = current_files - files_before

                if new_files:
                    # Lọc file tạm
                    valid_files = [f for f in new_files if not self._is_temp_file(f)]

                    # Filter by extension nếu có
                    if expected_extension and valid_files:
                        valid_files = [f for f in valid_files if f.suffix.lower() == expected_extension.lower()]

                    if valid_files:
                        newest_file = max(valid_files, key=lambda f: f.stat().st_mtime)
                        Logger.get_logger().info(f"Download completed: {newest_file}")
                        return newest_file

            time.sleep(1)

        Logger.get_logger().warning(f"No download detected within {timeout} seconds")
        return None

    def _is_temp_file(self, file_path: Path) -> bool:
        """Check file có phải temporary file không"""
        temp_extensions = {".tmp", ".temp", ".crdownload", ".download", ".part"}
        return file_path.suffix.lower() in temp_extensions

    def cleanup_download_directory(self, keep_latest: int = 0) -> int:
        """
        Dọn dẹp download directory hiện tại

        Args:
            keep_latest (int): Số file mới nhất cần giữ lại

        Returns:
            int: Số file đã xóa
        """
        if not self._current_download_path:
            Logger.get_logger().warning("No download path set")
            return 0

        download_dir = Path(self._current_download_path)
        if not download_dir.exists():
            return 0

        files = list(download_dir.glob("*"))
        if not files:
            return 0

        # Sắp xếp theo thời gian sửa đổi (mới nhất trước)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Xóa file cũ
        files_to_delete = files[keep_latest:] if keep_latest > 0 else files
        deleted_count = 0

        for file_path in files_to_delete:
            try:
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
                    Logger.get_logger().debug(f"Deleted file: {file_path}")
            except Exception as e:
                Logger.get_logger().warning(f"Failed to delete file {file_path}: {e}")

        Logger.get_logger().info(f"Cleaned up {deleted_count} files from download directory")
        return deleted_count

    def get_driver_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết về driver hiện tại

        Returns:
            Dict: Driver information
        """
        info = {
            "has_driver": self._driver is not None,
            "current_page": self._current_page,
            "download_path": self._current_download_path,
            "browser_name": None,
            "session_id": None,
            "window_handles": None,
        }

        if self._driver:
            try:
                info.update(
                    {
                        "browser_name": self._driver.capabilities.get("browserName"),
                        "browser_version": self._driver.capabilities.get("browserVersion"),
                        "session_id": self._driver.session_id,
                        "window_handles": len(self._driver.window_handles),
                        "current_url": self._driver.current_url,
                    }
                )
            except Exception as e:
                Logger.get_logger().warning(f"Error getting driver info: {e}")

        return info

    def __str__(self) -> str:
        """String representation của DriverManager"""
        info = self.get_driver_info()
        return f"DriverManager(page={info['current_page']}, browser={info['browser_name']}, download_path={info['download_path']})"

    def __repr__(self) -> str:
        """Detailed representation của DriverManager"""
        return self.__str__()
