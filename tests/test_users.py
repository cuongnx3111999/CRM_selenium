# tests/test_users.py
import pytest
from time import sleep
from pathlib import Path

from pages.users.users_locators import UsersLocators
from pages.base.base_locators import BaseLocators
from conftest import shared_driver
from pages.users.users_actions import UsersActions
from utils.logger import Logger
from utils.pytest_data_helpers import (
    filter_by_test_function,
    excel_data_provider,
)
from config.settings import Settings

project_root = Path(__file__).parent.parent
path_file = project_root / "pages" / "users" / "export_file"
Settings.DOWNLOAD_PATH = path_file


@pytest.mark.usefixtures("shared_driver", "auto_login")
@pytest.mark.users
class TestUsers:
    """Test cases cho tính năng users"""

    def setup_method(self):
        """Setup before each test method."""
        self.logger = Logger.get_logger(self.__class__.__name__)

    def teardown_method(self):
        """Cleanup after each test method."""
        self.logger.info("Test method completed")

    def _cleanup_existing_user(self, users_actions, email):
        """Helper method để cleanup user nếu đã tồn tại"""
        user_index = users_actions.users_page.get_user_by_email(email)
        if user_index >= 0:
            users_actions.select_user_type(to_admin=False, user_index=user_index)
            users_actions.users_page.toggle_user_status_success("OFF", user_index=user_index)
            users_actions.delete_user(user_index=user_index)

    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_add_admin_success"))
    def test_add_admin_success(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)
            users_actions.nav_to_users()
            # Cleanup existing user if exists
            self._cleanup_existing_user(users_actions, test_data["email"])
            users_actions.add_user(
                test_data=test_data,
                is_admin=True,
            )
            # assert "success" in users_actions.get_notice_message(), "Thông báo thành công không xuất hiện."
            sleep(2)
            new_user = users_actions.users_page.get_user_by_index(0)
            assert new_user["Email"] == test_data["email"], "Tạo user thất bại"
            self.logger.info("Create new user successfully")

            # users_actions.select_user_type(to_admin=False)
            # new_user = users_actions.users_page.get_user_by_index(0)
            # sleep(2)
            # assert new_user["Is admin"] == "", "Edit admin to user FAIL"

        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    def test_change_password(self, shared_driver):
        try:
            users_actions = UsersActions(shared_driver)
            assert users_actions.change_password(), "change password fail"
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    def test_switch_active(self, shared_driver):
        try:
            users_actions = UsersActions(shared_driver)

            index_admin = users_actions.users_page.get_index_admin()
            if index_admin >= 0:
                users_actions.switch_active_user_success(user_index=index_admin)
                current_user = users_actions.users_page.get_user_by_index(index_admin)
                assert current_user["Active"] == "ON", f"Có thể inactive của admin {current_user['Name']}"

            user_index = users_actions.users_page.get_index_user()
            if index_admin >= 0:
                current_active = users_actions.users_page.get_user_by_index(user_index)["Active"]
                users_actions.switch_active_user_fail(user_index=user_index)
                assert users_actions.users_page.get_user_by_index(user_index)["Active"] == current_active, f"switch active user fail"
                users_actions.switch_active_user_success(user_index=user_index)
                assert users_actions.users_page.get_user_by_index(user_index)["Active"] != current_active, f"switch active user fail"
                users_actions.switch_active_user_success(user_index=user_index)
                assert users_actions.users_page.get_user_by_index(user_index)["Active"] == current_active, f"switch active user fail"
            else:
                self.logger.error("khong tim thay user nao")

        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_validate_fields_add_user")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_add_user_success"))
    def test_add_user_success(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)

            # Cleanup existing user if exists
            self._cleanup_existing_user(users_actions, test_data["email"])

            users_actions.add_user(test_data=test_data)
            # assert "success" in users_actions.get_notice_message(), "Thông báo thành công không xuất hiện."
            sleep(2)
            new_user = users_actions.users_page.get_user_by_index(0)
            assert new_user["Email"] == test_data["email"], "Tạo user thất bại"

            self.logger.info("Create new user successfully")
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_delete_user_fail")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_add_user_success"))
    def test_add_user_fail(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)

            # Cleanup existing user if exists
            self._cleanup_existing_user(users_actions, test_data["email"])

            users_actions.add_user(
                test_data=test_data,
                action=False,
            )

            sleep(2)
            new_user = users_actions.users_page.get_user_by_index(0)
            assert new_user["Email"] != test_data["email"], "cancel tao user thất bại"

            self.logger.info("Cancel new user successfully")
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_delete_user_fail")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("validate_fields_add_user"))
    def test_validate_fields_add_user(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)

            # Cleanup existing user if exists
            try:
                self._cleanup_existing_user(users_actions, test_data["email"])
            except Exception as e:
                users_actions.logger.info(e)

            users_actions.users_page.wait_for_clickable(UsersLocators.btn_add_user)
            users_actions.users_page.click(UsersLocators.btn_add_user)
            sleep(1)

            modal_title = users_actions.get_visible_modal_title()
            if modal_title == "Create new user":
                assert users_actions.validation_field(
                    test_data=test_data,
                    field=test_data["field"],
                    expected_message=test_data["expected_message"],
                ), f"validate fields add user {test_data['expected_message']} fail"
            else:
                assert False, "Invalidate fields add user but can save"

            # assert users_actions.get_visible_modal_title() == "Create new user", "Create new user form not visible."
            users_actions.click_cancel()
            sleep(1)
            new_user = users_actions.users_page.get_user_by_index(0)
            assert new_user["Email"] != test_data["email"], "Tạo user thành công trong testcase add_user_failure "
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_edit_user_name_success"))
    def test_edit_user_name_success(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)
            users_actions.edit_user(test_data)

            # Construct expected fullname
            fullname = test_data["last_name"] + " " + test_data["middle_name"] + " " + test_data["first_name"]
            sleep(5)
            edit_user = users_actions.users_page.get_user_by_index(0)
            assert edit_user["Name"] == fullname, f"Tên người dùng không khớp. Kỳ vọng: '{fullname}', Thực tế: '{edit_user["Name"]}'"
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_edit_user_name_success"))
    def test_edit_user_name_fail(self, shared_driver, test_data):
        try:
            test_data["first_name"] = test_data["first_name"] + " fail "
            users_actions = UsersActions(shared_driver)
            users_actions.edit_user(test_data=test_data, action=False)

            # Construct expected fullname
            fullname = test_data["last_name"] + " " + test_data["middle_name"] + " " + test_data["first_name"]
            edit_user = users_actions.users_page.get_user_by_index(0)
            sleep(1)
            assert edit_user["Name"] != fullname, f"edit user thanh cong trong testcase fail {edit_user['Name']}'"
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_edit_user_role_reportto_success"))
    def test_edit_user_role_reportto_success(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)
            users_actions.edit_user(test_data=test_data)
            sleep(3)
            edit_user = users_actions.users_page.get_user_by_index(0)
            assert (
                edit_user["User role"] == test_data["roles"]
            ), f"Role người dùng không khớp. Kỳ vọng: '{test_data["roles"]}', Thực tế: '{edit_user["User role"]}'"
            assert " ".join(edit_user["Report to"].split()) in " ".join(
                test_data["report_to"].split()
            ), f"Report to người dùng không khớp. Kỳ vọng: '{test_data["report_to"]}', Thực tế: '{edit_user["Report to"]}'"
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_admin_success")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("test_edit_user_validate"))
    def test_edit_user_validate(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)

            users_actions.users_page.wait_for_clickable(BaseLocators.btn_icon_edit).click()

            users_actions.validation_field(
                test_data=test_data,
                field=test_data["field"],
                expected_message=test_data["expected_message"],
            )

            assert users_actions.get_visible_modal_title() == "Edit user", f"Tên người dùng có thể bị bỏ trống"
            users_actions.click_cancel()
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_delete_user_fail")
    @excel_data_provider("datatest_users.xlsx", filter_func=filter_by_test_function("delete_user_success"))
    def test_delete_user_success(self, shared_driver, test_data):
        try:
            users_actions = UsersActions(shared_driver)

            # Check if user exists
            if users_actions.users_page.get_user_by_email(test_data["email"]) == -1:
                users_actions.logger.info(f"Không tìm thấy {test_data['email']}")
                return

            index_user_will_delete = users_actions.users_page.get_user_by_email(test_data["email"])

            # Convert admin to user if needed
            if users_actions.users_page.get_user_by_index(users_actions.users_page.get_user_by_email(test_data["email"]))["Is admin"] == "Admin":
                users_actions.select_user_type(to_admin=False)

            users_actions.users_page.toggle_user_status_success(target_status="off", user_index=index_user_will_delete)

            sleep(2)
            current_user = users_actions.users_page.get_user_by_index(index_user_will_delete)
            users_actions.delete_user(user_index=index_user_will_delete)
            # assert "success" in users_actions.get_notice_message(), f"Delete that bai {users_actions.get_notice_message()}"

            assert users_actions.users_page.get_user_by_index(index_user_will_delete) != current_user, "Delete user fail"

        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_add_user_success")
    def test_delete_user_fail(self, shared_driver, test_data):
        try:
            print(Settings.DOWNLOAD_PATH)
            users_actions = UsersActions(shared_driver)

            # Check if user exists
            index_user_will_delete = 0

            # Convert admin to user if needed
            if users_actions.users_page.get_user_by_index(index_user_will_delete)["Is admin"] == "Admin":
                users_actions.select_user_type(to_admin=False)

            users_actions.users_page.toggle_user_status_success(target_status="off", user_index=index_user_will_delete)

            sleep(2)
            current_user = users_actions.users_page.get_user_by_index(index_user_will_delete)
            users_actions.delete_user(user_index=index_user_will_delete, action=False)
            assert users_actions.users_page.get_user_by_index(index_user_will_delete) == current_user, "Cancel Delete user fail"
            current_user = users_actions.users_page.get_user_by_index(index_user_will_delete)
            users_actions.delete_user(user_index=index_user_will_delete, action=True, confirm_action=False)
            assert users_actions.users_page.get_user_by_index(index_user_will_delete) == current_user, "Cancel confirm action Delete user fail"
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            raise

    @pytest.mark.dependency(name="TestUsers::test_delete_user_fail")
    def test_import_file(self, shared_driver):
        users_actions = UsersActions(shared_driver)
        file_name = "users_success.xlsx"
        users_actions.users_page.import_file(file_name=file_name)
        assert "import" in users_actions.get_notice_message(), "Import fail"

    # @pytest.mark.dependency(name="TestUsers::test_delete_user_fail")
    # def test_export_file(self, shared_driver):
    #     users_actions = UsersActions(shared_driver)
    #
    #     file_name = "export.xlsx"
    #     users_actions.users_page.export_file_users(page="users", file_name=file_name)
    #     sleep(5)
    #     assert users_actions.users_page.verify_export_download(file_name=file_name), "Export fail"
    #
    # @pytest.mark.dependency(name="TestUsers::test_export_file")
    # def test_download_sample_file(self, shared_driver):
    #     users_actions = UsersActions(shared_driver)
    #
    #     file_name = "sample_data_users.xlsx"
    #     users_actions.users_page.download_sample_file_users(page="users", file_name=file_name)
    #     sleep(3)
    #     assert users_actions.users_page.verify_export_download(file_name=file_name), "Download sample data users fail"
    #     users_actions.clear_folder_files(str(path_file), file_extensions=[".xlsx"])
