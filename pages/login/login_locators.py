# pages/login/login_locators.py
"""Login page locators."""

from selenium.webdriver.common.by import By
from ..base.base_locators import BaseLocators


class LoginLocators(BaseLocators):
    """Locators specific to login page."""

    # Login form elements
    btn_login = (By.CSS_SELECTOR, "button.ant-btn.ant-btn-primary")
    username = (By.CSS_SELECTOR, "#basic_email")
    password = (By.CSS_SELECTOR, "#basic_pass")

    # Error messages
    errors_username = (By.CSS_SELECTOR, "#basic_email_help .ant-form-item-explain-error")
    errors_password = (By.CSS_SELECTOR, "#basic_pass_help .ant-form-item-explain-error")
