"""Base Actions class containing business logic and complex UI operations."""

import os
import time
from time import sleep
from typing import Optional, List
from pathlib import Path

import pygetwindow as gw
import pyautogui
import pyperclip
from selenium.webdriver.common.by import By

from utils.logger import Logger
from pages.base.base_page import BasePage


class BaseActions:
    """Base Actions class containing business logic and complex UI operations."""

    def __init__(self, driver_manager):
        self.driver_manager = driver_manager
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._page = None

    @property
    def page(self) -> BasePage:
        """Lazy initialization of BasePage"""
        if self._page is None:
            self._page = BasePage(self.driver_manager)
        return self._page

    # ========================================================================
    # COMMON UI METHODS - ENHANCED FOR ANT DESIGN
    # ========================================================================

    def get_notice_message(self) -> Optional[str]:
        """Get notice/alert message if displayed - sử dụng enhanced wait_for_element"""
        try:
            if self.page.is_displayed(self.page.wait_for_element(self.page.base_locators.notice)):
                return self.page.get_text(self.page.base_locators.notice)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get notice message: {e}")
            return None

    def click_by_text(self, button_text: str, index: int = 0, use_javascript: bool = False) -> bool:
        """
        Click button theo text với khả năng tùy chỉnh click method - sử dụng enhanced base_page

        Args:
            button_text: Text của button cần click ("Save", "Cancel", etc.)
            index: Index của button nếu có nhiều button cùng text (default=0)
            use_javascript: True để dùng JavaScript click, False để dùng normal click

        Returns:
            bool: True nếu click thành công, False nếu thất bại
        """
        try:
            # Sử dụng wait_for_clickable cải tiến từ base_page
            button = self.page.wait_for_clickable(
                (By.XPATH, f"//button[.//span[text()='{button_text}'] and ancestor::div[contains(@class, 'ant-modal-content')]]")
            )

            # Click button theo method được chỉ định
            if use_javascript:
                self.page.driver.execute_script("arguments[0].click();", button)
            else:
                self.page.click(button)

            self.logger.info(f"Clicked {button_text} button using {'JavaScript' if use_javascript else 'normal'} click")
            time.sleep(1)
            return True

        except Exception as e:
            self.logger.error(f"Error clicking {button_text} button: {e}")
            return False

    def click_save(self, index: int = 0) -> bool:
        """Click Save button - sử dụng click_by_text"""
        return self.click_by_text("Save", index=index, use_javascript=False)

    def click_cancel(self, index: int = 0) -> bool:
        """Click Cancel button - sử dụng click_by_text"""
        return self.click_by_text("Cancel", index=index, use_javascript=True)

    def choose_language(self, language: str = "English") -> None:
        """Select language from dropdown"""
        try:
            self.page.click(self.page.base_locators.btn_add_language)

            if language.lower() == "english":
                self.page.wait_for_clickable(self.page.base_locators.btn_english_language)
                self.page.click(self.page.base_locators.btn_english_language)
            else:
                self.page.wait_for_clickable(self.page.base_locators.btn_vietnamese_language)
                self.page.click(self.page.base_locators.btn_vietnamese_language)

            self.logger.info(f"Language set to: {language}")
        except Exception as e:
            self.logger.error(f"Failed to choose language '{language}': {e}")
            raise

    def get_visible_modal_title(self) -> str:
        """
        Trả về tiêu đề của modal đang hiển thị - sử dụng enhanced methods
        """
        try:
            # Sử dụng wait_for_element cải tiến
            modal = self.page.wait_for_element(self.page.base_locators.modals)

            title_elements = modal.find_elements(*self.page.base_locators.modal_title)
            if title_elements:
                return title_elements[0].text.strip()

            return ""
        except Exception as e:
            self.logger.error(f"Error getting modal title: {str(e)}")
            return ""

    # ========================================================================
    # VALIDATION HELPERS
    # ========================================================================

    def validate_field_error(
        self,
        field_locator,
        error_locator,
        expected_message: str = "Please input",
    ) -> bool:
        """
        Validate that empty field shows correct error message
        Args:
            field_locator: Field element locator
            error_locator: Error message element locator
            expected_message: Expected error message text
        Returns:
            bool: True if validation passes
        """
        try:
            self.logger.info(f"Validation passed: {field_locator}")
            actual_message = self.page.get_text(error_locator)
            if self.page.is_select_box_by_role(field_locator):
                expected_message = "Please select"
            is_valid = expected_message in actual_message
            if is_valid:
                self.logger.info(f"{field_locator} empty validation passed")
            else:
                self.logger.warning(f"{field_locator} validation failed. Expected: '{expected_message}', Got: '{actual_message}'")

            return is_valid

        except Exception as e:
            self.logger.error(f"{field_locator} validation failed: {e}")
            return False

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def upload_file(self, locator, page: str, file_name: str) -> None:
        project_root = Path(__file__).parent.parent

        path_file = project_root / page / "import_file" / file_name

        import_button = self.page.find_element(self.page.base_locators.file_input_locator)
        import_button.send_keys(str(path_file))
        self.click_save()

    def _handle_export_dialog(self, file_name: str, timeout: int = 10):
        """
        Xử lý dialog export với PyAutoGUI
        Args:
            file_name: Tên file cần save
            timeout: Thời gian chờ dialog xuất hiện (seconds)

        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            start_time = time.time()
            save_window = None

            while time.time() - start_time < timeout:
                windows = gw.getAllWindows()
                for window in windows:
                    if "save as" in window.title.lower() or "save" in window.title.lower():
                        save_window = window

                        break
                if save_window:
                    break
                time.sleep(0.5)

            if not save_window:
                pass

            save_window.activate()
            time.sleep(1)

            pyperclip.copy(file_name)

            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.3)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)

            pyautogui.hotkey("ctrl", "a")
            pyautogui.write(file_name)
            pyautogui.press("enter")

            return True

        except Exception as e:
            pass

    def export_file(self, page: str, file_name="export.xlsx", timeout: int = 10) -> bool:
        project_root = Path(__file__).parent.parent

        path_file = project_root / page / "export_file" / file_name
        return self._handle_export_dialog(file_name=str(path_file), timeout=timeout)

    def verify_file_downloaded(self, download_path: str, file_name: str, timeout: int = 30) -> bool:
        """
        Kiểm tra file đã được tải về thành công

        Args:
            download_path: Đường dẫn thư mục download
            file_name: Tên file cần kiểm tra
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            bool: True nếu file đã tồn tại, False nếu không
        """
        file_path = os.path.join(download_path, file_name)

        for _ in range(timeout):
            if os.path.exists(file_path):
                return True
            time.sleep(1)

        return False

    def show_download_files(self, download_path: str) -> None:
        """
        Hiển thị tất cả file trong thư mục download

        Args:
            download_path: Đường dẫn thư mục download
        """
        try:
            if not os.path.exists(download_path):
                print(f"Thư mục không tồn tại: {download_path}")
                return

            files = [f for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f))]

            print(f"Files trong {download_path}:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")

            if not files:
                print("(Không có file nào)")

        except Exception as e:
            print(f"Lỗi: {e}")

    def clear_folder_files(self, folder_path: str, file_extensions: Optional[List[str]] = None, delete_all_if_empty: bool = False) -> bool:
        """
        Xóa file trong folder với logic an toàn

        Args:
            folder_path: Đường dẫn folder cần clear
            file_extensions: Danh sách extension cần xóa
                            - None: xóa tất cả file
                            - []: không xóa gì (trừ khi delete_all_if_empty=True)
                            - ['.xlsx', '.csv']: chỉ xóa file có extension này
            delete_all_if_empty: True nếu muốn xóa tất cả khi file_extensions = []

        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            if not os.path.exists(folder_path):
                print(f"❌ Folder không tồn tại: {folder_path}")
                return False

            if not os.path.isdir(folder_path):
                print(f"❌ Đường dẫn không phải là folder: {folder_path}")
                return False

            all_items = os.listdir(folder_path)
            files_to_delete = []

            print(f"📁 Đang kiểm tra folder: {folder_path}")
            print(f"🔍 file_extensions: {file_extensions}")
            print(f"🗑️ delete_all_if_empty: {delete_all_if_empty}")

            for item in all_items:
                item_path = os.path.join(folder_path, item)

                if os.path.isfile(item_path):

                    if file_extensions is None:
                        files_to_delete.append((item, item_path))

                    elif len(file_extensions) > 0:
                        file_ext = os.path.splitext(item)[1].lower()
                        if file_ext in [ext.lower() for ext in file_extensions]:
                            files_to_delete.append((item, item_path))

                    elif len(file_extensions) == 0 and delete_all_if_empty:
                        files_to_delete.append((item, item_path))

            if not files_to_delete:
                print(f"📁 Không có file nào để xóa trong: {folder_path}")
                return True

            print(f"🗑️ Sẽ xóa {len(files_to_delete)} file:")
            for file_name, _ in files_to_delete:
                print(f"   - {file_name}")

            deleted_count = 0
            for file_name, file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"   ✅ Đã xóa: {file_name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"   ❌ Lỗi xóa {file_name}: {e}")

            print(f"🎉 Đã xóa thành công {deleted_count}/{len(files_to_delete)} file")
            return deleted_count == len(files_to_delete)

        except Exception as e:
            print(f"❌ Lỗi clear folder: {e}")
            return False

    def auto_fill_form(self, test_data, skip_empty: bool = True):
        """
        Tự động fill form dựa trên data từ CSV với logic separator và xử lý empty fields

        Args:
            test_data: Dict data từ CSV (1 row)
            skip_empty: True để bỏ qua field có giá trị "", False để xử lý bình thường

        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Validation input parameters
            if not isinstance(test_data, dict):
                self.logger.error("Data test phải là dictionary")
                return False

            if not isinstance(skip_empty, bool):
                self.logger.error("skip_empty phải là boolean")
                return False

            filled_count = 0
            skipped_count = 0
            total_fields = 0

            # Convert dict thành list để duy trì thứ tự
            items = list(test_data.items())

            # Tìm vị trí của field rỗng đầu tiên (separator)
            separator_index = -1
            for i, (field_name, field_value) in enumerate(items):
                if str(field_value) == "-1" or field_value is None:
                    separator_index = i
                    break

            if separator_index == -1:
                self.logger.warning("Không tìm thấy separator (field rỗng), sẽ xử lý tất cả fields")
                input_fields = items
            else:
                # Lấy các field sau separator làm input fields
                input_fields = items[separator_index + 1 :]

            self.logger.info(f"Auto filling form với data: {input_fields}")

            # Fill từng input field
            for field_name, field_value in input_fields:
                total_fields += 1

                # Kiểm tra empty field và skip_empty flag
                if field_value == "" and skip_empty:
                    skipped_count += 1
                    continue

                # Tạo CSS selector từ field name
                css_selector = f"#{field_name}"
                field_locator = (By.CSS_SELECTOR, css_selector)

                try:
                    # Tìm và fill field - sử dụng enhanced wait_for_element

                    element = self.page.find_element(field_locator)

                    if element:
                        if self.page.is_select_box_by_role(field_locator):
                            select_element = self.page.find_element(field_locator)
                            self.page.click(select_element)
                            sleep(1)


                            select_option=(By.XPATH, f"//div[contains(@title, '{field_value}')]")
                            # (By.XPATH, "//div[contains(@class, 'ant-select-selector') and .//input[@id='privileges']]")
                            role_option = self.page.wait_for_clickable(select_option,fast_mode=False)
                            self.page.click(role_option)
                        else:
                            # Clear field trước khi fill
                            self.page.clear_inputs(element)

                            self.page.send_keys(element, field_value)
                        self.logger.debug(f"✅ Filled {field_name} = {field_value}")

                        filled_count += 1
                    else:
                        self.logger.warning(f"❌ Field không tìm thấy: {field_name}")

                except Exception as e:
                    self.logger.warning(f"❌ Lỗi fill field {field_name}: {e}")
                    continue

            # Logging kết quả chi tiết
            processed_fields = filled_count
            self.logger.info(f"Kết quả: {processed_fields}/{total_fields} fields được xử lý")
            if skip_empty and skipped_count > 0:
                self.logger.info(f"Đã bỏ qua {skipped_count} empty fields")

            return processed_fields > 0

        except Exception as e:
            self.logger.error(f"Lỗi trong auto_fill_form: {e}")
            return False

    def auto_validate_field_error_form(self, test_data, field="", expected_message: str = "Please input"):
        """
        Tự động validate field error với logic separator và xử lý empty fields

        Args:
            test_data: Dict data từ CSV (1 row)
            field: Tên field cần validate
            expected_message: Message error mong đợi
            skip_empty: True để bỏ qua field có giá trị "", False để xử lý bình thường

        Returns:
            bool: True nếu validation thành công, False nếu thất bại
        """
        try:
            # Validation input parameters
            if not isinstance(test_data, dict):
                self.logger.error("Data test phải là dictionary")
                return False

            if field != "":
                skip_empty = True

            if not field:
                self.logger.error("Field name không được rỗng")
                return False

            items = list(test_data.items())

            # Tìm vị trí của field rỗng đầu tiên (separator)
            separator_index = -1
            for i, (field_name, field_value) in enumerate(items):
                if field_value == "-1" or field_value is None:
                    separator_index = i
                    break

            if separator_index == -1:
                input_fields = items
            else:
                # Lấy các field sau separator làm input fields
                input_fields = items[separator_index + 1 :]

            # Tìm field cần validate
            for field_name, field_value in input_fields:
                if field_name == field:
                    # Kiểm tra empty field và skip_empty flag
                    if field_value == "" and skip_empty:
                        return True  # Skip validation nhưng vẫn return True

                    # Thực hiện validation
                    css_selector = f"#{field_name}"
                    field_locator = (By.CSS_SELECTOR, css_selector)
                    css_selector_error = f"#{field_name}_help"
                    error_locator = (By.CSS_SELECTOR, css_selector_error)

                    if field_value == "":
                        self.logger.debug(f"🧹 Validating cleared field: {field_name}")
                    else:
                        self.logger.debug(f"✅ Validating field: {field_name} = {field_value}")

                    return self.validate_field_error(field_locator=field_locator, error_locator=error_locator, expected_message=expected_message)

            self.logger.warning(f"Field '{field}' không tìm thấy trong input_fields")
            return False

        except Exception as e:
            self.logger.error(f"Lỗi không thể validate: {e}")
            return False
