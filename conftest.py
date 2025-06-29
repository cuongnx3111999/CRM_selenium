"""Global pytest configuration and fixtures"""

import pytest
import time
import datetime
from pathlib import Path
from pytest_html import extras

from pages.base.base_locators import BaseLocators
from pages.login.login_page import LoginPage
from pages.login.login_actions import LoginActions
from pages.base.base_page import BasePage
from pages.users.users_locators import UsersLocators
from utils.screenshot import screenshot
from utils.driver_manager import DriverManager
from utils.logger import Logger
from config.settings import Settings

# Dictionary để lưu đường dẫn screenshot và tracking
screenshots_dict = {}


def pytest_configure(config):
    """Configure pytest with custom markers and metadata."""
    # Thêm markers (giữ nguyên)
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Full regression tests")
    config.addinivalue_line("markers", "login: Login related tests")
    config.addinivalue_line("markers", "users: User related tests")
    config.addinivalue_line("markers", "performance: Performance tests")

    # THÊM PHẦN MỚI: Tạo tên file báo cáo động với thư mục theo ngày
    if hasattr(config.option, "htmlpath") and config.option.htmlpath:
        # Tạo thư mục theo ngày
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")

        # Tạo đường dẫn: reports/2025-06-25/report_084700.html
        report_dir = Path("reports") / today
        report_dir.mkdir(parents=True, exist_ok=True)

        config.option.htmlpath = str(report_dir / f"report_{timestamp}.html")

    # Thêm metadata cho HTML report (cập nhật với timestamp)
    config._metadata = {
        "Project": "CRM Selenium Framework",
        "Base URL": Settings.BASE_URL,
        "Browser": Settings.BROWSER,
        "Test Run Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def pytest_html_report_title(report):
    """Tùy chỉnh tiêu đề cho HTML report"""
    report.title = "CRM Automation Test Report - Executive Summary"


# ==================== SETUP REPORTS DIRECTORY ====================


@pytest.fixture(scope="session", autouse=True)
def setup_reports_directory():
    """Tự động tạo cấu trúc thư mục reports"""
    project_root = Path(__file__).parent
    reports_dir = project_root / "reports"
    screenshot_dir = reports_dir / "screenshots"

    # Tạo thư mục nếu chưa có
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    Logger.get_logger().info(f"📁 Reports directory setup: {reports_dir}")


# ==================== FIXTURES ====================


@pytest.fixture(scope="session")
def driver_manager():
    """Driver manager fixture - session scope"""
    Logger.get_logger().info("=== Starting test session ===")
    manager = DriverManager()
    yield manager
    manager.quit_driver()
    Logger.get_logger().info("=== Test session ended ===")


@pytest.fixture(scope="function")
def driver(driver_manager):
    """WebDriver fixture - function scope (mỗi test 1 driver mới)"""
    Logger.get_logger().info("=== Starting new driver instance ===")
    Logger.get_logger().info(f"🔧 Using HEADLESS mode: {Settings.HEADLESS}")

    # Clear instance để đảm bảo tạo driver mới cho mỗi test
    driver_manager._driver = None

    driver_instance = driver_manager.get_driver()
    driver_instance.delete_all_cookies()
    driver_instance.get(Settings.BASE_URL)

    yield driver_instance

    try:
        driver_instance.delete_all_cookies()
        # Clear any alerts
        try:
            driver_instance.switch_to.alert.dismiss()
        except:
            pass
    except Exception as e:
        Logger.get_logger().warning(f"Cleanup warning: {e}")
    finally:
        driver_manager.quit_driver()


@pytest.fixture(scope="class")
def shared_driver(driver_manager):
    """Shared WebDriver fixture - class scope (dùng chung trong 1 test class)"""
    Logger.get_logger().info("=== Starting shared driver instance ===")
    driver_instance = driver_manager.get_driver()
    driver_instance.delete_all_cookies()
    yield driver_instance
    driver_manager.quit_driver()


@pytest.fixture(scope="class", autouse=True)
def auto_login(shared_driver):
    """Tự động login trước khi chạy các test case trong class"""
    try:
        username = "cuongb@gmail.com"
        password = "Abc123456789@"

        url = Settings.BASE_URL

        login_action = LoginActions(shared_driver)
        login_page = LoginPage(shared_driver)
        base_page = BasePage(shared_driver)
        base_locators = BaseLocators()
        users_locators = UsersLocators()

        # Thực hiện login
        login_page.navigate_to_login_page(url=url)
        login_action.login(username, password)

        # Điều hướng đến trang users
        login_action.choose_language()
        base_page.click(base_locators.btn_setting)
        # base_page.click(users_locators.btn_users)

    except Exception as e:
        Logger.get_logger().error(f"Login failed: {str(e)}")
        raise


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook để capture test results cho failure handling"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ==================== HELPER FUNCTIONS ====================


def _get_driver_from_item(item):
    """Helper function để lấy driver từ item/node"""
    driver = None
    # Thử lấy từ funcargs
    for arg_name in ["driver", "shared_driver"]:
        if hasattr(item, "funcargs") and arg_name in item.funcargs:
            driver = item.funcargs[arg_name]
            if driver:
                return driver

    # Thử lấy từ driver_manager
    if hasattr(item, "funcargs") and "driver_manager" in item.funcargs:
        return item.funcargs["driver_manager"].get_driver()

    return None


def _capture_and_add_to_report(driver, test_name, status, report=None):
    """Helper function để chụp và thêm ảnh vào report với đường dẫn đúng"""
    if not driver:
        return None

    try:
        # Đặt timeout ngắn cho việc chụ màn hình để tránh treo
        driver.set_script_timeout(Settings.SCREENSHOT_TIMEOUT)
        driver.set_page_load_timeout(Settings.SCREENSHOT_TIMEOUT)

        screenshot_path = screenshot.capture_screenshot(driver, test_name, status)
        if screenshot_path:
            screenshots_dict[test_name] = screenshot_path

            # Thêm vào report nếu được cung cấp
            if report and hasattr(report, "extras"):
                # FIX: Sửa đường dẫn để tránh lặp "reports/reports"
                try:
                    # Lấy path từ project root
                    project_root = Path(__file__).parent
                    relative_path = Path(screenshot_path).relative_to(project_root)

                    # Đảm bảo đường dẫn không bị lặp "reports/reports"
                    path_str = str(relative_path).replace("\\", "/")
                    if path_str.startswith("reports/reports/"):
                        path_str = path_str.replace("reports/reports/", "reports/")

                    report.extras.append(extras.image(path_str))
                    Logger.get_logger().debug(f"Added screenshot to report: {path_str}")
                except Exception as path_error:
                    # Fallback: sử dụng đường dẫn gốc
                    report.extras.append(extras.image(screenshot_path))
                    Logger.get_logger().warning(f"Using fallback path: {path_error}")

            return screenshot_path
    except Exception as e:
        Logger.get_logger().error(f"Không thể chụ màn hình: {str(e)}")

    return None


def _determine_failure_status(report):
    """Xác định status chi tiết của test failure"""
    if report.skipped:
        return "skipped", False

    should_screenshot = True

    if report.outcome == "error":
        status = "error"
    elif report.failed:
        status = "fail"
        # Phân loại chi tiết hơn
        if hasattr(report, "longrepr") and report.longrepr:
            longrepr_str = str(report.longrepr)
            if "AssertionError" in longrepr_str:
                status = "assertion_fail"
            elif "TypeError" in longrepr_str:
                status = "type_error"
    else:
        status = "unknown_fail"

    return status, should_screenshot


def _handle_test_failure(item, report, test_name, status):
    """Xử lý khi test thất bại - chụ screenshot và reload page"""
    Logger.get_logger().info(f"❌ Test {test_name} failed with status: {status}")

    try:
        driver = _get_driver_from_item(item)
        if driver:
            # 1. Chụp screenshot CHÍNH khi test fail (trước khi reload)
            _capture_and_add_to_report(driver, f"{test_name}_before_reload", status, report)
            Logger.get_logger().info("📸 Captured screenshot before reload")

            # 2. Reload page
            Logger.get_logger().info("🔄 Reloading page after failure...")
            driver.refresh()
            time.sleep(2)

            # 3. Chụp screenshot sau khi reload (để kiểm tra trang đã reload thành công)
            _capture_and_add_to_report(driver, f"{test_name}_after_reload", "reloaded", report)
            Logger.get_logger().info("📸 Captured screenshot after reload")

        else:
            Logger.get_logger().warning(f"Cannot get driver for test {test_name}")
    except Exception as e:
        Logger.get_logger().error(f"Error handling test failure for {test_name}: {e}")


# ==================== PYTEST HOOKS ====================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook chính để xử lý báo cáo test và chụ màn hình khi test thất bại"""
    outcome = yield
    report = outcome.get_result()

    # Đảm bảo report có thuộc tính extras
    report.extras = getattr(report, "extras", [])

    # Lấy test_name từ node
    test_name = item.nodeid

    # Chỉ quan tâm đến call và setup phase
    if report.when in ["call", "setup"]:
        # Kiểm tra tất cả các trường hợp không pass
        if not report.passed:
            # Xác định status và có cần screenshot không
            status, should_screenshot = _determine_failure_status(report)

            # Xử lý khi test không pass (trừ skipped)
            if should_screenshot:
                _handle_test_failure(item, report, test_name, status)


@pytest.hookimpl(trylast=True)
def pytest_exception_interact(node, call, report):
    """Hook bổ sung để bắt các exception không được xử lý bởi makereport"""
    # TRÁNH DUPLICATE: Chỉ xử lý nếu chưa có screenshot và không phải từ makereport
    test_name = node.nodeid

    # Kiểm tra xem đã có screenshot từ _handle_test_failure() chưa
    before_reload_key = f"{test_name}_before_reload"
    if before_reload_key not in screenshots_dict:
        driver = _get_driver_from_item(node)
        if driver:
            _capture_and_add_to_report(driver, test_name, "exception", report)
            Logger.get_logger().info("📸 Captured exception screenshot (fallback)")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Hook để lưu report vào node để có thể truy cập trong fixtures"""
    outcome = yield

    # Store reports in node for later use
    if hasattr(item, "_report_sections"):
        for report in item._report_sections:
            if report[0] == "call":
                item.rep_call = report
            elif report[0] == "setup":
                item.rep_setup = report


# ==================== TEST DATA FIXTURES ====================


@pytest.fixture
def test_data(request):
    """Fixture để thu thập và lưu trữ test data cho báo cáo"""
    test_name = request.node.nodeid
    data = {}

    def _update_data(new_data):
        data.update(new_data)

    yield type("TestData", (), {"update": _update_data, "get": lambda: data})

    # Sau khi test hoàn thành, thêm data vào report nếu có
    if data and hasattr(request.node, "rep_call"):
        report = request.node.rep_call
        if hasattr(report, "extras"):
            # Tạo HTML cho test data
            data_html = "<div><h3>Test Data:</h3><table border='1'>"
            data_html += "<tr><th>Parameter</th><th>Value</th></tr>"
            for key, value in data.items():
                data_html += f"<tr><td>{key}</td><td>{str(value)}</td></tr>"
            data_html += "</table></div>"

            report.extras.append(extras.html(data_html))
