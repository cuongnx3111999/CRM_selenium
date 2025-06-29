from selenium.webdriver.common.by import By


class UsersLocators:
    # --- Main Buttons & Actions ---
    btn_users = (By.XPATH, "//div[@class='title' and text()='Users']")
    btn_add_user = (By.XPATH, "//span[text()='+ Add user']")
    btn_thao_tac_excel = (By.XPATH, "//span[text()='Thao tác với Excel ']")

    # --- User Form Fields ---
    first_name = (By.CSS_SELECTOR, "#first_name")
    last_name = (By.CSS_SELECTOR, "#last_name")
    middle_name = (By.CSS_SELECTOR, "#middle_name")
    email = (By.CSS_SELECTOR, "#email")
    verify_password = (By.CSS_SELECTOR, "#verify_password")
    verify_password_help = (By.CSS_SELECTOR, "#verify_password_help")
    select_role = (
        By.XPATH,
        "//label[normalize-space(text())='Role']" "/ancestor::div[contains(@class, 'ant-form-item')]" "//div[contains(@class, 'ant-select')]",
    )

    select_role_value = (By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@id='roles']]//span[@class='ant-select-selection-item']")
    select_report_to = (
        By.XPATH,
        "//label[normalize-space(text())='Report to']" "/ancestor::div[contains(@class, 'ant-form-item')]" "//div[contains(@class, 'ant-select')]",
    )

    select_report_value = (By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@id='report_to']]//span[@class='ant-select-selection-item']")
    select_transfer_to = (
        By.XPATH,
        "//label[normalize-space(text())='Transfer data to']"
        "/ancestor::div[contains(@class, 'ant-form-item')]"
        "//div[contains(@class, 'ant-select')]",
    )

    # --- Form Field Error Messages ---
    first_name_error = (By.CSS_SELECTOR, "#first_name_help")
    middle_name_error = (By.CSS_SELECTOR, "#middle_name_help")
    last_name_error = (By.CSS_SELECTOR, "#last_name_help")
    email_error = (By.CSS_SELECTOR, "#email_help")
    role_error = (By.CSS_SELECTOR, "#roles_help")
    report_to_error = (By.CSS_SELECTOR, "#report_to_help")
    transfer_to_error = (By.CSS_SELECTOR, "#transfer_help")

    # --- Radio Buttons & Toggles ---
    radio_admin_user = (By.XPATH, "(//span[@class='ant-radio-inner'])")
    radio_user = (By.XPATH, "//input[@type='radio'  and @value='user']")
    radio_admin = (By.XPATH, "//input[@type='radio' and @value='admin']")
    btn_switch = (By.CSS_SELECTOR, ".ant-switch")
    switch_inner = (By.CSS_SELECTOR, ".ant-switch-inner")

    # --- Action Icons in User List ---
    btn_edit = (By.CSS_SELECTOR, 'img[alt="edit"]')
    btn_change_password = (
        By.CSS_SELECTOR,
        '.users__WrapAction-sc-12srhl-5 img[alt="changePass"]',
    )
    btn_delete = (By.CSS_SELECTOR, '.users__WrapAction-sc-12srhl-5 img[alt="delete"]')

    role_LV3 = (By.XPATH, "//div[@class='ant-select-item-option-content' and contains(., 'LV3')]")

    btn_excel = (By.XPATH, "//button[contains(@class, 'users__ButtonExcel-sc-12srhl-10')]")
    btn_export = (By.XPATH, "//span[text()='Export users']")
    btn_import = (By.XPATH, "//span[text()='Import users']")
    btn_download_sample_data = (By.XPATH, "//span[text()='Generate sample data']")
    btm_view_logs = (By.XPATH, "//span[text()='View logs']")
