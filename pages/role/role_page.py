"""
Template Page - Customize operations theo page cụ thể
Copy file này và đổi tên thành {page_name}page.py
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, List, Dict, Any
import logging

from pages.base.base_page import BasePage
from pages.role.role_locators import RoleLocators

logger = logging.getLogger(__name__)


class RolePage(BasePage):
    """
    Chứa các operations cơ bản cho page
    """

    def __init__(self, driver):
        """Initialize template page"""
        super().__init__(driver)
        self.role_locators = RoleLocators()
        logger.info("role page initialized")

