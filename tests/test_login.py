# pages/login/test_login.py
"""Test cases for login functionality with data-driven approach."""

import time
from time import sleep

import pytest
from typing import Dict, Any

from pages.login.login_page import LoginPage
from pages.login.login_actions import LoginActions
from utils.logger import Logger
from utils.pytest_data_helpers import (
    filter_by_expected_result,
    filter_by_expected_message,
    excel_data_provider,
    filter_by_test_function,
)


@pytest.mark.login
class TestLogin:
    """Test suite for login functionality with comprehensive validation scenarios"""

    def setup_method(self):
        """Setup before each test method"""
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.logger.info("Starting login test setup")

    def teardown_method(self):
        """Cleanup after each test method"""
        self.logger.info("Login test completed")

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_login_page(self, driver) -> LoginPage:
        """Initialize login page and navigate to it"""
        try:
            login_page = LoginPage(driver)
            login_page.navigate_to_login_page()
            self.logger.debug("Successfully navigated to login page")
            return login_page
        except Exception as e:
            self.logger.error(f"Failed to initialize login page: {e}")
            raise

    def _get_login_actions(self, driver) -> LoginActions:
        """Initialize login actions with lazy initialization"""
        try:
            login_actions = LoginActions(driver)
            self.logger.debug("Successfully initialized login actions")
            return login_actions
        except Exception as e:
            self.logger.error(f"Failed to initialize login actions: {e}")
            raise

    def _log_test_start(self, test_type: str, test_data: Dict[str, Any]) -> None:
        """Log test start with sanitized data"""
        safe_data = {k: v for k, v in test_data.items() if k != "password"}
        safe_data["password"] = "***" if test_data.get("password") else ""
        self.logger.info(f"Starting {test_type} test with data: {safe_data}")

    # ========================================================================
    # ACCOUNT LOCKOUT TESTS
    # ========================================================================

    @excel_data_provider(
        "datatest_login.xlsx",
        filter_func=filter_by_test_function("test_user_account_lock"),
    )
    def test_user_account_lock(self, driver, test_data):
        """Test user account lockout mechanism after multiple failed login attempts"""
        self._log_test_start("account lockout", test_data)

        self.logger.info(f"---{test_data}---")

        login_page = self._get_login_page(driver)
        login_actions = self._get_login_actions(driver)
        max_attempts = 5

        try:
            # Step 1: Enter wrong credentials to trigger lockout
            wrong_password = test_data["basic_pass"] + "abc"
            self.logger.info(f"Attempting {max_attempts} failed logins to trigger lockout")

            login_actions.auto_fill_form(test_data=test_data)  # Muốn sử dụng hàm autofill nên điền password đúng xong đó xóa điền password sai vào
            login_page.clear_password()
            login_page.send_keys(login_page.login_locators.password, text=wrong_password)

            # Perform multiple failed login attempts
            for attempt in range(max_attempts):
                self.logger.debug(f"Failed login attempt {attempt + 1}/{max_attempts}")
                login_page.click_login_button()
                time.sleep(10)

            # Step 2: Clear fields and try with correct credentials
            login_actions.clear_all_fields()
            self.logger.info("Attempting login with correct credentials after lockout")
            time.sleep(10)

            login_actions.login_with_autofill(test_data=test_data)

            # Step 3: Verify lockout message
            error_message = login_actions.get_login_error()
            assert "lock" in error_message, "khong co thong bao locked "

            self.logger.info("✅ Account lockout mechanism working correctly")

        except Exception as e:
            self.logger.error(f"Account lockout test failed: {e}")
            raise

    # ========================================================================
    # SUCCESSFUL LOGIN TESTS
    # ========================================================================

    @excel_data_provider("datatest_login.xlsx", filter_func=filter_by_test_function("test_successful_login"))
    def test_successful_login(self, driver, test_data):
        """Test successful login scenarios with valid credentials"""
        self._log_test_start("successful login", test_data)

        try:
            login_page = self._get_login_page(driver)
            login_actions = self._get_login_actions(driver)

            login_actions.login_with_autofill(test_data=test_data)

            # Verify successful login by checking navigation
            assert login_page.is_login_successful(), f"Login should be successful for user: {test_data['basic_email']}"

            self.logger.info(f"✅ Login successful for user: {test_data['basic_email']}")

        except Exception as e:
            self.logger.error(f"Successful login test failed for {test_data['basic_email']}: {e}")
            raise

    # ========================================================================
    # FAILED LOGIN TESTS
    # ========================================================================

    @pytest.mark.dependency(depends=["TestLogin::test_user_account_lockout"])
    @excel_data_provider("datatest_login.xlsx", filter_func=filter_by_test_function(["test_failed_login", "test_validation"]))
    def test_failed_login(self, driver, test_data):
        """Test failed login scenarios with invalid credentials"""
        self._log_test_start("failed login", test_data)

        try:
            login_page = self._get_login_page(driver)
            login_actions = self._get_login_actions(driver)

            login_actions.login_with_autofill(test_data=test_data, wait_for_navigation=False)

            # Verify user remains on login page
            assert not login_page.is_login_successful(), f"Should remain on login page for failed login: {test_data['basic_email']}"

            self.logger.info(f"✅ Login failed as expected for user: {test_data['basic_email']}")

        except Exception as e:
            self.logger.error(f"Failed login test error for {test_data['basic_email']}: {e}")
            raise

    # ========================================================================
    # FIELD VALIDATION TESTS
    # ========================================================================

    @excel_data_provider("datatest_login.xlsx", filter_func=filter_by_test_function("test_validation"))
    def test_validation(self, driver, test_data):
        """Test username field validation"""
        self._log_test_start("username validation", test_data)

        try:
            login_page = self._get_login_page(driver)
            login_actions = self._get_login_actions(driver)

            login_actions.login_with_autofill(test_data=test_data, wait_for_navigation=False)

            # Verify username validation error
            assert login_actions.auto_validate_field_error_form(
                test_data=test_data, field=test_data["field"], expected_message=test_data["expected_message"]
            ), f"Validation user fail: {test_data['basic_email']}"

            self.logger.info("✅ validation working correctly")

        except Exception as e:
            self.logger.error(f"validation test failed: {e}")
            raise

    # ========================================================================
    # LOGIN ERROR TESTS
    # ========================================================================

    @excel_data_provider("datatest_login.xlsx", filter_func=filter_by_test_function(["test_failed_login", "test_login_errors"]))
    def test_login_errors(self, driver, test_data):
        """Test specific login error scenarios"""
        self._log_test_start("login error", test_data)

        try:
            login_page = self._get_login_page(driver)
            login_actions = self._get_login_actions(driver)

            login_actions.login_with_autofill(test_data=test_data, wait_for_navigation=False)

            # Verify specific error message
            error_message = login_actions.get_notice_message()
            assert test_data["expected_message"] in error_message, "login error test failed"

        except Exception as e:
            self.logger.error(f"Login error test failed: {e}")
            raise
