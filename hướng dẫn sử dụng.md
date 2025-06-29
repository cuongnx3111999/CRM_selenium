📚 CÁC NHÓM HÀM CHÍNH
1. NAVIGATION_FUNCTIONS (Điều hướng - BasePage)
python
# Mở trang web
page.open_url("https://example.com")

# Lấy tiêu đề trang
title = page.get_title()

# Lấy URL hiện tại
url = page.get_current_url()

# Làm mới trang
page.refresh_page()

# Quay lại trang trước
page.go_back()
2. ELEMENT_FINDING_FUNCTIONS (Tìm element - BasePage)
python
# Tìm element theo locator
element = page.find_element((By.ID, 'username'))

# Tìm nhiều element
buttons = page.find_elements((By.TAG_NAME, 'button'))

# Tìm theo text chính xác
save_btn = page.find_element_by_text('Save')

# Tìm theo text chứa
element = page.find_element_containing_text('User')

# Tìm button theo text
cancel_btn = page.find_button_by_text('Cancel')

# Tìm input theo placeholder
input_field = page.get_element_by_placeholder('Enter username')

# Tìm input theo placeholder một phần
input_field = page.get_element_by_partial_placeholder('Enter')
3. WAIT_FUNCTIONS (Chờ element - BasePage) - QUAN TRỌNG NHẤT
python
# Chờ element hiển thị (dùng nhiều nhất)
element = page.wait_for_element((By.ID, 'submit'))

# Chờ element có thể click (BẮT BUỘC trước khi click)
button = page.wait_for_clickable((By.ID, 'save-btn'))

# Chờ element biến mất
disappeared = page.wait_for_element_to_disappear((By.CLASS_NAME, 'loading'))
Tham số quan trọng:

timeout: Thời gian chờ (giây) - mặc định từ Settings

retry_count: Số lần thử lại - mặc định 1

fast_mode: True (nhanh) / False (cho Ant Design phức tạp)

4. INTERACTION_FUNCTIONS (Tương tác - BasePage)
python
# Click element (tự động thử 4 cách khác nhau)
page.click((By.ID, 'submit-btn'))

# Nhập text (tự động validate)
page.send_keys((By.ID, 'username'), 'admin')

# Xóa nội dung input
page.clear_inputs((By.ID, 'search-box'))

# Cuộn đến element
page.scroll_to_element((By.ID, 'footer'))
Tham số send_keys:

text: Text cần nhập

clear_first: True (xóa text cũ trước) / False

validate_input: True (kiểm tra nhập thành công) / False

max_retries: Số lần thử lại

5. VALIDATION_FUNCTIONS (Kiểm tra - BasePage)
python
# Kiểm tra element có tồn tại không
exists = page.is_element_present((By.ID, 'error-msg'))

# Kiểm tra element có hiển thị không
visible = page.is_displayed((By.ID, 'popup'))

# Kiểm tra element có enable không
enabled = page.is_enabled((By.ID, 'submit-btn'))

# Kiểm tra input có rỗng không
empty = page.is_field_empty((By.ID, 'username'))

# Kiểm tra có phải select box không (Ant Design)
is_select = page.is_select_box_by_role((By.ID, 'dropdown'))
6. DATA_EXTRACTION_FUNCTIONS (Lấy dữ liệu - BasePage)
python
# Lấy text hiển thị
message = page.get_text((By.CLASS_NAME, 'error'))

# Lấy giá trị attribute
value = page.get_attribute((By.ID, 'input'), 'value')
7. UTILITY_FUNCTIONS (Tiện ích - BasePage)
python
# Chụp màn hình
screenshot_path = page.take_screenshot('test_result')

# Chuyển cửa sổ browser
page.switch_to_window(handles[1])

# Lấy danh sách cửa sổ
handles = page.get_window_handles()
8. COMMON_UI_OPERATIONS (Thao tác UI chung - BaseActions)
python
# Lấy thông báo notice/alert
message = actions.get_notice_message()

# Click button theo text với nhiều tùy chọn
success = actions.click_by_text("Save", index=0, use_javascript=False)

