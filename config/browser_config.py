# config/browser_config.py
"""Browser configuration and options for different browsers."""

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from typing import Union, Dict, List

from .settings import Settings


class BrowserConfig:
    """Browser configuration class for managing browser options and capabilities."""

    @staticmethod
    def get_chrome_options() -> ChromeOptions:
        """Get Chrome browser options with optimized settings."""
        options = ChromeOptions()

        # Basic Chrome arguments
        chrome_args = [
            "--incognito",  # Chế độ ẩn danh - không lưu lịch sử, cookies, cache
            "--no-sandbox",  # Tắt sandbox security - cần thiết cho Docker/CI environments
            "--disable-dev-shm-usage",  # Tránh lỗi thiếu bộ nhớ chia sẻ trong Docker
            "--disable-extensions",  # Tắt tất cả extensions để tăng tốc độ
            "--disable-infobars",  # Ẩn thanh thông báo "Chrome is being controlled by automated software"
            "--disable-notifications",  # Tắt popup notifications từ websites
            "--disable-popup-blocking",  # Cho phép popup windows (nếu test cần)
            "--disable-translate",  # Tắt tính năng dịch tự động của Chrome
            "--disable-background-timer-throttling",  # Tắt throttling timer cho background tabs
            "--disable-backgrounding-occluded-windows",  # Không làm chậm windows bị che khuất
            "--disable-renderer-backgrounding",  # Không làm chậm renderer process
            "--disable-features=TranslateUI",  # Tắt giao diện dịch thuật
            "--disable-ipc-flooding-protection",  # Tắt bảo vệ chống flooding IPC messages
            "--disable-hang-monitor",  # Tắt monitor theo dõi treo ứng dụng
            "--disable-client-side-phishing-detection",  # Tắt phát hiện phishing
            "--disable-component-update",  # Tắt tự động update components
            "--disable-default-apps",  # Không cài đặt default apps
            "--disable-domain-reliability",  # Tắt báo cáo reliability về Google
            "--disable-background-networking",  # Tắt network requests ở background
            "--disable-sync",  # Tắt đồng bộ hóa với Google account
            "--metrics-recording-only",  # Chỉ ghi metrics, không gửi về Google
            "--no-first-run",  # Bỏ qua setup wizard lần đầu chạy
            "--safebrowsing-disable-auto-update",  # Tắt tự động update Safe Browsing
            "--disable-logging",  # Tắt logging của Chrome
            "--silent",  # Chạy im lặng, không hiển thị console output
        ]

        # Add all arguments
        for arg in chrome_args:
            options.add_argument(arg)

        # Window size
        width, height = Settings.get_window_size()
        options.add_argument(f"--window-size={width},{height}")

        # Headless mode
        if Settings.HEADLESS:
            options.add_argument("--headless=new")  # Chrome 109+
            options.add_argument("--disable-gpu")
            print("🔧 Chrome HEADLESS mode enabled")
        else:
            print("🔧 Chrome NORMAL mode enabled")

        # Chrome preferences
        prefs = {
            # Notifications and popups
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "profile.default_content_settings.popups": 0,  # Allow popups (0=allow, 1=block)
            # Images - CHANGED to allow images
            "profile.managed_default_content_settings.images": 1,  # Allow images (1=allow, 2=block)
            # Location and media permissions
            "profile.default_content_setting_values.geolocation": 2,  # Block geolocation
            "profile.default_content_setting_values.media_stream": 2,  # Block camera/microphone
            # Download settings
            "profile.default_content_settings.multiple-automatic-downloads": 1,  # Allow multiple downloads
            "download.default_directory": str(Settings.REPORTS_DIR / "downloads"),  # Fixed path
            "download.prompt_for_download": False,  # Don't prompt for download
            "download.directory_upgrade": True,  # Allow directory upgrade
            "profile.default_content_setting_values.automatic_downloads": 1,  # Allow automatic downloads
            # Security settings
            "safebrowsing.enabled": False,  # Disable safe browsing for faster loading
            # Password manager - REMOVED DUPLICATES
            "profile.password_manager_enabled": False,  # Disable password manager
            "credentials_enable_service": False,  # Disable credentials service
            # Additional performance settings
            "profile.default_content_setting_values.plugins": 1,  # Allow plugins
            "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,  # Allow Flash if needed
            "profile.default_content_setting_values.javascript": 1,  # Allow JavaScript
        }

        options.add_experimental_option("prefs", prefs)

        # Additional experimental options
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        # Add user agent to avoid detection
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        return options

    @staticmethod
    def get_firefox_options() -> FirefoxOptions:
        """Get Firefox browser options with optimized settings."""
        options = FirefoxOptions()

        # Headless mode
        if Settings.HEADLESS:
            options.add_argument("--headless")

        # Window size
        width, height = Settings.get_window_size()
        options.add_argument(f"--width={width}")
        options.add_argument(f"--height={height}")

        # Firefox preferences
        firefox_prefs = {
            # Disable notifications
            "dom.webnotifications.enabled": False,
            "dom.push.enabled": False,
            # Disable geolocation
            "geo.enabled": False,
            "geo.provider.use_corelocation": False,
            "geo.prompt.testing": False,
            "geo.prompt.testing.allow": False,
            # Media settings
            "media.volume_scale": "0.0",
            "media.autoplay.default": 5,
            "media.autoplay.blocking_policy": 2,
            # Download settings
            "browser.download.folderList": 2,
            "browser.download.manager.showWhenStarting": False,
            "browser.download.dir": str(Settings.REPORTS_DIR / "downloads"),
            "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream,text/csv,application/pdf",
            # Performance settings
            "browser.cache.disk.enable": False,
            "browser.cache.memory.enable": False,
            "browser.cache.offline.enable": False,
            "network.http.use-cache": False,
            # Security settings
            "security.tls.insecure_fallback_hosts": "",
            "security.tls.unrestricted_rc4_fallback": False,
            # Disable password manager
            "signon.rememberSignons": False,
            "signon.autofillForms": False,
            # Disable updates
            "app.update.enabled": False,
            "app.update.auto": False,
            # Privacy settings
            "privacy.trackingprotection.enabled": False,
            "datareporting.healthreport.uploadEnabled": False,
            "datareporting.policy.dataSubmissionEnabled": False,
            # Disable animations for faster execution
            "toolkit.cosmeticAnimations.enabled": False,
            "browser.fullscreen.animateUp": 0,
            # Logging
            "devtools.console.stdout.chrome": True,
        }

        # Set all preferences
        for pref, value in firefox_prefs.items():
            options.set_preference(pref, value)

        return options

    @staticmethod
    def get_edge_options() -> EdgeOptions:
        """Get Edge browser options with optimized settings."""
        options = EdgeOptions()

        # Use Chrome-like options for Edge (since Edge is Chromium-based)
        edge_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor",
            "--disable-logging",
            "--silent",
        ]

        # Add all arguments
        for arg in edge_args:
            options.add_argument(arg)

        # Window size
        width, height = Settings.get_window_size()
        options.add_argument(f"--window-size={width},{height}")

        # Headless mode
        if Settings.HEADLESS:
            options.add_argument("--headless=new")

        # Edge preferences (similar to Chrome)
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "download.default_directory": str(Settings.REPORTS_DIR / "downloads"),
            "download.prompt_for_download": False,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
        }

        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        return options

    @staticmethod
    def get_safari_options() -> SafariOptions:
        """Get Safari browser options."""
        options = SafariOptions()

        # Safari has limited options compared to other browsers
        # Most configurations are done through Safari preferences

        return options

    @classmethod
    def get_browser_options(cls, browser_name: str) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions]:
        """
        Get browser options based on browser name.

        Args:
            browser_name: Name of the browser ('chrome', 'firefox', 'edge', 'safari')

        Returns:
            Browser options object

        Raises:
            ValueError: If browser is not supported
        """
        browser_name = browser_name.lower().strip()

        browser_map = {
            "chrome": cls.get_chrome_options,
            "firefox": cls.get_firefox_options,
            "edge": cls.get_edge_options,
            "safari": cls.get_safari_options,
        }

        if browser_name not in browser_map:
            supported_browsers = ", ".join(browser_map.keys())
            raise ValueError(f"Unsupported browser: {browser_name}. Supported browsers: {supported_browsers}")

        return browser_map[browser_name]()

    @staticmethod
    def get_mobile_chrome_options(device_name: str = "iPhone X") -> ChromeOptions:
        """
        Get Chrome options for mobile emulation.

        Args:
            device_name: Name of the device to emulate

        Returns:
            ChromeOptions configured for mobile emulation
        """
        options = BrowserConfig.get_chrome_options()

        # Mobile emulation
        mobile_emulation = {"deviceName": device_name}
        options.add_experimental_option("mobileEmulation", mobile_emulation)

        return options

    @staticmethod
    def get_custom_chrome_options(custom_args: List[str] = None, custom_prefs: Dict = None) -> ChromeOptions:
        """
        Get Chrome options with custom arguments and preferences.

        Args:
            custom_args: List of custom Chrome arguments
            custom_prefs: Dictionary of custom Chrome preferences

        Returns:
            ChromeOptions with custom settings
        """
        options = BrowserConfig.get_chrome_options()

        # Add custom arguments
        if custom_args:
            for arg in custom_args:
                options.add_argument(arg)

        # Add custom preferences
        if custom_prefs:
            # Get existing prefs and update with custom ones
            existing_prefs = options.experimental_options.get("prefs", {})
            existing_prefs.update(custom_prefs)
            options.add_experimental_option("prefs", existing_prefs)

        return options

    @staticmethod
    def get_performance_optimized_options(browser_name: str) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions]:
        """
        Get browser options optimized for performance (faster test execution).

        Args:
            browser_name: Name of the browser

        Returns:
            Browser options optimized for performance
        """
        options = BrowserConfig.get_browser_options(browser_name)

        if browser_name.lower() == "chrome":
            # Additional performance optimizations for Chrome
            performance_args = [
                "--disable-images",
                "--disable-javascript",
                "--disable-plugins",
                "--disable-java",
                "--disable-extensions",
                "--no-proxy-server",
                "--max_old_space_size=4096",
            ]

            for arg in performance_args:
                options.add_argument(arg)

        elif browser_name.lower() == "firefox":
            # Additional performance optimizations for Firefox
            performance_prefs = {
                "javascript.enabled": False,
                "permissions.default.image": 2,  # Block images
                "dom.ipc.plugins.enabled.libflashplayer.so": False,
            }

            for pref, value in performance_prefs.items():
                options.set_preference(pref, value)

        return options

    @staticmethod
    def get_debug_options(browser_name: str) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions]:
        """
        Get browser options for debugging (with developer tools, logging, etc.).

        Args:
            browser_name: Name of the browser

        Returns:
            Browser options configured for debugging
        """
        options = BrowserConfig.get_browser_options(browser_name)

        if browser_name.lower() == "chrome":
            # Remove silent and logging disable arguments for debugging
            debug_args = ["--enable-logging", "--log-level=0", "--v=1", "--auto-open-devtools-for-tabs"]

            for arg in debug_args:
                options.add_argument(arg)

        elif browser_name.lower() == "firefox":
            # Enable debugging for Firefox
            debug_prefs = {
                "devtools.console.stdout.chrome": True,
                "devtools.debugger.remote-enabled": True,
                "devtools.chrome.enabled": True,
            }

            for pref, value in debug_prefs.items():
                options.set_preference(pref, value)

        return options
