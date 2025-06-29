from selenium.webdriver.common.by import By


class RoleLocators:
    role_icon = (By.XPATH, "//img[@alt='user.icon' and contains(@src, 'RoleSetting')]")
    lv3_span = (By.XPATH, "//span[contains(@class, 'ant-typography') and text()='LV3']")
    add_role_icon = (By.XPATH, "//img[@alt='add' and contains(@src, 'PlusRoles')]")
    edit_role_icon = (By.XPATH, "//img[@alt='edit' and contains(@src, 'EditRoles')]")
    delete_role_icon = (By.XPATH, "//img[@alt='delete' and contains(@src, 'DeleteRoles')]")
    label_all_users = (By.XPATH, "//label[contains(@class, 'ant-radio-wrapper') and .//span[text()='All users']]")
    label_same_subordinate = (By.XPATH, "//label[contains(@class, 'ant-radio-wrapper') and .//span[contains(text(), 'Users having same roles and subordinate roles')]]")
    label_subordinate = (By.XPATH, "//label[contains(@class, 'ant-radio-wrapper') and .//span[contains(text(), 'Users having subordinate roles')]]")
    # privileges_select=(By.CSS_SELECTOR,"#privileges")
    privileges_select = (By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@id='privileges']]")