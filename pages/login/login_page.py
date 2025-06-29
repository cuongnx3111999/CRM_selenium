# pages/login/login_page.py
"""Login page object model - Core operations only."""

from typing import Optional

from ..base.base_page import BasePage
from .login_locators import LoginLocators
from config.settings import Settings
from utils.logger import Logger


class LoginPage(BasePage):
    """Page Object for login page core functionality."""

    def __init__(self, driver):
        super().__init__(driver)
        self.login_locators = LoginLocators
        self.login_timeout = Settings.EXPLICIT_WAIT
        self.login_url = Settings.BASE_URL
        self.logger = Logger.get_logger(self.__class__.__name__)

    # ==================== NAVIGATION METHODS ====================

    def navigate_to_login_page(self, url: str = None) -> "LoginPage":
        """Navigate to login page."""
        if url is None:
            url = self.login_url
        self.logger.info(f"Navigating to login page: {url}")
        self.open_url(url)
        self.click_login_button()
        return self

    def click_login_button(self) -> "LoginPage":
        """Click the login button."""
        self.logger.info("Clicking login button")
        self.wait_for_clickable(self.login_locators.btn_login)
        self.click(self.login_locators.btn_login)
        self.logger.info("Login button clicked")
        return self

    # ==================== INPUT METHODS ====================

    def enter_username(self, username: str) -> "LoginPage":
        """Enter username in the username field."""
        self.logger.info(f"Entering username: {username}")
        self.wait_for_element(self.login_locators.username)
        self.send_keys(self.login_locators.username, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password in the password field."""
        self.logger.info("Entering password")
        self.wait_for_element(self.login_locators.password)
        self.send_keys(self.login_locators.password, password)
        return self

    def clear_username(self) -> "LoginPage":
        """Clear username field."""
        self.clear_inputs(self.login_locators.username)
        return self

    def clear_password(self) -> "LoginPage":
        """Clear password field."""
        self.clear_inputs(self.login_locators.password)
        return self

    # ==================== VALIDATION METHODS ====================

    def is_login_successful(self) -> bool:
        """Check if login was successful (not on login page anymore)."""
        # Wait a bit for potential page transition

        try:
            self.wait_for_element(self.base_locators.btn_add_language)
            self.logger.info(f"Login successful")
            return True
        except:
            return False

    # ==================== UTILITY METHODS ====================

    def wait_for_login_form(self, timeout: int = None) -> "LoginPage":
        """Wait for login form to be fully loaded."""
        if timeout is None:
            timeout = self.login_timeout

        self.wait_for_element(self.login_locators.username, timeout)
        self.wait_for_clickable(self.login_locators.username, timeout)
        self.wait_for_clickable(self.login_locators.password, timeout)
        self.wait_for_clickable(self.login_locators.btn_login, timeout)

        self.logger.info("Login form is ready")
        return self

    def get_username_value(self) -> str:
        """Get current value in username field."""
        return self.get_attribute(self.login_locators.username, "value")

    def get_password_value(self) -> str:
        """Get current value in password field."""
        return self.get_attribute(self.login_locators.password, "value")
