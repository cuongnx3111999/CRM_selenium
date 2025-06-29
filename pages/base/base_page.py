"""Base Page Object class containing core Selenium operations."""

import functools
import time
from typing import Union, Tuple, Optional, List

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config.settings import Settings
from utils.logger import Logger
from utils.screenshot import screenshot
from .base_locators import BaseLocators


def slow_down(wait_time: float = 0):
    """Decorator to add delay before actions for stability"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(wait_time)
            return result

        return wrapper

    return decorator


class BasePage:
    """Base Page Object class containing core Selenium operations."""

    def __init__(self, driver_manager):
        self.driver = driver_manager
        self.base_locators = BaseLocators
        self.timeout = Settings.EXPLICIT_WAIT
        self.logger = Logger.get_logger(self.__class__.__name__)

    # ========================================================================
    # NAVIGATION METHODS
    # ========================================================================

    def open_url(self, url: str) -> None:
        """Navigate to specified URL"""
        try:
            self.driver.get(url)
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")
            raise

    def get_title(self) -> str:
        """Get the page title"""
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"Failed to get page title: {e}")
            return ""

    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {e}")
            return ""

    def refresh_page(self) -> None:
        """Refresh the current page"""
        try:
            self.driver.refresh()
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {e}")
            raise

    def go_back(self) -> None:
        """Navigate back to previous page"""
        try:
            self.driver.back()
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {e}")
            raise

    # ========================================================================
    # ELEMENT FINDING METHODS
    # ========================================================================

    def find_element(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> WebElement:
        """Find an element by locator or return the element if it's already a WebElement"""
        try:
            if isinstance(locator_or_element, tuple):
                return self.driver.find_element(*locator_or_element)
            return locator_or_element
        except NoSuchElementException as e:
            self.logger.error(f"Element not found: {locator_or_element}")
            raise

    def find_elements(self, locator: Tuple[By, str]) -> List[WebElement]:
        """Find multiple elements by locator"""
        try:
            elements = self.driver.find_elements(*locator)
            return elements
        except Exception as e:
            self.logger.error(f"Failed to find elements {locator}: {e}")
            return []

    def find_element_by_text(self, text: str, element_type: str = "*") -> WebElement:
        """Find element by exact text content"""
        xpath = f"//{element_type}[text()='{text}']"
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            self.logger.error(f"Element with text '{text}' not found")
            raise

    def find_element_containing_text(self, text: str, element_type: str = "*") -> WebElement:
        """Find element containing specific text"""
        xpath = f"//{element_type}[contains(text(),'{text}')]"
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            self.logger.error(f"Element containing text '{text}' not found")
            raise

    def find_button_by_text(self, text: str) -> WebElement:
        """Find button by exact text content"""
        return self.find_element_by_text(text, element_type="button")

    def get_element_by_placeholder(self, placeholder_text: str) -> WebElement:
        """Find input element by placeholder text"""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, f'input[placeholder="{placeholder_text}"]')
        except NoSuchElementException:
            self.logger.error(f"Element with placeholder '{placeholder_text}' not found")
            raise

    def get_element_by_partial_placeholder(self, partial_placeholder: str) -> WebElement:
        """Find input element by partial placeholder text"""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, f'input[placeholder*="{partial_placeholder}"]')
        except NoSuchElementException:
            self.logger.error(f"Element with partial placeholder '{partial_placeholder}' not found")
            raise

    # ========================================================================
    # WAIT METHODS - ENHANCED FOR ANT DESIGN
    # ========================================================================

    def wait_for_clickable(self, locator_or_element, timeout=None, retry_count=1, fast_mode=True):
        timeout = timeout or self.timeout

        if fast_mode:
            # Fast mode: direct Selenium EC
            wait = WebDriverWait(self.driver, timeout)
            if isinstance(locator_or_element, str):
                locator_or_element = (By.XPATH, locator_or_element)

            if isinstance(locator_or_element, tuple):
                return wait.until(EC.element_to_be_clickable(locator_or_element))
            else:
                return wait.until(EC.element_to_be_clickable(locator_or_element))

        else:
            # Simplified enhanced mode: retry mechanism only
            for attempt in range(retry_count + 1):
                try:
                    wait = WebDriverWait(self.driver, timeout)

                    if isinstance(locator_or_element, str):
                        locator_or_element = (By.XPATH, locator_or_element)

                    if isinstance(locator_or_element, tuple):
                        return wait.until(EC.element_to_be_clickable(locator_or_element))
                    else:
                        if self._is_element_stale(locator_or_element):
                            if attempt < retry_count:
                                time.sleep(0.5)
                                continue
                            else:
                                raise StaleElementReferenceException("Element is stale")

                        return wait.until(EC.element_to_be_clickable(locator_or_element))

                except StaleElementReferenceException:
                    if attempt < retry_count:
                        time.sleep(0.5)
                        continue
                    else:
                        raise
                except TimeoutException:
                    if attempt < retry_count:
                        time.sleep(0.5)
                        continue
                    else:
                        raise

    def wait_for_element(
            self,
            locator_or_element: Union[Tuple[By, str], WebElement],
            timeout: Optional[int] = None,
            retry_count: int = 1,
            fast_mode: bool = True
    ) -> WebElement:
        """
        Wait for element visibility with simplified enhanced validation

        Args:
            locator_or_element: Element locator or WebElement
            timeout: Wait timeout in seconds
            retry_count: Number of retry attempts
            fast_mode: If True, use standard Selenium wait (faster). If False, use simplified enhanced mode

        Returns:
            WebElement: Visible element

        Raises:
            TimeoutException: If element not found within timeout
            StaleElementReferenceException: If element becomes stale
        """
        timeout = timeout or self.timeout

        # FAST MODE: Chỉ dùng Selenium WebDriverWait chuẩn
        if fast_mode:
            try:
                wait = WebDriverWait(self.driver, timeout)

                # Xử lý string locator
                if isinstance(locator_or_element, str):
                    locator_or_element = (By.XPATH, locator_or_element)

                # Xử lý tuple locator
                if isinstance(locator_or_element, tuple):
                    element = wait.until(EC.visibility_of_element_located(locator_or_element))
                    self.logger.debug(f"Fast mode: Found visible element")
                    return element

                # Xử lý WebElement
                else:
                    element = wait.until(EC.visibility_of(locator_or_element))
                    self.logger.debug(f"Fast mode: Element is visible")
                    return element

            except TimeoutException:
                self.logger.error(f"Fast mode: Element not visible after {timeout}s")
                raise
            except Exception as e:
                self.logger.error(f"Fast mode: Failed to wait for visible element: {e}")
                raise

        # SIMPLIFIED ENHANCED MODE: Retry mechanism với trust Selenium EC
        else:
            for attempt in range(retry_count + 1):
                try:
                    wait = WebDriverWait(self.driver, timeout)

                    if isinstance(locator_or_element, str):
                        locator_or_element = (By.XPATH, locator_or_element)

                    if isinstance(locator_or_element, tuple):
                        # Trust Selenium EC - không cần complex validation
                        element = wait.until(EC.visibility_of_element_located(locator_or_element))
                        self.logger.debug(f"Simplified enhanced mode: Found visible element")
                        return element
                    else:
                        # Xử lý WebElement với stale check
                        if self._is_element_stale(locator_or_element):
                            if attempt < retry_count:
                                time.sleep(0.5)
                                continue
                            else:
                                raise StaleElementReferenceException("Element is stale")

                        element = wait.until(EC.visibility_of(locator_or_element))
                        self.logger.debug(f"Simplified enhanced mode: Element is visible")
                        return element

                except StaleElementReferenceException:
                    if attempt < retry_count:
                        time.sleep(0.5)
                        continue
                    else:
                        raise

                except TimeoutException:
                    if attempt < retry_count:
                        time.sleep(0.5)
                        continue
                    else:
                        self.logger.error(f"Simplified enhanced mode: Element not visible after {timeout}s")
                        raise

                except Exception as e:
                    if attempt < retry_count:
                        time.sleep(0.5)
                        continue
                    else:
                        self.logger.error(f"Simplified enhanced mode: Failed to wait for visible element: {e}")
                        raise

    # ========================================================================
    # ANT DESIGN HELPER METHODS - INTERNAL USE
    # ========================================================================

    def _find_truly_visible_element(self, elements: List[WebElement]) -> Optional[WebElement]:
        """
        Tìm element thực sự visible từ danh sách elements (xử lý Ant Design)

        Args:
            elements: Danh sách elements cần kiểm tra

        Returns:
            WebElement: Element thực sự visible, None nếu không tìm thấy
        """
        try:
            for element in elements:
                if self._is_element_truly_visible(element):
                    return element
            return None
        except Exception as e:
            self.logger.debug(f"Error finding truly visible element: {e}")
            return None

    def _find_truly_clickable_element(self, elements: List[WebElement]) -> Optional[WebElement]:
        """
        Tìm element thực sự clickable từ danh sách elements (xử lý Ant Design)

        Args:
            elements: Danh sách elements cần kiểm tra

        Returns:
            WebElement: Element thực sự clickable, None nếu không tìm thấy
        """
        try:
            for element in elements:
                if self._is_element_truly_clickable(element):
                    return element
            return None
        except Exception as e:
            self.logger.debug(f"Error finding truly clickable element: {e}")
            return None

    def _is_element_truly_visible(self, element: WebElement) -> bool:
        """
        Kiểm tra element có thực sự visible không (xử lý Ant Design)

        Args:
            element: Element cần kiểm tra

        Returns:
            bool: True nếu element thực sự visible
        """
        try:
            # Kiểm tra cơ bản
            if not element.is_displayed():
                return False

            # Kiểm tra location (không bị đẩy ra ngoài viewport)
            location = element.location
            if location["x"] < 0 or location["y"] < 0:
                return False

            # Kiểm tra size (phải có kích thước thực tế)
            size = element.size
            if size["width"] <= 0 or size["height"] <= 0:
                return False

            # Kiểm tra CSS computed style
            display_style = self.driver.execute_script("return window.getComputedStyle(arguments[0]).display;", element)
            if display_style == "none":
                return False

            visibility_style = self.driver.execute_script("return window.getComputedStyle(arguments[0]).visibility;", element)
            if visibility_style == "hidden":
                return False

            # Kiểm tra opacity
            opacity = self.driver.execute_script("return window.getComputedStyle(arguments[0]).opacity;", element)
            if float(opacity) == 0:
                return False

            # Kiểm tra element có bị che khuất không
            center_x = location["x"] + size["width"] // 2
            center_y = location["y"] + size["height"] // 2

            element_at_point = self.driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", center_x, center_y)

            if element_at_point:
                # Kiểm tra element tại điểm center có phải là element hiện tại hoặc con của nó
                is_same_or_child = self.driver.execute_script(
                    "return arguments[0] === arguments[1] || arguments[0].contains(arguments[1]);", element, element_at_point
                )
                if not is_same_or_child:
                    return False

            return True

        except Exception as e:
            self.logger.debug(f"Error checking element visibility: {e}")
            return False

    def _is_element_truly_clickable(self, element: WebElement) -> bool:
        """
        Kiểm tra element có thực sự clickable không (xử lý Ant Design)

        Args:
            element: Element cần kiểm tra

        Returns:
            bool: True nếu element thực sự clickable
        """
        try:
            # Kiểm tra visible trước
            if not self._is_element_truly_visible(element):
                return False

            # Kiểm tra enabled
            if not element.is_enabled():
                return False

            # Kiểm tra pointer-events CSS
            pointer_events = self.driver.execute_script("return window.getComputedStyle(arguments[0]).pointerEvents;", element)
            if pointer_events == "none":
                return False

            return True

        except Exception as e:
            self.logger.debug(f"Error checking element clickability: {e}")
            return False

    def _is_element_stale(self, element: WebElement) -> bool:
        """Check if element is stale (no longer attached to DOM)"""
        try:
            # Try to access any property to trigger stale check
            element.is_enabled()
            return False
        except StaleElementReferenceException:
            return True
        except Exception:
            # Other exceptions mean element is not stale, just not accessible
            return False

    def _validate_element_clickability(self, element: WebElement) -> bool:
        """
        Additional validation for element clickability beyond EC.element_to_be_clickable

        Args:
            element: WebElement to validate

        Returns:
            bool: True if element is truly clickable
        """
        try:
            # Check basic properties
            if not element.is_displayed() or not element.is_enabled():
                return False

            # Check element size (must have dimensions)
            size = element.size
            if size["width"] <= 0 or size["height"] <= 0:
                return False

            # Check element location (must be in viewport)
            location = element.location
            if location["x"] < 0 or location["y"] < 0:
                return False

            # Check if element is not covered by other elements
            try:
                # Get element at center point
                center_x = location["x"] + size["width"] // 2
                center_y = location["y"] + size["height"] // 2

                element_at_point = self.driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", center_x, center_y)

                # Check if the element at point is the same or a child of our element
                if element_at_point:
                    is_same_or_child = self.driver.execute_script(
                        "return arguments[0] === arguments[1] || arguments[0].contains(arguments[1]);", element, element_at_point
                    )
                    if not is_same_or_child:
                        return False

            except Exception:
                # If we can't check overlap, assume it's clickable
                pass

            return True

        except Exception as e:
            self.logger.debug(f"Error validating element clickability: {e}")
            return True  # Assume clickable if validation fails

    def wait_for_element_to_disappear(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> bool:
        """Wait for an element to disappear from DOM"""
        timeout = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.logger.warning(f"Element still visible after {timeout}s")
            return False

    # ========================================================================
    # INTERACTION METHODS
    # ========================================================================

    @slow_down()
    def click(self, locator_or_element: Union[Tuple[By, str], WebElement], timeout: Optional[int] = None, max_retries: int = 3) -> None:
        """Enhanced click with optimized fallback strategies"""

        click_strategies = [self._normal_click, self._javascript_click, self._actions_click, self._send_keys_click]

        for attempt in range(max_retries):
            try:
                element = self._prepare_element_for_click(locator_or_element, timeout)

                for strategy_index, strategy in enumerate(click_strategies):
                    try:
                        strategy(element, locator_or_element)
                        # Chỉ log khi cần fallback strategy
                        if strategy_index > 0:
                            self.logger.debug(f"Click successful using fallback strategy {strategy_index + 1}")
                        return
                    except Exception as strategy_error:
                        # Chỉ log khi tất cả strategies fail
                        if strategy_index == len(click_strategies) - 1 and attempt == max_retries - 1:
                            self.logger.error(f"All click strategies failed: {str(strategy_error)[:100]}")
                            raise strategy_error
                        continue

            except TimeoutException:
                if attempt == max_retries - 1:
                    self.logger.error(f"Element not clickable after {max_retries} attempts")
                    self._take_timeout_screenshot(f"element_not_clickable")
                    raise

            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Click failed: {str(e)[:100]}")
                    self._take_timeout_screenshot(f"failed_click")
                    raise

    def _prepare_element_for_click(self, locator_or_element: Union[Tuple[By, str], WebElement], timeout: Optional[int]) -> WebElement:
        """Prepare element for clicking with proper waiting and scrolling - IMPROVED VERSION"""
        # Sử dụng wait_for_clickable cải tiến thay vì wait_for_element
        element = self.wait_for_clickable(locator_or_element, timeout)

        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({
                behavior: 'smooth', 
                block: 'center', 
                inline: 'center'
            });
            const rect = arguments[0].getBoundingClientRect();
            if (rect.top < 100) {
                window.scrollBy(0, -100);
            }
        """,
            element,
        )

        time.sleep(0.3)
        return element

    def _normal_click(self, element: WebElement, locator_info) -> None:
        """Standard Selenium click"""
        element.click()

    def _javascript_click(self, element: WebElement, locator_info) -> None:
        """JavaScript-based click"""
        self.driver.execute_script("arguments[0].click();", element)

    def _actions_click(self, element: WebElement, locator_info) -> None:
        """ActionChains-based click with hover"""
        actions = ActionChains(self.driver)
        actions.move_to_element(element).pause(0.2).click().perform()

    def _send_keys_click(self, element: WebElement, locator_info) -> None:
        """Keyboard-based click using Enter/Space"""
        element.send_keys(Keys.RETURN)

    def send_keys(
        self,
        locator_or_element: Union[Tuple[By, str], WebElement],
        text: str = "",
        clear_first: bool = True,
        validate_input: bool = True,
        max_retries: int = 1,
    ) -> "BasePage":
        """Enhanced send_keys with validation and retry mechanism"""
        if text == "":
            return self

        for attempt in range(max_retries + 1):
            try:
                element = self.wait_for_clickable(locator_or_element)

                # Chỉ log khi có lỗi hoặc retry
                if attempt > 0:
                    self.logger.warning(f"Retry send_keys attempt {attempt + 1}")

                self.click(element)

                if clear_first:
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.BACKSPACE)

                element.send_keys(text)

                # Chỉ validate và log khi cần thiết
                if validate_input:
                    if self._validate_input_success(element, text):
                        # Chỉ log khi success sau retry
                        if attempt > 0:
                            self.logger.info(f"Send keys successful after {attempt + 1} attempts")
                        return self
                    else:
                        if attempt < max_retries:
                            self._retry_with_alternative_method(element, text, clear_first)
                            continue
                        else:
                            self.logger.error(f"Send keys validation failed: '{text[:20]}...'")
                            raise Exception(f"Failed to input text after validation")
                else:
                    return self

            except Exception as e:
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue
                else:
                    self.logger.error(f"Send keys failed: '{text[:20]}...': {str(e)[:100]}")
                    self._take_timeout_screenshot(f"sendkeys_failed")
                    raise

        return self

    def _validate_input_success(self, element: WebElement, expected_text: str) -> bool:
        """Validate that the input was successful"""
        try:
            actual_value = (element.get_attribute("value") or element.get_attribute("textContent") or element.text or "").strip()

            return actual_value == expected_text.strip()

        except Exception as e:
            self.logger.error(f"Error during input validation: {e}")
            return False

    def _retry_with_alternative_method(self, element: WebElement, text: str, clear_first: bool) -> None:
        """Retry send_keys using JavaScript approach as fallback"""
        try:
            if clear_first:
                self.driver.execute_script("arguments[0].value = '';", element)

            self.driver.execute_script("arguments[0].value = arguments[1];", element, text)

            # Trigger events to ensure proper form handling
            self.driver.execute_script(
                """
                var element = arguments[0];
                var events = ['input', 'change', 'keyup', 'blur'];
                events.forEach(function(eventType) {
                    var event = new Event(eventType, { 
                        bubbles: true, 
                        cancelable: true 
                    });
                    element.dispatchEvent(event);
                });
            """,
                element,
            )

        except Exception as e:
            self.logger.error(f"Alternative method also failed: {e}")
            raise

    def clear_inputs(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> "BasePage":
        """Clear input field content using keyboard shortcuts"""
        try:
            element = self.find_element(locator_or_element)
            self.click(element)
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.BACKSPACE)
            return self
        except Exception as e:
            self.logger.error(f"Failed to clear input: {e}")
            raise

    def get_text(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> str:
        """Get text content from an element"""
        try:
            element = self.wait_for_element(locator_or_element)
            return element.text
        except Exception as e:
            self.logger.error(f"Failed to get text: {e}")
            return ""

    def get_attribute(self, locator_or_element: Union[Tuple[By, str], WebElement], attribute_name: str) -> str:
        """Get attribute value from an element"""
        try:
            element = self.wait_for_element(locator_or_element)
            value = element.get_attribute(attribute_name)
            return value or ""
        except Exception as e:
            self.logger.error(f"Failed to get attribute '{attribute_name}': {e}")
            return ""

    def scroll_to_element(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> None:
        """Scroll element into view"""
        try:
            element = self.find_element(locator_or_element)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except Exception as e:
            self.logger.error(f"Failed to scroll to element: {e}")
            raise

    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================

    def is_element_present(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> bool:
        """Check if element exists in DOM"""
        try:
            self.find_element(locator_or_element)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def is_displayed(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> bool:
        """Check if element is visible on page"""
        try:
            element = self.find_element(locator_or_element)
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            return False

    def is_enabled(self, locator_or_element: Union[Tuple[By, str], WebElement]) -> bool:
        """Check if element is enabled/interactable"""
        try:
            element = self.find_element(locator_or_element)
            return element.is_enabled()
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            return False

    def is_field_empty(self, field_locator: Union[Tuple[By, str], WebElement]) -> bool:
        """Check if input/select field is empty"""
        try:
            return self.get_attribute(field_locator, "value") == ""
        except Exception as e:
            self.logger.error(f"Failed to check if field is empty: {e}")
            return False

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def take_screenshot(self, filename: str = None) -> str:
        """Take and save screenshot"""
        try:
            return screenshot.generate_filename(self.driver, filename)
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""

    def _take_timeout_screenshot(self, scenario: str) -> None:
        """Internal method to take screenshot on timeout"""
        try:
            screenshot.generate_filename(self.driver, f"timeout_{scenario}")
        except Exception as e:
            self.logger.error(f"Failed to take timeout screenshot: {e}")

    def switch_to_window(self, window_handle: str) -> None:
        """Switch to specific browser window"""
        try:
            self.driver.switch_to.window(window_handle)
        except Exception as e:
            self.logger.error(f"Failed to switch to window '{window_handle}': {e}")
            raise

    def get_window_handles(self) -> List[str]:
        """Get all browser window handles"""
        try:
            handles = self.driver.window_handles
            return handles
        except Exception as e:
            self.logger.error(f"Failed to get window handles: {e}")
            return []

    def is_select_box_by_role(self, locator_or_element: Union[Tuple[By, str], WebElement, str]) -> bool:
        """
        Kiểm tra element có phải select box qua thuộc tính role

        Args:
            locator_or_element: Có thể là:
                - Tuple[By, str]: (By.ID, "element_id")
                - WebElement: element đã tìm được
                - str: element_id (sẽ convert thành (By.ID, element_id))

        Returns:
            bool: True nếu là select box (role="combobox"), False nếu không
        """
        try:
            if isinstance(locator_or_element, str):
                locator_or_element = (By.ID, locator_or_element)

            element = self.find_element(locator_or_element)
            role = element.get_attribute("role")
            return role == "combobox"

        except Exception as e:
            self.logger.error(f"Failed to check role for {locator_or_element}: {e}")
            return False