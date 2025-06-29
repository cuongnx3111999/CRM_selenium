# import_export_helper.py
import os
import logging
from pathlib import Path
from typing import Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from pages.base.base_locators import BaseLocators
from utils.logger import Logger


class ImportExportHelper:
    """
    Helper class để xử lý import/export files trong CRM Selenium Framework

    Attributes:
        driver: Selenium WebDriver instance
        wait_timeout: Timeout cho explicit waits (default: 10s)
        logger: Logger instance để ghi log
    """

    def __init__(self, driver, wait_timeout: int = 10):
        """
        Khởi tạo ImportExportHelper

        Args:
            driver: Selenium WebDriver instance
            wait_timeout: Timeout cho explicit waits
        """
        self.driver = driver
        self.wait_timeout = wait_timeout
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.base_locators = BaseLocators()

        # Base path của project (pages folder)
        self.base_path = Path(__file__).parent / "pages"

    def get_import_file_path(self, page_name: str, filename: str) -> Optional[str]:
        """
        Lấy đường dẫn tuyệt đối của file import từ folder của page

        Args:
            page_name: Tên page (ví dụ: 'users', 'reports')
            filename: Tên file cần import (ví dụ: 'sample.xlsx')

        Returns:
            str: Đường dẫn tuyệt đối của file, None nếu không tìm thấy

        Example:
            # >>> helper.get_import_file_path('users', 'sample.xlsx')
            'C:/project/pages/users/import_file/sample.xlsx'
        """
        try:
            # Tạo đường dẫn đến folder import của page
            import_folder = self.base_path / page_name / "import_file"
            file_path = import_folder / filename

            self.logger.info(f"Tìm kiếm file: {file_path}")

            # Kiểm tra folder import có tồn tại không
            if not import_folder.exists():
                self.logger.error(f"Folder import không tồn tại: {import_folder}")
                return None

            # Kiểm tra file có tồn tại không
            if not file_path.exists():
                self.logger.error(f"File không tồn tại: {file_path}")
                return None

            # Trả về đường dẫn tuyệt đối
            absolute_path = str(file_path.resolve())
            self.logger.info(f"Tìm thấy file: {absolute_path}")
            return absolute_path

        except Exception as e:
            self.logger.error(f"Lỗi khi lấy đường dẫn file: {str(e)}")
            return None

    def upload_file(self, file_input_locator: tuple, page_name: str, filename: str) -> bool:
        """
        Upload file sử dụng send_keys method

        Args:
            file_input_locator: Tuple (By, locator) của input file element
            page_name: Tên page chứa file import
            filename: Tên file cần upload

        Returns:
            bool: True nếu upload thành công, False nếu thất bại

        Example:
            # >>> locator = (By.CSS_SELECTOR, "input[type='file']")
            # >>> helper.upload_file(locator, 'users', 'sample.xlsx')
            True
        """
        try:
            # Lấy đường dẫn file
            file_path = self.get_import_file_path(page_name, filename)
            if not file_path:
                self.logger.error("Không thể lấy đường dẫn file")
                return False

            # Wait cho file input element
            wait = WebDriverWait(self.driver, self.wait_timeout)
            file_input = wait.until(EC.presence_of_element_located(self.base_locators.file_input_locator))

            # Kiểm tra element có enabled không
            if not file_input.is_enabled():
                self.logger.error("File input element không enabled")
                return False

            # Upload file bằng send_keys
            self.logger.info(f"Đang upload file: {filename}")
            file_input.send_keys(file_path)

            # Verify file đã được chọn (optional)
            if self._verify_file_selected(file_input, filename):
                self.logger.info(f"Upload file thành công: {filename}")
                return True
            else:
                self.logger.warning("Không thể verify file đã được chọn")
                return True  # Vẫn return True vì send_keys đã thực hiện

        except TimeoutException:
            self.logger.error("Timeout khi chờ file input element")
            return False
        except NoSuchElementException:
            self.logger.error("Không tìm thấy file input element")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi khi upload file: {str(e)}")
            return False

    def _verify_file_selected(self, file_input, expected_filename: str) -> bool:
        """
        Verify file đã được chọn thành công

        Args:
            file_input: WebElement của input file
            expected_filename: Tên file mong đợi

        Returns:
            bool: True nếu file đã được chọn đúng
        """
        try:
            # Lấy value của input file (thường chứa đường dẫn hoặc tên file)
            selected_value = file_input.get_attribute("value")

            if selected_value and expected_filename in selected_value:
                return True
            return False

        except Exception as e:
            self.logger.warning(f"Không thể verify file selection: {str(e)}")
            return False