# Click Save button (wrapper)
success = actions.click_save(index=0)

# Click Cancel button (wrapper)
success = actions.click_cancel(index=0)

# Chọn ngôn ngữ
actions.choose_language("English")  # hoặc "Vietnamese"

# Lấy tiêu đề modal đang hiển thị
title = actions.get_visible_modal_title()
9. VALIDATION_HELPERS (Hỗ trợ validation - BaseActions)
python
# Validate field error message
is_valid = actions.validate_field_error(
    field_locator=(By.ID, 'username'),
    error_locator=(By.ID, 'username_help'),
    expected_message="Please input"
)
10. FORM_AUTOMATION (Tự động hóa form - BaseActions) - QUAN TRỌNG NHẤT
python
# Tự động fill form từ data CSV
success = actions.auto_fill_form(
    test_data=csv_row_data,
    skip_empty=True
)

# Tự động validate field error
success = actions.auto_validate_field_error_form(
    test_data=csv_row_data,
    field="firstname",
    expected_message="Please input"
)
11. FILE_OPERATIONS (Xử lý file - BaseActions)
python
# Upload file
actions.upload_file(
    locator=(By.ID, 'file-input'),
    page="users",
    file_name="users_success.xlsx"
)

# Export file
success = actions.export_file(
    page="users",
    file_name="export.xlsx",
    timeout=10
)

# Verify file đã download
downloaded = actions.verify_file_downloaded(
    download_path="C:/Downloads",
    file_name="export.xlsx",
    timeout=30
)

# Xóa file trong folder
success = actions.clear_folder_files(
    folder_path="C:/Downloads",
    file_extensions=['.xlsx', '.csv']
)
🔥 PATTERN THƯỜNG DÙNG
Pattern Cơ Bản (90% trường hợp)
python
# 1. Chờ element có thể click (BasePage)
element = page.wait_for_clickable((By.ID, 'button'))

# 2. Click element (BasePage)
page.click(element)
Pattern Business Logic (BaseActions)
python
# 1. Fill form tự động
actions.auto_fill_form(test_data)

# 2. Save/Cancel
if save_action:
    actions.click_save()
else:
    actions.click_cancel()

# 3. Verify kết quả
message = actions.get_notice_message()
Pattern Validation (Kết hợp cả hai)
python
# 1. Fill form (có thể để trống một số field)
actions.auto_fill_form(test_data, skip_empty=False)

# 2. Click Save để trigger validation
actions.click_save()

# 3. Validate từng field error
is_valid = actions.auto_validate_field_error_form(
    test_data,
    field="firstname",
    expected_message="Please input"
)
Pattern File Operations (BaseActions)
python
# 1. Clear folder trước khi test
actions.clear_folder_files(download_path, ['.xlsx'])

# 2. Thực hiện export
actions.export_file("users", "test_export.xlsx")

# 3. Verify file downloaded
assert actions.verify_file_downloaded(download_path, "test_export.xlsx")
⚠️ LƯU Ý QUAN TRỌNG
BẮT BUỘC PHẢI NHỚ:
LUÔN dùng wait_for_clickable trước khi click (BasePage)

Dùng fast_mode=False cho Ant Design phức tạp (BasePage)

Hàm click tự động retry với 4 chiến lược khác nhau (BasePage)

CSV data phải có separator (-1 hoặc None) để phân biệt metadata và input data (BaseActions)

Auto detect select box - hệ thống tự nhận biết select vs input (BaseActions)

Mối quan hệ giữa BasePage và BaseActions:
BaseActions kế thừa và sử dụng BasePage qua self.page

Tất cả hàm BasePage đều có thể dùng qua actions.page.function_name()

BaseActions tập trung vào business logic, BasePage tập trung vào Selenium operations

Cấu trúc CSV data cho BaseActions:
text
test_name,expected_result,separator,firstname,lastname,email,role
"Add User Test","Success",-1,"John","Doe","john@example.com","Admin"
Cho Ant Design:
python
# Dùng enhanced mode cho component phức tạp
element = page.wait_for_clickable(locator, fast_mode=False, retry_count=2)