# pages/template_page/template_actions.py
"""template actions containing business logic and workflows."""
from time import sleep
from selenium.webdriver.common.by import By

from ..base.base_actions import BaseActions
from utils.logger import Logger


class TemplateActions(BaseActions):
    """Actions class for template business logic and workflows."""

    def __init__(self, driver_manager):
        super().__init__(driver_manager)
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._template_page = None

    @property
    def template_page(self):
        """Lazy initialization of templatePage"""
        if self._template_page is None:
            from .template_page import templatePage

            self._template_page = templatePage(self.driver_manager)
        return self._template_page

    # def nav_to_template(self):
    #     self.page.click(self.template_page.template_locators.btn_template)