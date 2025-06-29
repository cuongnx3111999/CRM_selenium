# pages/users/users_page.py
"""Users page object model - Page Operations only."""
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from ..base.base_page import BasePage
from .users_locators import UsersLocators
from config.settings import Settings
from utils.logger import Logger

from bs4 import BeautifulSoup


class UsersPage(BasePage):
    """Page Object for users page basic operations."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.users_locators = UsersLocators
        self.users_timeout = Settings.EXPLICIT_WAIT
        self.users_url = Settings.BASE_URL
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.driver_manager = driver_manager
        self._base_actions = None

    @property
    def base_actions(self):
        """Lazy initialization of BaseActions"""
        if self._base_actions is None:
            from ..base.base_actions import BaseActions

            self._base_actions = BaseActions(self.driver_manager)
        return self._base_actions

    # ========================================================================
    # Wrapper Methods for BaseActions functionality
    # ========================================================================
    def click_save(self, index=0):
        """Wrapper for BaseActions click_save method"""
        return self.base_actions.click_save(index)

    def click_cancel(self, index=0):
        """Wrapper for BaseActions click_cancel method"""
        return self.base_actions.click_cancel(index)

    def validate_field_error(self, field_locator, error_locator, expected_message="Please input", field_name="Field"):
        """Wrapper for BaseActions validate_field_error method"""
        return self.base_actions.validate_field_error(field_locator, error_locator, expected_message, field_name)

    # ========================================================================
    # Navigation Methods
    # ========================================================================
    def open_users_page(self):
        """Navigate to users page through settings menu"""
        try:
            self.wait_for_element(self.base_locators.btn_setting)
            self.click(self.base_locators.btn_setting)
            self.wait_for_element(self.users_locators.btn_users)
            self.click(self.users_locators.btn_users)
            self.logger.info("Successfully navigated to users page")
            return self
        except NoSuchElementException as e:
            self.logger.error(f"Element not found when opening users page: {e}")
            raise
        except TimeoutException as e:
            self.logger.error(f"Timeout when opening users page: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error when opening users page: {e}")
            raise

    # ========================================================================
    # Data Retrieval Methods
    # ========================================================================
    def get_users_data(self):
        """
        Extract users table data using BeautifulSoup
        Returns: list of dictionaries containing user data
        """
        try:
            sleep(3)

            table_element = self.find_element(self.base_locators.table_content)
            if not table_element:
                self.logger.warning("Table content element not found")
                return []

            html_content = table_element.get_attribute("outerHTML")
            if not html_content:
                self.logger.warning("No HTML content found in table")
                return []

            soup = BeautifulSoup(html_content, "lxml")

            # Extract headers
            headers = self._extract_table_headers(soup)
            if not headers:
                self.logger.warning("No table headers found")
                return []

            # Extract rows data
            users_data = self._extract_table_rows(soup, headers)

            self.logger.info(f"Successfully extracted {len(users_data)} users data")
            return users_data

        except Exception as e:
            self.logger.error(f"Failed to extract users data: {e}")
            return []

    def _extract_table_headers(self, soup):
        """Extract table headers from soup object"""
        try:
            headers = []
            thead = soup.find("thead")
            if not thead:
                self.logger.warning("No thead element found")
                return headers

            header_row = thead.find("tr")
            if not header_row:
                self.logger.warning("No header row found in thead")
                return headers

            for th in header_row.find_all("th"):
                header_text = th.text.strip()
                if header_text:  # Only add non-empty headers
                    headers.append(header_text)

            return headers
        except Exception as e:
            self.logger.error(f"Error extracting table headers: {e}")
            return []

    def _extract_table_rows(self, soup, headers):
        """Extract table rows data from soup object"""
        try:
            all_rows_data = []
            table_body = soup.find("tbody")

            if not table_body:
                self.logger.warning("No tbody element found")
                return all_rows_data

            for row in table_body.find_all("tr"):
                row_data = {}
                cells = row.find_all("td")

                for i, cell in enumerate(cells):
                    if i < len(headers):  # Safety check
                        header_name = headers[i]
                        if header_name == "Action":
                            # Extract action buttons/images
                            actions = [img["alt"] for img in cell.find_all("img") if img.has_attr("alt")]
                            row_data[header_name] = actions
                        else:
                            row_data[header_name] = cell.text.strip()

                if row_data:  # Only add non-empty rows
                    all_rows_data.append(row_data)

            return all_rows_data
        except Exception as e:
            self.logger.error(f"Error extracting table rows: {e}")
            return []

    def get_user_by_email(self, email=""):
        """Get user index by email address"""
        try:
            data = self.get_users_data()
            for index, user in enumerate(data):
                if user.get("Email") == email:
                    user_index = index - 1
                    return user_index
            return -1
        except Exception as e:
            self.logger.error(f"Error getting user by email: {e}")
            return False

    def get_user_by_index(self, user_index=0):
        """Get user data by index"""
        try:
            data = self.get_users_data()
            index = user_index + 1
            if index < len(data):
                return data[index]
            self.logger.error(f"User index {index} out of range")
            return None
        except Exception as e:
            self.logger.error(f"Error getting user by index: {e}")
            return None

    def get_index_admin(self):
        """Get index of first admin user"""
        try:
            data = self.get_users_data()
            for index, user in enumerate(data):
                if user.get("Is admin") == "Admin":
                    return index - 1
            return -1
        except Exception as e:
            self.logger.error(f"Error getting admin index: {e}")
            return -1

    def get_index_user(self):
        """Get index of first regular user (skip index 0)"""
        try:
            data = self.get_users_data()
            for index, user in enumerate(data):
                if index == 0:
                    continue
                if user.get("Is admin") == "":
                    return index
            return -1
        except Exception as e:
            self.logger.error(f"Error getting user index: {e}")
            return -1

    # ========================================================================
    # Status Toggle Operations
    # ========================================================================
    def _toggle_user_status(self, target_status: str, action: bool, user_index: int = 0) -> bool:
        """
        Base method để toggle user status

        Args:
            target_status: 'on' hoặc 'off'
            action: True để confirm, False để cancel
        """
        try:
            switch_elements = self.find_elements(self.users_locators.switch_inner)
            if user_index >= len(switch_elements):
                self.logger.error(f"Switch element not found for user index: {user_index}")
                return False

            current_status = switch_elements[user_index].text.strip()
            self.logger.info(f"Current status: {current_status}")

            # Kiểm tra có cần toggle không
            needs_toggle = (target_status.lower() == "on" and current_status == "OFF") or (target_status.lower() == "off" and current_status == "ON")

            if not needs_toggle:
                self.logger.info(f"User already in target state: {current_status}")
                return False

            # Click toggle switch
            switch_buttons = self.find_elements(self.users_locators.btn_switch)
            if user_index >= len(switch_buttons):
                self.logger.error(f"Switch button not found for user index: {user_index}")
                return False

            switch_buttons[user_index].click()

            # Confirm hoặc cancel
            if action:
                self.wait_for_clickable(self.base_locators.btn_yes)
                self.click(self.base_locators.btn_yes)
                action_text = "activated" if target_status.lower() == "on" else "deactivated"
                self.logger.info(f"User {action_text} successfully")
            else:
                self.wait_for_clickable(self.base_locators.btn_no)
                self.click(self.base_locators.btn_no)
                self.logger.info("User toggle action cancelled")
            sleep(3)
            return True

        except Exception as e:
            self.logger.error(f"Failed to toggle user status: {e}")
            return False

    def toggle_user_status_success(self, target_status: str, user_index=0) -> bool:
        """Toggle user status với confirmation"""
        return self._toggle_user_status(target_status, action=True, user_index=user_index)

    def toggle_user_status_fail(self, target_status: str, user_index=0) -> bool:
        """Toggle user status với cancellation"""
        return self._toggle_user_status(target_status, action=False, user_index=user_index)

    # ========================================================================
    # File Operations
    # ========================================================================
    def import_file(self, page="users", file_name="users_success.xlsx"):
        self.click(self.users_locators.btn_thao_tac_excel)
        self.wait_for_clickable(self.users_locators.btn_import)
        self.click(self.users_locators.btn_import)

        self.upload_file(locator=self.base_locators.file_input_locator, page=page, file_name=file_name)

    def export_file_users(self, page="users", file_name="export.xlsx"):
        self.wait_for_clickable(self.users_locators.btn_thao_tac_excel).click()
        self.wait_for_clickable(self.users_locators.btn_export).click()
        sleep(1)
        return self.export_file(page=page, file_name=file_name)

    def download_sample_file_users(self, page="users", file_name="sample_data_users.xlsx"):
        self.click(self.users_locators.btn_thao_tac_excel)
        self.wait_for_clickable(self.users_locators.btn_download_sample_data).click()
        sleep(1)
        return self.export_file(page=page, file_name=file_name)

    def verify_export_download(self, file_name="export.xlsx"):
        export_path = r"C:\Users\BASEBS\OneDrive\Desktop\base\CRM_selenium_framework\pages\users\export_file"
        return self.verify_file_downloaded(download_path=str(export_path), file_name=file_name)

    # ========================================================================
    # Additional wrapper methods for file operations
    # ========================================================================
    def upload_file(self, locator, page="users", file_name=""):
        """Wrapper for BaseActions upload_file method"""
        return self.base_actions.upload_file(locator, page, file_name)

    def export_file(self, page="users", file_name="export.xlsx"):
        """Wrapper for BaseActions export_file method"""
        return self.base_actions.export_file(page, file_name)

    def verify_file_downloaded(self, download_path="", file_name=""):
        """Wrapper for BaseActions verify_file_downloaded method"""
        return self.base_actions.verify_file_downloaded(download_path, file_name)
