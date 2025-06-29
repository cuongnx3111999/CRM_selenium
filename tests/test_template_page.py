# tests/test_template.py
import pytest
from time import sleep
from pathlib import Path

from pages.template_page.template_locators import TemplateLocators
from pages.base.base_locators import BaseLocators
from conftest import shared_driver
from pages.template_page.template_actions import TemplateActions
from utils.logger import Logger
from utils.pytest_data_helpers import (
    filter_by_test_function,
    excel_data_provider,
)
from config.settings import Settings

project_root = Path(__file__).parent.parent
path_file = project_root / "pages" / "template" / "export_file"
Settings.DOWNLOAD_PATH = path_file


@pytest.mark.usefixtures("shared_driver", "auto_login")
@pytest.mark.template
class TestTemplate:
    """Test cases cho tính năng template"""

    def setup_method(self):
        """Setup before each test method."""
        self.logger = Logger.get_logger(self.__class__.__name__)

    def teardown_method(self):
        """Cleanup after each test method."""
        self.logger.info("Test method completed")