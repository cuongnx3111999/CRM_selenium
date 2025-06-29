# pages/template/template_page.py
"""template page object model - Page Operations only."""
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from pages.base.base_page import BasePage
from pages.template_page.template_locators import TemplateLocators
from config.settings import Settings
from utils.logger import Logger

from bs4 import BeautifulSoup


class templatePage(BasePage):
    """Page Object for template page basic operations."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.template_locators = TemplateLocators
        self.template_timeout = Settings.EXPLICIT_WAIT
        self.template_url = Settings.BASE_URL
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