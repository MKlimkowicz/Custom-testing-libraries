import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
import logging

driver = WebDriver | WebElement
default_timeout = 10


class CustomSelenium:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def find_element(self, locator: str) -> WebElement:
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, locator)
            if element:
                return element
        except NoSuchElementException:
            logging.exception(f"No element found with locator {locator}")
            return None

    def find_elements(self, locator: str) -> list:
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, locator)
            if elements:
                return elements
        except NoSuchElementException:
            logging.exception(f"No elements found with locator {locator}")
            return []

    def find_specific_element(self, locator: str, index: int) -> WebElement:
        try:
            element = self.find_elements(locator)[index]
            if element:
                return element
        except IndexError:
            logging.exception(
                f"No element found with index {index} in locator {locator}"
            )
            return None

    def wait_for_element(
        self, locator: str, timeout: int = default_timeout
    ) -> WebElement:
        try:
            element = Wait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, locator))
            )
            if element:
                return element
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for element with locator {locator}"
            )
            return None

    def wait_for_elements(
        self, locator: str, timeout: int = default_timeout
    ) -> list[WebElement]:
        try:
            elements = Wait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator))
            )
            if elements:
                return elements
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for elements with locator {locator}"
            )
            return []

    def wait_for_specific_element(
        self, locator: str, index: int = 0, timeout: int = default_timeout
    ) -> WebElement:
        try:
            elements = Wait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator))
            )
            if elements:
                return elements[index]
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for element with index {index} in locator {locator}"
            )
            return None

    def wait_until_element_invisible(
        self, locator: str, timeout: int = default_timeout
    ) -> bool:
        try:
            return Wait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, locator))
            )
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for invisibility of element with locator {locator}"
            )
            return False

    def wait_for_text_in_element(
        self, locator: str, text: str, timeout: int = default_timeout
    ) -> bool:
        try:
            return Wait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, locator), text)
            )
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for text to be present in element with locator {locator}"
            )
            return False

    def wait_for_text_not_in_element(
        self, locator: str, text: str, index: int = 0
    ) -> bool:
        try:
            element = self.find_specific_element(locator, index)
            return element.text != text
        except Exception as e:
            logging.exception(f"Error in wait_for_text_not_in_element method: {str(e)}")
            return False

    def wait_until_url_is(self, url: str, timeout: int = default_timeout):
        try:
            return Wait(self.driver, timeout).until(EC.url_to_be(url))
        except TimeoutException:
            logging.exception(f"Timeout while waiting for URL to be {url}")
            return False

    def wait_until_url_contains(self, url: str, timeout: int = default_timeout):
        try:
            return Wait(self.driver, timeout).until(EC.url_contains(url))
        except TimeoutException:
            logging.exception(f"Timeout while waiting for URL to contain {url}")
            return False

    def wait_until_title_contains(self, title: str, timeout: int = default_timeout):
        try:
            return Wait(self.driver, timeout).until(EC.title_contains(title))
        except TimeoutException:
            logging.exception(f"Timeout while waiting for title to contain {title}")
            return False

    def is_element_displayed(self, locator: str) -> bool:
        element = self.find_element(locator)
        return element.is_displayed() if element else False

    def is_element_clickable(
        self, locator: str, timeout: int = default_timeout
    ) -> WebElement:
        try:
            element = Wait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, locator))
            )
            if element:
                return element
        except ElementClickInterceptedException:
            logging.exception(f"No clickable element found for locator: {locator}")
            return None

    def check_that_title_is(self, title: str, timeout: int = default_timeout):
        try:
            return Wait(self.driver, timeout).until(EC.title_is(title))
        except TimeoutException:
            logging.exception(f"Timeout while checking if title is {title}")
            return False

    def check_that_title_does_not_contain(self, text: str):
        return text not in self.driver.title

    def are_elements_visible(
        self, locator: str, timeout: int = default_timeout
    ) -> list[WebElement]:
        try:
            elements = Wait(self.driver, timeout).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, locator))
            )
            if elements:
                return elements
        except TimeoutException:
            logging.exception(
                f"Timeout while waiting for visibility of elements with locator {locator}"
            )

    def get_attribute_from_element(self, locator: str, attribute: str, index: int = 0):
        elements = self.wait_for_elements(locator)
        return elements[index].get_attribute(attribute) if elements else None

    def move_mouse(self, element: WebElement):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()

    def scroll_to_element(self, locator, index: int = 0):
        elements = self.wait_for_elements(locator)
        if elements:
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", elements[index]
            )

    def element_list_to_text(self, list_of_elements, read_hidden=False):
        return [
            element.get_attribute("textContent") if read_hidden else element.text
            for element in list_of_elements
        ]

    def refresh_page(self):
        self.driver.refresh()

    def take_screenshot(self, name: str = ""):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"test_{name}_{timestamp}.png"
        folder_name = "folder_name"
        os.makedirs(folder_name, exist_ok=True)
        save_as = f"{folder_name}/{file_name}"
        self.driver.save_screenshot(save_as)
