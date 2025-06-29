import sys
from pathlib import Path

# Thêm đường dẫn vào sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from pages.login.login_page import LoginPage
from pages.users.users_page import UsersPage
from pages.base.base_page import BasePage
from pages.base.base_locators import BaseLocators
from pages.login.login_locators import LoginLocators
from pages.login.login_actions import LoginActions
from pages.base.base_actions import BaseActions
from pages.users.users_actions import UsersActions
from pages.users.users_locators import UsersLocators
from pages.role.role_locators import RoleLocators
from pages.role.role_actions import RoleActions
from pages.role.role_page import RolePage
from selenium.webdriver.common.by import By
from utils.driver_manager import DriverManager
from config.settings import Settings
from time import sleep
from utils.import_export_helper import ImportExportHelper


Settings.HEADLESS = False

driver = DriverManager().get_driver()
base_page = BasePage(driver)
login_page = LoginPage(driver)
users_page = UsersPage(driver)
base_locators = BaseLocators()
login_locators = LoginLocators()
users_locators = UsersLocators()
base_action = BaseActions(driver)
login_action = LoginActions(driver)
users_actions = UsersActions(driver)
role_locators=RoleLocators
role_actions=RoleActions(driver)
role_page=RolePage(driver)




# username =
# password =
URL = Settings.BASE_URL
first_name = "aa"
middle_name = "bb"
last_name = "cc"
email = "cuongnew@gmail.com"
password = password
role = "LV4"
report_to = "n dddd (cuonglock@gmail.com)"


login_page.navigate_to_login_page()

login_action.login(username, password)
base_action.choose_language()

base_page.wait_for_clickable(base_locators.btn_setting).click()
base_page.wait_for_clickable(role_page.role_locators.role_icon).click()

base_page.click(role_page.role_locators.lv3_span)
base_page.click(role_page.role_locators.add_role_icon)
base_page.click(role_page.role_locators.privileges_select)

base_page.wait_for_clickable(role_page.role_locators.privileges_select)
base_page.find_element(base_page.wait_for_clickable(role_page.role_locators.privileges_select)).get_attribute("outerHTML")
a=(By.CSS_SELECTOR,"#privileges")
b=base_page.find_element(a)
b.get_attribute("outerHTML")