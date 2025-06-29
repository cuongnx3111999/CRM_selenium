# pages/users/users_actions.py
"""Users actions containing business logic and workflows."""
from time import sleep
from selenium.webdriver.common.by import By

from ..base.base_actions import BaseActions
from utils.logger import Logger


class UsersActions(BaseActions):
    """Actions class for users business logic and workflows."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._users_page = None

    @property
    def users_page(self):
        """Lazy initialization of UsersPage"""
        if self._users_page is None:
            from .users_page import UsersPage

            self._users_page = UsersPage(self.driver_manager)
        return self._users_page

    def nav_to_users(self):
        self.page.click(self.users_page.users_locators.btn_users)
    # ========================================================================
    # User Management Workflows
    # ========================================================================
    def add_user(self, test_data, is_admin=False, action=True):
        """Add new user with provided information"""
        try:
            # Click add user button
            self.users_page.wait_for_clickable(self.users_page.users_locators.btn_add_user)
            self.users_page.click(self.users_page.users_locators.btn_add_user)

            # Fill user information
            self.auto_fill_form(test_data=test_data)
            if is_admin:
                self.users_page.find_element(self.users_page.users_locators.radio_admin).click()
            if action:
                self.click_save()
            else:
                self.click_cancel()

        except Exception as e:
            self.logger.error(f"Failed to add user: {e}")
            raise

    def edit_user(self, test_data, action=True, user_index=0):
        """Edit user information"""
        try:
            edit_buttons = self.users_page.find_elements(self.users_page.base_locators.btn_icon_edit)
            if user_index >= len(edit_buttons):
                self.logger.error(f"Edit button not found for index: {user_index}")
                return False

            self.users_page.wait_for_clickable(edit_buttons[user_index]).click()

            # Fill form fields if provided
            self.auto_fill_form(test_data=test_data)

            sleep(1)

            if action:
                self.click_save()
                self.logger.info("User successfully edited")
                return True
            else:
                self.click_cancel()
                self.logger.info("User editing cancelled")
                return True

        except Exception as e:
            self.logger.error(f"Failed to edit user: {e}")
            return False

    def delete_user(self, action: bool = True, confirm_action: bool = True, user_index=0):
        """Delete user with transfer to first available option"""
        try:
            # Validate user index
            users_data = self.users_page.get_users_data()
            if user_index < 0:
                self.logger.error(f"Invalid user index: {user_index}")
                return False

            user = users_data[user_index]
            user_email = user.get("Email", "Unknown")

            edit_button = self.users_page.find_elements(self.users_page.base_locators.btn_icon_edit)[user_index]

            parent_container = edit_button.find_element(By.XPATH, "./parent::div")
            delete_button = parent_container.find_element(By.XPATH, ".//img[@alt='delete']")

            delete_button.click()
            sleep(1)

            # Select transfer option
            transfer_select = self.users_page.wait_for_element(self.users_page.users_locators.select_transfer_to)
            if not transfer_select:
                self.logger.error("Transfer select element not found")
                return False

            transfer_select.click()

            first_option = self.users_page.wait_for_element(self.users_page.base_locators.option_first_child)
            if not first_option:
                self.logger.error("First transfer option not found")
                return False

            first_option.click()

            if action:
                self.click_save()
                if confirm_action:
                    self.users_page.wait_for_clickable(self.users_page.base_locators.btn_delete).click()
                    # Verify deletion
                    user_index = self.users_page.get_user_by_email(user["Email"])

                    if user_index == -1:
                        self.logger.info(f"User {user_email} deleted successfully")
                        return True
                    else:
                        self.logger.error(f"User {user_email} deletion failed {user_index}")
                        return False
                else:
                    sleep(2)
                    self.click_cancel()
                    sleep(2)
                    self.click_cancel()
                    self.logger.info("User deletion cancelled at confirmation step")
                    return True
            else:
                sleep(2)
                self.click_cancel()
                self.logger.info(f"User deletion cancelled: {user_email}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
            return False

    def select_user_type(self, to_admin: bool = False, action: bool = True, user_index=0):
        """Select user type (admin or regular user)"""
        try:
            edit_buttons = self.users_page.find_elements(self.users_page.base_locators.btn_icon_edit)
            if user_index >= len(edit_buttons):
                self.logger.error(f"Edit button not found for user index: {user_index}")
                return False

            edit_buttons[user_index].click()

            current_user = self.users_page.get_user_by_index(user_index)
            if not current_user:
                self.logger.error("Could not get current user data")
                self.click_cancel()
                return False

            current_is_admin = current_user.get("Is admin") == "Admin"

            if to_admin == current_is_admin:  # No change needed
                self.logger.info("User type already matches target, no change needed")
                self.click_cancel()
                return True

            sleep(2)

            if not to_admin:
                self.users_page.find_element(self.users_page.users_locators.radio_user).click()
                target_status = "User"
            else:
                self.users_page.find_element(self.users_page.users_locators.radio_admin).click()
                target_status = "Admin"

            if action:
                self.click_save()
                # Verify change
                updated_user = self.users_page.get_user_by_index(user_index + 1)
                if updated_user:
                    updated_is_admin = updated_user.get("Is admin") == "Admin"
                    if updated_is_admin == to_admin:
                        self.logger.info(f"Successfully changed user type to {target_status}")
                        return True
                    else:
                        self.logger.error(f"Failed to change user type to {target_status}")
                        return False
            else:
                self.click_cancel()
                self.logger.info(f"Cancelled changing user type to {target_status}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to select user type: {e}")
            return False

    # ========================================================================
    # Status Management Workflows
    # ========================================================================
    def _switch_active_user(self, user_index: int, expect_success: bool) -> bool:
        """
        Base method để switch user status

        Args:
            user_index: Index của user
            expect_success: True nếu expect thành công, False nếu expect thất bại
        """
        try:
            user = self.users_page.get_user_by_index(user_index)
            if not user:
                self.logger.error(f"User at index {user_index} not found")
                return False

            original_status = user.get("Active")
            user_email = user.get("Email", "Unknown")

            # Validate status
            if original_status not in ["ON", "OFF"]:
                self.logger.error(f"User {user_email} has invalid status: {original_status}")
                return False

            # Determine target action
            target_action = "off" if original_status == "ON" else "on"
            expected_final_status = "OFF" if original_status == "ON" else "ON"

            # Perform toggle (success hoặc fail)
            if expect_success:
                self.users_page.toggle_user_status_success(target_status=target_action, user_index=user_index)
            else:
                self.users_page.toggle_user_status_fail(target_status=target_action, user_index=user_index)
            sleep(1)

            # Verify result
            updated_user = self.users_page.get_user_by_index(user_index)
            if not updated_user:
                self.logger.error("Could not get updated user data")
                return False

            actual_status = updated_user.get("Active")

            if expect_success:
                # Expect status changed
                success = actual_status == expected_final_status
                if success:
                    self.logger.info(f"Successfully switched user {user_email}: {original_status} -> {actual_status}")
                else:
                    self.logger.error(f"Failed to switch user {user_email}: expected {expected_final_status}, got {actual_status}")
            else:
                # Expect status unchanged
                success = actual_status == original_status
                if success:
                    self.logger.info(f"User {user_email} status remained unchanged as expected: {original_status}")
                else:
                    self.logger.warning(f"User {user_email} status changed unexpectedly: {original_status} -> {actual_status}")

            sleep(1)
            return success

        except Exception as e:
            self.logger.error(f"Exception in switch user: {e}")
            return False

    def switch_active_user_success(self, user_index: int = 0) -> bool:
        """Switch user status và expect thành công"""
        return self._switch_active_user(user_index, expect_success=True)

    def switch_active_user_fail(self, user_index: int = 0) -> bool:
        """Switch user status và expect thất bại"""
        return self._switch_active_user(user_index, expect_success=False)

    # ========================================================================
    # Validation Workflows
    # ========================================================================
    def validation_field(
        self,
        test_data,
        field="first_name",
        expected_message="Please input",
    ):
        try:
            self.auto_fill_form(test_data)
            self.click_save()
            return self.auto_validate_field_error_form(test_data=test_data, field=field, expected_message=expected_message)
        except Exception as e:
            self.logger.error(f"Error in check_edit_validation_field: {e}")
            return False

    # ========================================================================
    # Password Management
    # ========================================================================
    def change_password(self, password="Abc123456789@"):
        self.users_page.wait_for_clickable(self.users_page.base_locators.btn_icon_change_pass).click()
        sleep(2)
        self.click_save()
        if (
            self.validate_field_error(
                self.users_page.base_locators.password,
                self.users_page.base_locators.password_help,
                expected_message="Please input",
            )
            == False
        ):
            self.logger.error(f"Password field error: {self.users_page.base_locators.password}")
            return False
        if (
            self.validate_field_error(
                self.users_page.base_locators.verify_password,
                self.users_page.base_locators.verify_password_help,
                expected_message="Please input",
            )
            == False
        ):
            self.logger.error(f"Verify password field error: {self.users_page.base_locators.verify_password}")
            return False

        self.users_page.send_keys(self.users_page.base_locators.password, text=password)
        self.users_page.send_keys(self.users_page.base_locators.verify_password, text=password + "abc")
        sleep(1)

        if "not match!" in self.users_page.get_text(self.users_page.base_locators.verify_password_help) == False:
            self.logger.error(f"Không verify password: {self.users_page.get_text(self.users_page.base_locators.verify_password_help)}")
            return False

        self.users_page.send_keys(self.users_page.base_locators.password, text=password)
        self.users_page.send_keys(self.users_page.base_locators.verify_password, text=password)

        self.click_save()
        return True
