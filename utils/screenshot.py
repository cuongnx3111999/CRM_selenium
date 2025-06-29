import logging
import os
import time
from datetime import datetime
from pathlib import Path
from selenium.common.exceptions import WebDriverException, TimeoutException


class screenshot:
    # Cấu hình mặc định
    DEFAULT_SCREENSHOT_DIR = "reports/screenshots"
    MAX_FILENAME_LENGTH = 200
    SCREENSHOT_TIMEOUT = 10  # seconds

    @staticmethod
    def get_screenshot_dir():
        """
        Tạo và trả về đường dẫn thư mục lưu screenshot
        """
        screenshot_dir = Path(screenshot.DEFAULT_SCREENSHOT_DIR)
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        return screenshot_dir

    @staticmethod
    def generate_filename(test_name, status=""):
        """
        Tạo tên file screenshot duy nhất và an toàn

        Args:
            test_name: Tên của test case
            status: Trạng thái test (fail, pass, timeout, etc.)

        Returns:
            str: Tên file screenshot an toàn
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds
        status_prefix = f"{status}_" if status else ""

        try:
            # Làm sạch tên test - loại bỏ ký tự đặc biệt
            safe_name = "".join(c if c.isalnum() or c in "_-." else "_" for c in test_name)
            # Loại bỏ các ký tự Unicode không mong muốn
            safe_name = safe_name.encode("ascii", "ignore").decode("ascii")

            # Giới hạn độ dài tên file
            max_name_length = screenshot.MAX_FILENAME_LENGTH - len(status_prefix) - len(timestamp) - 5  # .png
            if len(safe_name) > max_name_length:
                safe_name = safe_name[:max_name_length]

            filename = f"{status_prefix}{safe_name}_{timestamp}.png"

            # Đảm bảo tên file không trống
            if len(filename.replace(status_prefix, "").replace(timestamp, "").replace("_.png", "")) == 0:
                filename = f"{status_prefix}test_{timestamp}.png"

            return filename

        except Exception as e:
            logging.error(f"Lỗi tạo tên file: {e}")
            return f"{status_prefix}screenshot_{timestamp}.png"

    @classmethod
    def capture_screenshot(cls, driver, test_name, status=""):
        """
        Chụp ảnh màn hình với xử lý lỗi nâng cao

        Args:
            driver: WebDriver instance
            test_name: Tên của test case
            status: Trạng thái của test (fail, pass, timeout, etc.)

        Returns:
            str: Đường dẫn đến file ảnh đã lưu
            None: Nếu có lỗi xảy ra
        """
        if not driver:
            logging.warning("Driver is None, không thể chụp màn hình")
            return None

        try:
            # Kiểm tra driver có còn hoạt động không
            try:
                driver.current_url
            except Exception as e:
                logging.warning(f"Driver không phản hồi: {str(e)}")
                return cls._capture_screenshot_fallback(driver, test_name, status)

            screenshot_dir = cls.get_screenshot_dir()
            filename = cls.generate_filename(test_name, status)
            screenshot_path = screenshot_dir / filename

            # Thử chụp màn hình với timeout
            start_time = time.time()
            success = False

            try:
                # Lưu timeout hiện tại
                original_timeouts = cls._get_current_timeouts(driver)

                # Đặt timeout ngắn cho screenshot
                cls._set_short_timeouts(driver)

                # Chụp màn hình
                driver.save_screenshot(str(screenshot_path))
                success = True

                # Khôi phục timeout gốc
                cls._restore_timeouts(driver, original_timeouts)

            except Exception as screenshot_error:
                logging.warning(f"Screenshot chính thất bại: {screenshot_error}")
                # Thử phương pháp fallback
                return cls._capture_screenshot_fallback(driver, test_name, status)

            # Kiểm tra thời gian thực hiện
            elapsed_time = time.time() - start_time
            if elapsed_time > cls.SCREENSHOT_TIMEOUT:
                logging.warning(f"Screenshot mất quá nhiều thời gian: {elapsed_time:.2f}s")

            # Kiểm tra file đã được tạo thành công và có kích thước hợp lý
            if cls._validate_screenshot(screenshot_path):
                logging.info(f"✅ Screenshot đã được lưu: {screenshot_path}")
                return str(screenshot_path)
            else:
                logging.error(f"Screenshot không hợp lệ: {screenshot_path}")
                return None

        except Exception as e:
            logging.error(f"Lỗi nghiêm trọng khi chụp màn hình: {str(e)}")
            return cls._capture_screenshot_fallback(driver, test_name, status)

    @classmethod
    def capture_screenshot_simple(cls, driver, test_name, status):
        """
        Phương pháp chụp màn hình đơn giản không set timeout - dùng cho backup

        Args:
            driver: WebDriver instance
            test_name: Tên test case
            status: Trạng thái test

        Returns:
            str: Đường dẫn file screenshot hoặc None
        """
        try:
            if not driver:
                return None

            screenshot_dir = cls.get_screenshot_dir()
            filename = cls.generate_filename(test_name, f"{status}_simple")
            screenshot_path = screenshot_dir / filename

            # Chụp trực tiếp không set timeout
            driver.save_screenshot(str(screenshot_path))

            if cls._validate_screenshot(screenshot_path):
                logging.info(f"✅ Simple screenshot saved: {screenshot_path}")
                return str(screenshot_path)
            else:
                return None

        except Exception as e:
            logging.error(f"Simple screenshot failed: {str(e)}")
            return None

    @classmethod
    def _capture_screenshot_fallback(cls, driver, test_name, status):
        """
        Phương pháp chụp màn hình dự phòng khi phương pháp chính thất bại
        """
        try:
            logging.info("Thử phương pháp chụp màn hình dự phòng...")

            # Thử get_screenshot_as_file
            screenshot_dir = cls.get_screenshot_dir()
            filename = cls.generate_filename(test_name, f"{status}_fallback")
            screenshot_path = screenshot_dir / filename

            if driver.get_screenshot_as_file(str(screenshot_path)):
                if cls._validate_screenshot(screenshot_path):
                    logging.info(f"✅ Fallback screenshot saved: {screenshot_path}")
                    return str(screenshot_path)

            # Thử get_screenshot_as_png
            png_data = driver.get_screenshot_as_png()
            if png_data:
                with open(screenshot_path, "wb") as f:
                    f.write(png_data)
                if cls._validate_screenshot(screenshot_path):
                    logging.info(f"✅ PNG screenshot saved: {screenshot_path}")
                    return str(screenshot_path)

        except Exception as e:
            logging.error(f"Tất cả phương pháp chụp màn hình đều thất bại: {str(e)}")

        return None

    @staticmethod
    def _validate_screenshot(screenshot_path):
        """
        Kiểm tra tính hợp lệ của file screenshot

        Args:
            screenshot_path: Đường dẫn đến file screenshot

        Returns:
            bool: True nếu file hợp lệ
        """
        try:
            if not os.path.exists(screenshot_path):
                return False

            # Kiểm tra kích thước file (phải > 1KB)
            file_size = os.path.getsize(screenshot_path)
            if file_size < 1024:  # 1KB
                logging.warning(f"Screenshot file quá nhỏ: {file_size} bytes")
                return False

            # Kiểm tra header PNG (optional)
            with open(screenshot_path, "rb") as f:
                header = f.read(8)
                if not header.startswith(b"\x89PNG\r\n\x1a\n"):
                    logging.warning("File không phải PNG hợp lệ")
                    return False

            return True

        except Exception as e:
            logging.error(f"Lỗi validate screenshot: {e}")
            return False

    @staticmethod
    def _get_current_timeouts(driver):
        """Lấy timeout hiện tại của driver"""
        try:
            return {"script": driver.timeouts.script, "page_load": driver.timeouts.page_load, "implicit": driver.timeouts.implicit_wait}
        except:
            return {}

    @staticmethod
    def _set_short_timeouts(driver):
        """Đặt timeout ngắn cho screenshot"""
        try:
            driver.set_script_timeout(5)
            driver.set_page_load_timeout(5)
            driver.implicitly_wait(2)
        except:
            pass

    @staticmethod
    def _restore_timeouts(driver, original_timeouts):
        """Khôi phục timeout gốc"""
        try:
            if "script" in original_timeouts:
                driver.set_script_timeout(original_timeouts["script"])
            if "page_load" in original_timeouts:
                driver.set_page_load_timeout(original_timeouts["page_load"])
            if "implicit" in original_timeouts:
                driver.implicitly_wait(original_timeouts["implicit"])
        except:
            pass

    @classmethod
    def cleanup_old_screenshots(cls, days_old=7):
        """
        Dọn dẹp các screenshot cũ

        Args:
            days_old: Số ngày để xem screenshot là cũ
        """
        try:
            screenshot_dir = cls.get_screenshot_dir()
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)

            deleted_count = 0
            for file_path in screenshot_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                logging.info(f"Đã xóa {deleted_count} screenshot cũ")

        except Exception as e:
            logging.error(f"Lỗi khi dọn dẹp screenshot: {e}")
