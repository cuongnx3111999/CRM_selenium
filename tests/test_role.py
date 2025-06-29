# tests/test_role.py
import pytest
from time import sleep
from pathlib import Path

from pages.role.role_locators import RoleLocators
from pages.base.base_locators import BaseLocators
from conftest import shared_driver
from pages.role.role_actions import RoleActions
from utils.logger import Logger
from utils.pytest_data_helpers import (
    filter_by_test_function,
    excel_data_provider,
)
from config.settings import Settings

project_root = Path(__file__).parent.parent
path_file = project_root / "pages" / "role" / "export_file"
Settings.DOWNLOAD_PATH = path_file


@pytest.mark.usefixtures("shared_driver", "auto_login")
@pytest.mark.role
class TestRole:
    """Test cases cho tính năng role"""

    def setup_method(self):
        """Setup before each test method."""
        self.logger = Logger.get_logger(self.__class__.__name__)

    def teardown_method(self):
        """Cleanup after each test method."""
        self.logger.info("Test method completed")

    @excel_data_provider("datatest_role.xlsx", filter_func=filter_by_test_function("test_add_role_success"))
    def test_add_role_success(self,shared_driver,test_data):
        try:
            role_actions = RoleActions(shared_driver)

            role_actions.nav_to_role_setting()
            role_actions.add_role(test_data)
            sleep(5)
        except Exception as e:
            self.logger.error(f"LỖI THỰC THI - Không thể hoàn thành test case: {e}")
            self.logger.debug(f"Dữ liệu đầu vào: {test_data}")
            raise


