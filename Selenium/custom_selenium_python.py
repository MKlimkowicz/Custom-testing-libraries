import os
import time
from typing import Union, Optional, List, Callable, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    NoAlertPresentException,
)
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

default_timeout = 10


class SeleniumConfig:
    """Configuration class for CustomSelenium"""
    
    def __init__(
        self,
        default_timeout: int = 10,
        screenshot_folder: str = "screenshots",
        auto_screenshot_on_error: bool = False,
        polling_interval: float = 0.5,
        retry_count: int = 3,
        highlight_elements: bool = False,
        log_performance: bool = False
    ):
        self.default_timeout = default_timeout
        self.screenshot_folder = screenshot_folder
        self.auto_screenshot_on_error = auto_screenshot_on_error
        self.polling_interval = polling_interval
        self.retry_count = retry_count
        self.highlight_elements = highlight_elements
        self.log_performance = log_performance


class CustomSelenium:
    """
    Custom Selenium wrapper class providing enhanced functionality for web automation.
    
    Features:
    - Multi-locator strategy support (CSS, XPath, ID, Name, etc.)
    - Advanced waiting mechanisms with stability checks
    - Configurable timeouts and retries
    - Enhanced error handling with auto-screenshots
    - Common operations (iframes, alerts, dropdowns, etc.)
    - Developer-friendly utilities (highlighting, performance metrics)
    """
    
    def __init__(self, driver: WebDriver, config: Optional[SeleniumConfig] = None):
        """
        Initialize CustomSelenium wrapper.
        
        Args:
            driver: Selenium WebDriver instance
            config: Optional SeleniumConfig for custom settings
        """
        self.driver = driver
        self.config = config or SeleniumConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        os.makedirs(self.config.screenshot_folder, exist_ok=True)
    
    def _parse_locator(self, locator: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
        """
        Parse locator and auto-detect strategy.
        
        Args:
            locator: Either a string (CSS/XPath) or tuple (strategy, value)
            
        Returns:
            Tuple of (By strategy, locator value)
        """
        if isinstance(locator, tuple):
            return locator
        
        if locator.startswith('//') or locator.startswith('(//'):
            return (By.XPATH, locator)
        elif locator.startswith('#') and ' ' not in locator:
            return (By.ID, locator[1:])
        elif locator.startswith('.') and ' ' not in locator:
            return (By.CLASS_NAME, locator[1:])
        else:
            return (By.CSS_SELECTOR, locator)
    
    def find_element(self, locator: Union[str, Tuple[str, str]]) -> Optional[WebElement]:
        """
        Find a single element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            
        Returns:
            WebElement or None if not found
        """
        try:
            by, value = self._parse_locator(locator)
            element = self.driver.find_element(by, value)
            if element and self.config.highlight_elements:
                self._highlight_element(element)
            return element
        except NoSuchElementException:
            self.logger.error(f"No element found with locator {locator}")
            return None
    
    def find_elements(self, locator: Union[str, Tuple[str, str]]) -> List[WebElement]:
        """
        Find multiple elements.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            
        Returns:
            List of WebElements (empty if none found)
        """
        try:
            by, value = self._parse_locator(locator)
            elements = self.driver.find_elements(by, value)
            return elements if elements else []
        except NoSuchElementException:
            self.logger.error(f"No elements found with locator {locator}")
            return []
    
    def find_specific_element(
        self, locator: Union[str, Tuple[str, str]], index: int
    ) -> Optional[WebElement]:
        """
        Find a specific element from a list by index.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            index: Zero-based index
            
        Returns:
            WebElement or None if not found
        """
        try:
            elements = self.find_elements(locator)
            if elements and index < len(elements):
                element = elements[index]
                if self.config.highlight_elements:
                    self._highlight_element(element)
                return element
            return None
        except IndexError:
            self.logger.error(
                f"No element found with index {index} in locator {locator}"
            )
            return None
    
    def wait_for_element(
        self, locator: Union[str, Tuple[str, str]], timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wait for element to be present in DOM.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            WebElement or None if timeout occurs
        """
        timeout = timeout or self.config.default_timeout
        start_time = time.time()
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            element = wait.until(EC.presence_of_element_located((by, value)))
            
            if self.config.log_performance:
                elapsed = time.time() - start_time
                self.logger.info(f"Element found in {elapsed:.2f}s: {locator}")
            
            if element and self.config.highlight_elements:
                self._highlight_element(element)
            return element
        except TimeoutException:
            self.logger.error(f"Timeout waiting for element: {locator}")
            if self.config.auto_screenshot_on_error:
                self.take_screenshot(f"timeout_{locator[:30]}")
            return None
    
    def wait_for_elements(
        self, locator: Union[str, Tuple[str, str]], timeout: Optional[int] = None
    ) -> List[WebElement]:
        """
        Wait for elements to be present in DOM.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            List of WebElements (empty if timeout occurs)
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements if elements else []
        except TimeoutException:
            self.logger.error(f"Timeout waiting for elements: {locator}")
            return []
    
    def wait_for_specific_element(
        self, locator: Union[str, Tuple[str, str]], index: int = 0, timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wait for specific element by index.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            index: Zero-based index
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            WebElement or None if timeout occurs
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            if elements and index < len(elements):
                return elements[index]
            return None
        except TimeoutException:
            self.logger.error(
                f"Timeout waiting for element at index {index}: {locator}"
            )
            return None
    
    def wait_until_element_invisible(
        self, locator: Union[str, Tuple[str, str]], timeout: Optional[int] = None
    ) -> bool:
        """
        Wait until element becomes invisible or removed from DOM.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if element became invisible, False if timeout
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.invisibility_of_element_located((by, value)))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for invisibility: {locator}")
            return False
    
    def wait_for_text_in_element(
        self, locator: Union[str, Tuple[str, str]], text: str, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for text to be present in element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            text: Expected text
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if text appears, False if timeout
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.text_to_be_present_in_element((by, value), text))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for text '{text}' in element: {locator}")
            return False
    
    def wait_for_text_not_in_element(
        self, locator: Union[str, Tuple[str, str]], text: str, 
        index: int = 0, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for text to NOT be present in element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            text: Text that should not be present
            index: Element index if multiple elements match
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if text is not present, False if timeout or error
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            
            def text_not_in_element(driver):
                elements = driver.find_elements(by, value)
                if elements and index < len(elements):
                    return elements[index].text != text
                return False
            
            return wait.until(text_not_in_element)
        except TimeoutException:
            self.logger.error(f"Timeout waiting for text '{text}' to disappear from: {locator}")
            return False
        except Exception as e:
            self.logger.error(f"Error in wait_for_text_not_in_element: {str(e)}")
            return False
    
    def wait_until_url_is(self, url: str, timeout: Optional[int] = None) -> bool:
        """Wait until URL matches exactly."""
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.url_to_be(url))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for URL to be: {url}")
            return False
    
    def wait_until_url_contains(self, url: str, timeout: Optional[int] = None) -> bool:
        """Wait until URL contains substring."""
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.url_contains(url))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for URL to contain: {url}")
            return False
    
    def wait_until_title_contains(self, title: str, timeout: Optional[int] = None) -> bool:
        """Wait until page title contains substring."""
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.title_contains(title))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for title to contain: {title}")
            return False
    
    def wait_for_element_stable(
        self, locator: Union[str, Tuple[str, str]], 
        stability_time: float = 0.5, timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wait for element to be stable (not moving/animating).
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            stability_time: Time element must remain stable (seconds)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            WebElement or None if timeout
        """
        timeout = timeout or self.config.default_timeout
        end_time = time.time() + timeout
        
        element = self.wait_for_element(locator, timeout)
        if not element:
            return None
        
        try:
            last_location = None
            stable_start = None
            
            while time.time() < end_time:
                try:
                    current_location = element.location
                    
                    if last_location == current_location:
                        if stable_start is None:
                            stable_start = time.time()
                        elif time.time() - stable_start >= stability_time:
                            self.logger.info(f"Element stable: {locator}")
                            return element
                    else:
                        stable_start = None
                    
                    last_location = current_location
                    time.sleep(0.1)
                    
                except StaleElementReferenceException:
                    element = self.wait_for_element(locator, 5)
                    if not element:
                        return None
                    last_location = None
                    stable_start = None
            
            self.logger.warning(f"Element did not stabilize: {locator}")
            return element
            
        except Exception as e:
            self.logger.error(f"Error waiting for stable element: {str(e)}")
            return None
    
    def wait_for_element_count(
        self, locator: Union[str, Tuple[str, str]], 
        expected_count: int, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for specific number of elements.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            expected_count: Expected number of elements
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if count matches, False if timeout
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            
            def element_count_is(driver):
                elements = driver.find_elements(by, value)
                return len(elements) == expected_count
            
            return wait.until(element_count_is)
        except TimeoutException:
            self.logger.error(
                f"Timeout waiting for {expected_count} elements: {locator}"
            )
            return False
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for page to fully load (document ready state).
        
        Args:
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if page loaded, False if timeout
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout)
            return wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            self.logger.error("Timeout waiting for page load")
            return False
    
    def is_element_displayed(self, locator: Union[str, Tuple[str, str]]) -> bool:
        """Check if element is displayed."""
        element = self.find_element(locator)
        return element.is_displayed() if element else False
    
    def is_element_clickable(
        self, locator: Union[str, Tuple[str, str]], timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wait for element to be clickable.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            Clickable WebElement or None if timeout
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            if element and self.config.highlight_elements:
                self._highlight_element(element)
            return element
        except TimeoutException:
            self.logger.error(f"Element not clickable: {locator}")
            return None
    
    def check_that_title_is(self, title: str, timeout: Optional[int] = None) -> bool:
        """Check if page title matches exactly."""
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            return wait.until(EC.title_is(title))
        except TimeoutException:
            self.logger.error(f"Title does not match '{title}', current: {self.driver.title}")
            return False
    
    def check_that_title_does_not_contain(self, text: str) -> bool:
        """Check if page title does not contain text."""
        return text not in self.driver.title
    
    def are_elements_visible(
        self, locator: Union[str, Tuple[str, str]], timeout: Optional[int] = None
    ) -> List[WebElement]:
        """
        Wait for all matching elements to be visible.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            List of visible WebElements (empty if timeout)
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            by, value = self._parse_locator(locator)
            wait = Wait(self.driver, timeout, poll_frequency=self.config.polling_interval)
            elements = wait.until(EC.visibility_of_all_elements_located((by, value)))
            return elements if elements else []
        except TimeoutException:
            self.logger.error(f"Timeout waiting for elements visibility: {locator}")
            return []
    
    def get_attribute_from_element(
        self, locator: Union[str, Tuple[str, str]], attribute: str, index: int = 0
    ) -> Optional[str]:
        """
        Get attribute value from element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            attribute: Attribute name
            index: Element index if multiple elements match
            
        Returns:
            Attribute value or None
        """
        elements = self.wait_for_elements(locator)
        if elements and index < len(elements):
            return elements[index].get_attribute(attribute)
        return None
    
    def move_mouse(self, element: WebElement):
        """Move mouse to element using ActionChains."""
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
        except Exception as e:
            self.logger.error(f"Error moving mouse to element: {str(e)}")
    
    def scroll_to_element(
        self, locator: Union[str, Tuple[str, str]], index: int = 0
    ):
        """
        Scroll element into view.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            index: Element index if multiple elements match
        """
        elements = self.wait_for_elements(locator)
        if elements and index < len(elements):
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                elements[index]
            )
            time.sleep(0.3)
    
    def element_list_to_text(
        self, list_of_elements: List[WebElement], read_hidden: bool = False
    ) -> List[str]:
        """
        Convert list of elements to list of text values.
        
        Args:
            list_of_elements: List of WebElements
            read_hidden: If True, gets textContent (includes hidden text)
            
        Returns:
            List of text values
        """
        return [
            element.get_attribute("textContent") if read_hidden else element.text
            for element in list_of_elements
        ]
    
    def switch_to_iframe(self, locator: Union[str, Tuple[str, str], int]):
        """
        Switch to iframe by locator or index.
        
        Args:
            locator: CSS selector, XPath, tuple (By.strategy, value), or integer index
        """
        try:
            if isinstance(locator, int):
                self.driver.switch_to.frame(locator)
            else:
                iframe = self.wait_for_element(locator)
                if iframe:
                    self.driver.switch_to.frame(iframe)
                else:
                    raise NoSuchElementException(f"Iframe not found: {locator}")
            self.logger.info(f"Switched to iframe: {locator}")
        except Exception as e:
            self.logger.error(f"Error switching to iframe: {str(e)}")
            raise
    
    def switch_to_default_content(self):
        """Switch back to main page content from iframe."""
        try:
            self.driver.switch_to.default_content()
            self.logger.info("Switched to default content")
        except Exception as e:
            self.logger.error(f"Error switching to default content: {str(e)}")
    
    def switch_to_parent_frame(self):
        """Switch to parent frame."""
        try:
            self.driver.switch_to.parent_frame()
            self.logger.info("Switched to parent frame")
        except Exception as e:
            self.logger.error(f"Error switching to parent frame: {str(e)}")
    
    def accept_alert(self, timeout: Optional[int] = None) -> bool:
        """
        Accept alert/confirm dialog.
        
        Args:
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if alert was accepted, False if no alert
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert.accept()
            self.logger.info("Alert accepted")
            return True
        except (TimeoutException, NoAlertPresentException):
            self.logger.warning("No alert present")
            return False
    
    def dismiss_alert(self, timeout: Optional[int] = None) -> bool:
        """
        Dismiss alert/confirm dialog.
        
        Args:
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if alert was dismissed, False if no alert
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert.dismiss()
            self.logger.info("Alert dismissed")
            return True
        except (TimeoutException, NoAlertPresentException):
            self.logger.warning("No alert present")
            return False
    
    def get_alert_text(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get text from alert.
        
        Args:
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            Alert text or None if no alert
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            return alert.text
        except (TimeoutException, NoAlertPresentException):
            self.logger.warning("No alert present")
            return None
    
    def send_text_to_alert(self, text: str, timeout: Optional[int] = None) -> bool:
        """
        Send text to prompt dialog.
        
        Args:
            text: Text to send
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if text was sent, False if no alert
        """
        timeout = timeout or self.config.default_timeout
        
        try:
            wait = Wait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert.send_keys(text)
            return True
        except (TimeoutException, NoAlertPresentException):
            self.logger.warning("No alert present")
            return False
    
    def switch_to_window(self, window_handle: str):
        """Switch to window by handle."""
        try:
            self.driver.switch_to.window(window_handle)
            self.logger.info(f"Switched to window: {window_handle}")
        except Exception as e:
            self.logger.error(f"Error switching to window: {str(e)}")
    
    def switch_to_new_window(self, timeout: Optional[int] = None) -> bool:
        """
        Switch to newly opened window.
        
        Args:
            timeout: Custom timeout (uses config default if not provided)
            
        Returns:
            True if switched, False if no new window
        """
        timeout = timeout or self.config.default_timeout
        original_windows = self.driver.window_handles
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            current_windows = self.driver.window_handles
            if len(current_windows) > len(original_windows):
                new_window = list(set(current_windows) - set(original_windows))[0]
                self.driver.switch_to.window(new_window)
                self.logger.info("Switched to new window")
                return True
            time.sleep(0.5)
        
        self.logger.warning("No new window opened")
        return False
    
    def close_current_window(self):
        """Close current window."""
        try:
            self.driver.close()
            self.logger.info("Closed current window")
        except Exception as e:
            self.logger.error(f"Error closing window: {str(e)}")
    
    def get_window_handles(self) -> List[str]:
        """Get all window handles."""
        return self.driver.window_handles
    
    def select_dropdown_by_value(
        self, locator: Union[str, Tuple[str, str]], value: str
    ):
        """
        Select dropdown option by value.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            value: Option value
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                select = Select(element)
                select.select_by_value(value)
                self.logger.info(f"Selected dropdown value: {value}")
        except Exception as e:
            self.logger.error(f"Error selecting dropdown by value: {str(e)}")
    
    def select_dropdown_by_text(
        self, locator: Union[str, Tuple[str, str]], text: str
    ):
        """
        Select dropdown option by visible text.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            text: Option visible text
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                select = Select(element)
                select.select_by_visible_text(text)
                self.logger.info(f"Selected dropdown text: {text}")
        except Exception as e:
            self.logger.error(f"Error selecting dropdown by text: {str(e)}")
    
    def select_dropdown_by_index(
        self, locator: Union[str, Tuple[str, str]], index: int
    ):
        """
        Select dropdown option by index.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            index: Option index
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                select = Select(element)
                select.select_by_index(index)
                self.logger.info(f"Selected dropdown index: {index}")
        except Exception as e:
            self.logger.error(f"Error selecting dropdown by index: {str(e)}")
    
    def get_selected_dropdown_option(
        self, locator: Union[str, Tuple[str, str]]
    ) -> Optional[str]:
        """
        Get currently selected dropdown option text.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            
        Returns:
            Selected option text or None
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                select = Select(element)
                return select.first_selected_option.text
            return None
        except Exception as e:
            self.logger.error(f"Error getting selected option: {str(e)}")
            return None
    
    def hover(self, locator: Union[str, Tuple[str, str]]):
        """
        Hover over element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                ActionChains(self.driver).move_to_element(element).perform()
                self.logger.info(f"Hovered over element: {locator}")
        except Exception as e:
            self.logger.error(f"Error hovering over element: {str(e)}")
    
    def drag_and_drop(
        self, source_locator: Union[str, Tuple[str, str]], 
        target_locator: Union[str, Tuple[str, str]]
    ):
        """
        Drag and drop element.
        
        Args:
            source_locator: Source element locator
            target_locator: Target element locator
        """
        try:
            source = self.wait_for_element(source_locator)
            target = self.wait_for_element(target_locator)
            if source and target:
                ActionChains(self.driver).drag_and_drop(source, target).perform()
                self.logger.info(f"Dragged {source_locator} to {target_locator}")
        except Exception as e:
            self.logger.error(f"Error in drag and drop: {str(e)}")
    
    def send_keys_with_modifier(
        self, locator: Union[str, Tuple[str, str]], 
        modifier: str, key: str
    ):
        """
        Send keys with modifier (e.g., Ctrl+A).
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            modifier: Modifier key (e.g., Keys.CONTROL, Keys.SHIFT)
            key: Key to press
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                modifier_key = getattr(Keys, modifier.upper(), modifier)
                ActionChains(self.driver).key_down(modifier_key).send_keys(key).key_up(modifier_key).perform()
                self.logger.info(f"Sent {modifier}+{key} to element")
        except Exception as e:
            self.logger.error(f"Error sending keys with modifier: {str(e)}")
    
    def double_click(self, locator: Union[str, Tuple[str, str]]):
        """
        Double click element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                ActionChains(self.driver).double_click(element).perform()
                self.logger.info(f"Double clicked element: {locator}")
        except Exception as e:
            self.logger.error(f"Error double clicking: {str(e)}")
    
    def right_click(self, locator: Union[str, Tuple[str, str]]):
        """
        Right click (context click) element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                ActionChains(self.driver).context_click(element).perform()
                self.logger.info(f"Right clicked element: {locator}")
        except Exception as e:
            self.logger.error(f"Error right clicking: {str(e)}")
    
    def add_cookie(self, cookie_dict: dict):
        """Add cookie to browser."""
        try:
            self.driver.add_cookie(cookie_dict)
            self.logger.info(f"Added cookie: {cookie_dict.get('name')}")
        except Exception as e:
            self.logger.error(f"Error adding cookie: {str(e)}")
    
    def get_cookie(self, name: str) -> Optional[dict]:
        """Get cookie by name."""
        try:
            return self.driver.get_cookie(name)
        except Exception as e:
            self.logger.error(f"Error getting cookie: {str(e)}")
            return None
    
    def get_all_cookies(self) -> List[dict]:
        """Get all cookies."""
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"Error getting cookies: {str(e)}")
            return []
    
    def delete_cookie(self, name: str):
        """Delete cookie by name."""
        try:
            self.driver.delete_cookie(name)
            self.logger.info(f"Deleted cookie: {name}")
        except Exception as e:
            self.logger.error(f"Error deleting cookie: {str(e)}")
    
    def delete_all_cookies(self):
        """Delete all cookies."""
        try:
            self.driver.delete_all_cookies()
            self.logger.info("Deleted all cookies")
        except Exception as e:
            self.logger.error(f"Error deleting all cookies: {str(e)}")
    
    def _highlight_element(
        self, element: WebElement, duration: float = 0.5, color: str = "red"
    ):
        """
        Highlight element temporarily for debugging.
        
        Args:
            element: WebElement to highlight
            duration: How long to highlight (seconds)
            color: Highlight color
        """
        try:
            original_style = element.get_attribute("style")
            self.driver.execute_script(
                f"arguments[0].setAttribute('style', arguments[1]);",
                element,
                f"border: 3px solid {color}; background-color: yellow;"
            )
            time.sleep(duration)
            self.driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);",
                element,
                original_style
            )
        except Exception as e:
            self.logger.debug(f"Could not highlight element: {str(e)}")
    
    def highlight_element(
        self, locator: Union[str, Tuple[str, str]], duration: float = 1.0
    ):
        """
        Manually highlight element for debugging.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            duration: How long to highlight (seconds)
        """
        element = self.wait_for_element(locator)
        if element:
            self._highlight_element(element, duration)
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript.
        
        Args:
            script: JavaScript code
            *args: Arguments to pass to script
            
        Returns:
            Script return value
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Error executing script: {str(e)}")
            return None
    
    def refresh_page(self):
        """Refresh current page."""
        try:
            self.driver.refresh()
            self.logger.info("Page refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing page: {str(e)}")
    
    def navigate_to(self, url: str):
        """Navigate to URL."""
        try:
            self.driver.get(url)
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.error(f"Error navigating to URL: {str(e)}")
    
    def go_back(self):
        """Navigate back in browser history."""
        try:
            self.driver.back()
            self.logger.info("Navigated back")
        except Exception as e:
            self.logger.error(f"Error navigating back: {str(e)}")
    
    def go_forward(self):
        """Navigate forward in browser history."""
        try:
            self.driver.forward()
            self.logger.info("Navigated forward")
        except Exception as e:
            self.logger.error(f"Error navigating forward: {str(e)}")
    
    def get_current_url(self) -> str:
        """Get current URL."""
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """Get page title."""
        return self.driver.title
    
    def get_page_source(self) -> str:
        """Get page source HTML."""
        return self.driver.page_source
    
    def take_screenshot(self, name: str = "") -> str:
        """
        Take screenshot and save to file.
        
        Args:
            name: Optional name for screenshot file
            
        Returns:
            Path to saved screenshot
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{name}_{timestamp}.png" if name else f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.config.screenshot_folder, filename)
            
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return ""
    
    def take_element_screenshot(
        self, locator: Union[str, Tuple[str, str]], name: str = ""
    ) -> str:
        """
        Take screenshot of specific element.
        
        Args:
            locator: CSS selector, XPath, or tuple (By.strategy, value)
            name: Optional name for screenshot file
            
        Returns:
            Path to saved screenshot
        """
        try:
            element = self.wait_for_element(locator)
            if element:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"element_{name}_{timestamp}.png" if name else f"element_{timestamp}.png"
                filepath = os.path.join(self.config.screenshot_folder, filename)
                
                element.screenshot(filepath)
                self.logger.info(f"Element screenshot saved: {filepath}")
                return filepath
            return ""
        except Exception as e:
            self.logger.error(f"Error taking element screenshot: {str(e)}")
            return ""
