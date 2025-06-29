# utils/debug_helpers.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class ModalDebugger:
    @staticmethod
    def highlight_element(driver, element, duration=3, border_style="4px solid red"):
        """Highlight một element trên trang web"""

        def apply_style(style):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, style)

        original_style = element.get_attribute("style") or ""
        highlight_style = f"{original_style}; border: {border_style}; background-color: rgba(255, 255, 0, 0.3);"
        apply_style(highlight_style)
        time.sleep(duration)
        apply_style(original_style)

    @staticmethod
    def get_modal_title(modal_element):
        """Tìm title/tên của modal"""
        title_selectors = [
            ".modal-title",
            ".ant-modal-title",
            ".modal-header h1, .modal-header h2, .modal-header h3, .modal-header h4, .modal-header h5",
            "[class*='title']",
            "[class*='header'] h1, [class*='header'] h2, [class*='header'] h3",
            ".title",
            "h1, h2, h3, h4, h5",
            "[data-testid*='title']",
            "[aria-labelledby]",
        ]

        for selector in title_selectors:
            try:
                title_element = modal_element.find_element(By.CSS_SELECTOR, selector)
                if title_element.text.strip():
                    return title_element.text.strip()
            except NoSuchElementException:
                continue

        # Nếu không tìm thấy title, lấy text đầu tiên có nghĩa
        try:
            all_text = modal_element.text.strip()
            if all_text:
                # Lấy dòng đầu tiên không rỗng
                lines = [line.strip() for line in all_text.split("\n") if line.strip()]
                if lines:
                    return lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
        except:
            pass

        return "Không xác định được tên modal"

    @staticmethod
    def get_modal_content_summary(modal_element):
        """Lấy tóm tắt nội dung modal"""
        try:
            full_text = modal_element.text.strip()
            if not full_text:
                return "Modal không có text"

            # Loại bỏ các ký tự xuống dòng và khoảng trắng thừa
            clean_text = " ".join(full_text.split())

            # Cắt ngắn nếu quá dài
            if len(clean_text) > 200:
                return clean_text[:200] + "..."
            return clean_text
        except:
            return "Không thể đọc nội dung modal"

    @staticmethod
    def get_modal_buttons(modal_element):
        """Tìm các button trong modal"""
        button_selectors = ["button", ".btn", ".ant-btn", "[role='button']", "input[type='submit']", "input[type='button']"]

        buttons = []
        for selector in button_selectors:
            try:
                button_elements = modal_element.find_elements(By.CSS_SELECTOR, selector)
                for btn in button_elements:
                    if btn.is_displayed():
                        btn_text = btn.text.strip() or btn.get_attribute("value") or btn.get_attribute("aria-label") or "Button"
                        buttons.append(btn_text)
            except:
                continue

        return buttons

    @staticmethod
    def debug_modals_on_screen(driver, highlight_duration=5, print_details=True):
        """Kiểm tra và highlight tất cả modal đang xuất hiện với thông tin chi tiết"""
        modal_selectors = [
            ".modal.show",
            ".modal.fade.show",
            ".modal[style*='display: block']",
            "[role='dialog']",
            ".modal-overlay",
            ".modal-content",
            ".ant-modal",
            ".ant-modal-wrap",
        ]

        visible_modals = []
        for selector in modal_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        # Lấy thông tin chi tiết về modal
                        modal_title = ModalDebugger.get_modal_title(element)
                        modal_content = ModalDebugger.get_modal_content_summary(element)
                        modal_buttons = ModalDebugger.get_modal_buttons(element)

                        visible_modals.append(
                            {
                                "element": element,
                                "selector": selector,
                                "classes": element.get_attribute("class"),
                                "id": element.get_attribute("id"),
                                "title": modal_title,
                                "content": modal_content,
                                "buttons": modal_buttons,
                                "size": element.size,
                                "location": element.location,
                            }
                        )
            except NoSuchElementException:
                continue

        if not visible_modals:
            print("❌ Không tìm thấy modal nào đang hiển thị")
            return []

        print(f"✅ Tìm thấy {len(visible_modals)} modal đang hiển thị:")
        print("=" * 80)

        for i, modal_info in enumerate(visible_modals, 1):
            element = modal_info["element"]

            if print_details:
                print(f"\n🔍 Modal #{i}:")
                print(f"   📋 Tên/Title: {modal_info['title']}")
                print(f"   🎯 Selector: {modal_info['selector']}")
                print(f"   🆔 ID: {modal_info['id'] or 'N/A'}")
                print(f"   🏷️  Classes: {modal_info['classes'] or 'N/A'}")
                print(f"   📏 Kích thước: {modal_info['size']}")
                print(f"   📍 Vị trí: {modal_info['location']}")
                print(f"   📝 Nội dung: {modal_info['content']}")

                if modal_info["buttons"]:
                    print(f"   🔘 Buttons: {', '.join(modal_info['buttons'])}")
                else:
                    print(f"   🔘 Buttons: Không có button")

                print("-" * 60)

            # Highlight modal
            print(f"🎯 Highlighting modal #{i}: '{modal_info['title']}' trong {highlight_duration} giây...")
            ModalDebugger.highlight_element(driver, element, highlight_duration)

        print("=" * 80)
        return visible_modals
