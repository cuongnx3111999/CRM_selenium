from selenium.webdriver.common.by import By


class BaseLocators:
    # --- General ---
    notice = (By.CSS_SELECTOR, ".ant-notification-notice-description")
    icon_eye_invisible = (By.CSS_SELECTOR, ".ant-input-suffix")
    table_content = (By.CSS_SELECTOR, ".ant-table-content")
    modals = (By.CSS_SELECTOR, ".ant-modal-content")
    modal_title = (By.CSS_SELECTOR, ".ant-modal-title")
    select_box = (By.CSS_SELECTOR, ".ant-select-selection-item")

    modal_wrapper = (By.XPATH, "./ancestor::div[contains(@class, 'ant-modal')]")
    # --- Language Buttons ---
    btn_add_language = (By.CSS_SELECTOR, ".language_app")
    btn_vietnamese_language = (By.XPATH, "//*[contains(text(), 'Tiếng Việt')]")
    btn_english_language = (By.XPATH, "//*[contains(text(), 'English')]")

    # --- Common Action Buttons ---
    btn_save = (By.XPATH, "//button[.//span[text()='Save']]")
    btn_cancel = (By.XPATH, "//button[.//span[text()='Cancel']]")
    btn_yes = (By.XPATH, "//button[.//span[text()='Yes']]")
    btn_no = (By.XPATH, "//button[.//span[text()='No']]")
    btn_delete = (By.XPATH, "//button[.//span[text()='Delete']]")
    btn_icon_edit = (By.CSS_SELECTOR, 'img[alt="edit"]')
    btn_icon_change_pass = (By.CSS_SELECTOR, 'img[alt="changePass"]')
    btn_icon_delete = (By.CSS_SELECTOR, 'img[alt="delete"]')
    file_input_locator = (By.CSS_SELECTOR, "#file")

    btn_login = (By.CSS_SELECTOR, "button.ant-btn.ant-btn-primary")

    # --- Settings & Form Fields ---
    btn_setting = (By.CSS_SELECTOR, 'li[data-menu-id$="-settings"]')
    basic_password = (By.CSS_SELECTOR, "#basic_pass")
    password = (By.CSS_SELECTOR, "#password")
    password_help = (By.CSS_SELECTOR, "#password_help")
    verify_password = (By.CSS_SELECTOR, "#verify_password")
    verify_password_help = (By.CSS_SELECTOR, "#verify_password_help")

    # Opption
    option_first_child = (By.CSS_SELECTOR, ".ant-select-item.ant-select-item-option:nth-of-type(1)")
    option_second_child = (By.CSS_SELECTOR, ".ant-select-item.ant-select-item-option:nth-of-type(2)")
    option_report_to_com = (By.CSS_SELECTOR, ".ant-select-item.ant-select-item-option[title*='com']")
