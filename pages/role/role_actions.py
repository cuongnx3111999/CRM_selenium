"""
role Actions - Customize workflows theo page cụ thể
Copy file này và đổi tên thành {page_name}actions.py
"""

import logging
from typing import Dict, Any, List, Optional
import time

from pages.role.role_page import RolePage
from pages.base.base_actions import BaseActions
from utils.logger import Logger# pages/role_page/role_actions.py
"""role actions containing business logic and workflows."""
from time import sleep
from selenium.webdriver.common.by import By

from ..base.base_actions import BaseActions
from utils.logger import Logger


class roleActions(BaseActions):
    """Actions class for role business logic and workflows."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._role_page = None

    @property
    def role_page(self):
        """Lazy initialization of rolePage"""
        if self._role_page is None:
            from .role_page import rolePage

            self._role_page = rolePage(self.driver_manager)
        return self._role_page

    # def nav_to_role(self):
    #     self.page.click(self.role_page.role_locators.btn_role)

class RoleActions(BaseActions):
    """
    Role Actions - chứa business logic workflows
    Customize các workflows theo page thực tế
    """

    def __init__(self,driver_manager):
        """Initialize role actions"""
        self._role_page = None
        super().__init__(driver_manager)
        self.logger = Logger.get_logger(self.__class__.__name__)

    @property
    def role_page(self) -> RolePage:
        """Lazy initialization of role page"""
        if self._role_page is None:
            self._role_page = RolePage(self.driver_manager)
        return self._role_page
    
    def nav_to_role_setting(self):
        self.page.click(self.role_page.role_locators.role_icon)

    def add_role(self,data_test):
        self.page.click(self.role_page.role_locators.lv3_span)
        self.page.click(self.role_page.role_locators.add_role_icon)
        self.auto_fill_form(data_test)
        self.page.click(self.role_page.role_locators.label_all_users)
        self.click_save()