# pages/login/login_actions.py
"""Login actions containing business logic and workflows."""

import time
from typing import Optional

from ..base.base_actions import BaseActions
from .login_page import LoginPage
from utils.logger import Logger


class LoginActions(BaseActions):
    """Actions class for login business logic and workflows."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._login_page = None

    @property
    def login_page(self) -> LoginPage:
        """Lazy initialization of LoginPage"""
        if self._login_page is None:
            self._login_page = LoginPage(self.driver_manager)
        return self._login_page

    # ==================== BUSINESS WORKFLOWS ====================

    def clear_all_fields(self) -> "LoginActions":
        """Clear both username and password fields."""
        self.login_page.clear_username()
        self.login_page.clear_password()
        return self

    def login(self, username: str, password: str) -> "LoginActions":
        self.logger.info(f"Starting login process for user: {username}")

        # Wait for login form to be ready
        self.login_page.wait_for_login_form()

        # Enter credentials
        self.login_page.send_keys(self.login_page.login_locators.username, text=username)
        self.login_page.send_keys(self.login_page.login_locators.password, text=password)

        # Click login button
        self.login_page.click_login_button()
        time.sleep(1)

        self.logger.info("Login process completed")
        return self

    def login_with_autofill(self, test_data, wait_for_navigation: bool = True) -> "LoginActions":
        """
        Perform complete login action.

        Args:
            test_data: Truyền vào data test
            wait_for_navigation: Whether to wait for page navigation after login
        """
        self.logger.info(f"Starting login process for user: {test_data}")

        # Wait for login form to be ready
        self.login_page.wait_for_login_form()

        # Enter credentials
        self.auto_fill_form(test_data=test_data, skip_empty=False)

        # Click login button
        self.login_page.click_login_button()
        time.sleep(1)

        self.logger.info("Login process completed")
        return self

    # ==================== COMPLEX VALIDATIONS ====================

    def get_login_error(self) -> Optional[str]:
        """Get general login error message."""
        error_message = self.get_notice_message()
        if error_message:
            self.logger.warning(f"Login error message: {error_message}")
        return error_message
