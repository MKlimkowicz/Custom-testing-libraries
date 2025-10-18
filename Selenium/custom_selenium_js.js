const { Builder, By, until, Key } = require("selenium-webdriver");
const winston = require("winston");
const fs = require("fs");
const path = require("path");

class SeleniumConfig {
  constructor(options = {}) {
    this.defaultTimeout = options.defaultTimeout || 10000;
    this.screenshotFolder = options.screenshotFolder || "screenshots";
    this.autoScreenshotOnError = options.autoScreenshotOnError || false;
    this.pollingInterval = options.pollingInterval || 500;
    this.retryCount = options.retryCount || 3;
    this.highlightElements = options.highlightElements || false;
    this.logPerformance = options.logPerformance || false;
  }
}

class CustomSelenium {
  /**
   * Initialize CustomSelenium wrapper.
   * @param {WebDriver} driver - Selenium WebDriver instance
   * @param {SeleniumConfig} config - Optional SeleniumConfig for custom settings
   */
  constructor(driver, config = null) {
    this.driver = driver;
    this.config = config || new SeleniumConfig();
    
    this.logger = winston.createLogger({
      level: "info",
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.printf(({ timestamp, level, message }) => {
          return `${timestamp} - ${level}: ${message}`;
        })
      ),
      transports: [new winston.transports.Console()],
    });

    if (!fs.existsSync(this.config.screenshotFolder)) {
      fs.mkdirSync(this.config.screenshotFolder, { recursive: true });
    }
  }

  /**
   * Parse locator and auto-detect strategy.
   * @param {string|Object} locator - Either a string (CSS/XPath) or By object
   * @returns {Function} By locator function
   */
  _parseLocator(locator) {
    if (typeof locator === "object" && locator.using) {
      return locator;
    }

    if (locator.startsWith("//") || locator.startsWith("(//")) {
      return By.xpath(locator);
    } else if (locator.startsWith("#") && !locator.includes(" ")) {
      return By.id(locator.substring(1));
    } else if (locator.startsWith(".") && !locator.includes(" ")) {
      return By.className(locator.substring(1));
    } else {
      return By.css(locator);
    }
  }

  /**
   * Find a single element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @returns {Promise<WebElement|null>} WebElement or null if not found
   */
  async findElement(locator) {
    try {
      const by = this._parseLocator(locator);
      const element = await this.driver.findElement(by);
      if (element && this.config.highlightElements) {
        await this._highlightElement(element);
      }
      return element;
    } catch (err) {
      this.logger.error(`No element found with locator ${locator}`);
      return null;
    }
  }

  /**
   * Find multiple elements.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @returns {Promise<Array<WebElement>>} Array of WebElements (empty if none found)
   */
  async findElements(locator) {
    try {
      const by = this._parseLocator(locator);
      const elements = await this.driver.findElements(by);
      return elements || [];
    } catch (err) {
      this.logger.error(`No elements found with locator ${locator}`);
      return [];
    }
  }

  /**
   * Find a specific element from a list by index.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} index - Zero-based index
   * @returns {Promise<WebElement|null>} WebElement or null if not found
   */
  async findSpecificElement(locator, index = 0) {
    try {
      const elements = await this.findElements(locator);
      if (elements && elements.length > index) {
        const element = elements[index];
        if (this.config.highlightElements) {
          await this._highlightElement(element);
        }
        return element;
      }
      return null;
    } catch (err) {
      this.logger.error(
        `No element found with index ${index} in locator ${locator}`
      );
      return null;
    }
  }

  /**
   * Wait for element to be present in DOM.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<WebElement|null>} WebElement or null if timeout occurs
   */
  async waitForElement(locator, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;
    const startTime = Date.now();

    try {
      const by = this._parseLocator(locator);
      const element = await this.driver.wait(
        until.elementLocated(by),
        timeout,
        `Timeout waiting for element: ${locator}`,
        this.config.pollingInterval
      );

      if (this.config.logPerformance) {
        const elapsed = (Date.now() - startTime) / 1000;
        this.logger.info(`Element found in ${elapsed.toFixed(2)}s: ${locator}`);
      }

      if (element && this.config.highlightElements) {
        await this._highlightElement(element);
      }
      return element;
    } catch (err) {
      this.logger.error(`Timeout waiting for element: ${locator}`);
      if (this.config.autoScreenshotOnError) {
        await this.takeScreenshot(`timeout_${locator.substring(0, 30)}`);
      }
      return null;
    }
  }

  /**
   * Wait for elements to be present in DOM.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<Array<WebElement>>} Array of WebElements (empty if timeout occurs)
   */
  async waitForElements(locator, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const elements = await this.driver.findElements(by);
          return elements.length > 0;
        },
        timeout,
        `Timeout waiting for elements: ${locator}`,
        this.config.pollingInterval
      );
      const elements = await this.driver.findElements(by);
      return elements || [];
    } catch (err) {
      this.logger.error(`Timeout waiting for elements: ${locator}`);
      return [];
    }
  }

  /**
   * Wait for specific element by index.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} index - Zero-based index
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<WebElement|null>} WebElement or null if timeout occurs
   */
  async waitForSpecificElement(locator, index = 0, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const elements = await this.driver.findElements(by);
          return elements.length > index;
        },
        timeout,
        `Timeout waiting for element at index ${index}: ${locator}`,
        this.config.pollingInterval
      );
      const elements = await this.driver.findElements(by);
      return elements[index] || null;
    } catch (err) {
      this.logger.error(
        `Timeout waiting for element at index ${index}: ${locator}`
      );
      return null;
    }
  }

  /**
   * Wait until element becomes invisible or removed from DOM.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if element became invisible, false if timeout
   */
  async waitUntilElementInvisible(locator, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      
      // Wait for element to either not exist or be invisible
      await this.driver.wait(
        async () => {
          try {
            const elements = await this.driver.findElements(by);
            if (elements.length === 0) {
              return true; // Element doesn't exist
            }
            const isDisplayed = await elements[0].isDisplayed();
            return !isDisplayed; // Element exists but not visible
          } catch (err) {
            return true; // Element no longer in DOM
          }
        },
        timeout,
        `Timeout waiting for invisibility: ${locator}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(`Timeout waiting for invisibility: ${locator}`);
      return false;
    }
  }

  /**
   * Wait for text to be present in element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} text - Expected text
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if text appears, false if timeout
   */
  async waitForTextInElement(locator, text, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const element = await this.driver.findElement(by);
          const elementText = await element.getText();
          return elementText.includes(text);
        },
        timeout,
        `Timeout waiting for text '${text}' in element: ${locator}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(
        `Timeout waiting for text '${text}' in element: ${locator}`
      );
      return false;
    }
  }

  /**
   * Wait for text to NOT be present in element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} text - Text that should not be present
   * @param {number} index - Element index if multiple elements match
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if text is not present, false if timeout or error
   */
  async waitForTextNotInElement(locator, text, index = 0, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const elements = await this.driver.findElements(by);
          if (elements && elements.length > index) {
            const elementText = await elements[index].getText();
            return elementText !== text;
          }
          return false;
        },
        timeout,
        `Timeout waiting for text '${text}' to disappear from: ${locator}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(
        `Timeout waiting for text '${text}' to disappear from: ${locator}`
      );
      return false;
    }
  }

  /**
   * Wait until URL matches exactly.
   * @param {string} url - Expected URL
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if URL matches, false if timeout
   */
  async waitUntilUrlIs(url, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(
        async () => {
          const currentUrl = await this.driver.getCurrentUrl();
          return currentUrl === url;
        },
        timeout,
        `Timeout waiting for URL to be: ${url}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(`Timeout waiting for URL to be: ${url}`);
      return false;
    }
  }

  /**
   * Wait until URL contains substring.
   * @param {string} url - Expected URL substring
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if URL contains substring, false if timeout
   */
  async waitUntilUrlContains(url, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(
        async () => {
          const currentUrl = await this.driver.getCurrentUrl();
          return currentUrl.includes(url);
        },
        timeout,
        `Timeout waiting for URL to contain: ${url}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(`Timeout waiting for URL to contain: ${url}`);
      return false;
    }
  }

  /**
   * Wait until page title contains substring.
   * @param {string} title - Expected title substring
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if title contains substring, false if timeout
   */
  async waitUntilTitleContains(title, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(
        async () => {
          const currentTitle = await this.driver.getTitle();
          return currentTitle.includes(title);
        },
        timeout,
        `Timeout waiting for title to contain: ${title}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(`Timeout waiting for title to contain: ${title}`);
      return false;
    }
  }

  /**
   * Wait for element to be stable (not moving/animating).
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} stabilityTime - Time element must remain stable (milliseconds)
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<WebElement|null>} WebElement or null if timeout
   */
  async waitForElementStable(locator, stabilityTime = 500, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;
    const endTime = Date.now() + timeout;

    const element = await this.waitForElement(locator, timeout);
    if (!element) {
      return null;
    }

    try {
      let lastLocation = null;
      let stableStart = null;

      while (Date.now() < endTime) {
        try {
          const currentLocation = await element.getRect();

          if (
            lastLocation &&
            currentLocation.x === lastLocation.x &&
            currentLocation.y === lastLocation.y
          ) {
            if (stableStart === null) {
              stableStart = Date.now();
            } else if (Date.now() - stableStart >= stabilityTime) {
              this.logger.info(`Element stable: ${locator}`);
              return element;
            }
          } else {
            stableStart = null;
          }

          lastLocation = currentLocation;
          await this._sleep(100);
        } catch (err) {
          // Stale element, try to find again
          const newElement = await this.waitForElement(locator, 5000);
          if (!newElement) {
            return null;
          }
          lastLocation = null;
          stableStart = null;
        }
      }

      this.logger.warn(`Element did not stabilize: ${locator}`);
      return element;
    } catch (err) {
      this.logger.error(`Error waiting for stable element: ${err.message}`);
      return null;
    }
  }

  /**
   * Wait for specific number of elements.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} expectedCount - Expected number of elements
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if count matches, false if timeout
   */
  async waitForElementCount(locator, expectedCount, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const elements = await this.driver.findElements(by);
          return elements.length === expectedCount;
        },
        timeout,
        `Timeout waiting for ${expectedCount} elements: ${locator}`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error(
        `Timeout waiting for ${expectedCount} elements: ${locator}`
      );
      return false;
    }
  }

  /**
   * Wait for page to fully load (document ready state).
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if page loaded, false if timeout
   */
  async waitForPageLoad(timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(
        async () => {
          const readyState = await this.driver.executeScript(
            "return document.readyState"
          );
          return readyState === "complete";
        },
        timeout,
        "Timeout waiting for page load",
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      this.logger.error("Timeout waiting for page load");
      return false;
    }
  }

  /**
   * Check if element is displayed.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @returns {Promise<boolean>} True if element is displayed
   */
  async isElementDisplayed(locator) {
    try {
      const element = await this.findElement(locator);
      if (element) {
        return await element.isDisplayed();
      }
      return false;
    } catch (err) {
      this.logger.error(`Error checking if element is displayed: ${locator}`);
      return false;
    }
  }

  /**
   * Wait for element to be clickable.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<WebElement|null>} Clickable WebElement or null if timeout
   */
  async isElementClickable(locator, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const element = await this.waitForElement(locator, timeout);
      if (element) {
        await this.driver.wait(
          until.elementIsVisible(element),
          timeout,
          `Element not visible: ${locator}`,
          this.config.pollingInterval
        );
        await this.driver.wait(
          until.elementIsEnabled(element),
          timeout,
          `Element not enabled: ${locator}`,
          this.config.pollingInterval
        );
        if (this.config.highlightElements) {
          await this._highlightElement(element);
        }
        return element;
      }
      return null;
    } catch (err) {
      this.logger.error(`Element not clickable: ${locator}`);
      return null;
    }
  }

  /**
   * Check if page title matches exactly.
   * @param {string} title - Expected title
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if title matches, false if timeout
   */
  async checkThatTitleIs(title, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(
        async () => {
          const currentTitle = await this.driver.getTitle();
          return currentTitle === title;
        },
        timeout,
        `Title does not match '${title}'`,
        this.config.pollingInterval
      );
      return true;
    } catch (err) {
      const currentTitle = await this.driver.getTitle();
      this.logger.error(
        `Title does not match '${title}', current: ${currentTitle}`
      );
      return false;
    }
  }

  /**
   * Check if page title does not contain text.
   * @param {string} text - Text that should not be in title
   * @returns {Promise<boolean>} True if title doesn't contain text
   */
  async checkThatTitleDoesNotContain(text) {
    const currentTitle = await this.driver.getTitle();
    return !currentTitle.includes(text);
  }

  /**
   * Wait for all matching elements to be visible.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<Array<WebElement>>} Array of visible WebElements (empty if timeout)
   */
  async areElementsVisible(locator, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      const by = this._parseLocator(locator);
      await this.driver.wait(
        async () => {
          const elements = await this.driver.findElements(by);
          if (elements.length === 0) {
            return false;
          }
          // Check all elements are displayed
          const displayedStates = await Promise.all(
            elements.map((el) => el.isDisplayed())
          );
          return displayedStates.every((displayed) => displayed);
        },
        timeout,
        `Timeout waiting for elements visibility: ${locator}`,
        this.config.pollingInterval
      );
      const elements = await this.driver.findElements(by);
      return elements || [];
    } catch (err) {
      this.logger.error(`Timeout waiting for elements visibility: ${locator}`);
      return [];
    }
  }

  /**
   * Get attribute value from element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} attribute - Attribute name
   * @param {number} index - Element index if multiple elements match
   * @returns {Promise<string|null>} Attribute value or null
   */
  async getAttributeFromElement(locator, attribute, index = 0) {
    const elements = await this.waitForElements(locator);
    if (elements && elements.length > index) {
      return await elements[index].getAttribute(attribute);
    }
    return null;
  }

  /**
   * Move mouse to element using Actions.
   * @param {WebElement} element - WebElement to move mouse to
   */
  async moveMouse(element) {
    try {
      const actions = this.driver.actions({ async: true });
      await actions.move({ origin: element }).perform();
    } catch (err) {
      this.logger.error(`Error moving mouse to element: ${err.message}`);
    }
  }

  /**
   * Scroll element into view.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} index - Element index if multiple elements match
   */
  async scrollToElement(locator, index = 0) {
    const elements = await this.waitForElements(locator);
    if (elements && elements.length > index) {
      await this.driver.executeScript(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        elements[index]
      );
      await this._sleep(300);
    }
  }

  /**
   * Convert list of elements to list of text values.
   * @param {Array<WebElement>} listOfElements - Array of WebElements
   * @param {boolean} readHidden - If true, gets textContent (includes hidden text)
   * @returns {Promise<Array<string>>} Array of text values
   */
  async elementListToText(listOfElements, readHidden = false) {
    const textList = [];
    for (let i = 0; i < listOfElements.length; i++) {
      if (readHidden) {
        const textContent = await listOfElements[i].getAttribute("textContent");
        textList.push(textContent);
      } else {
        const text = await listOfElements[i].getText();
        textList.push(text);
      }
    }
    return textList;
  }

  /**
   * Switch to iframe by locator or index.
   * @param {string|Object|number} locator - CSS selector, XPath, By object, or integer index
   */
  async switchToIframe(locator) {
    try {
      if (typeof locator === "number") {
        await this.driver.switchTo().frame(locator);
      } else {
        const iframe = await this.waitForElement(locator);
        if (iframe) {
          await this.driver.switchTo().frame(iframe);
        } else {
          throw new Error(`Iframe not found: ${locator}`);
        }
      }
      this.logger.info(`Switched to iframe: ${locator}`);
    } catch (err) {
      this.logger.error(`Error switching to iframe: ${err.message}`);
      throw err;
    }
  }

  /**
   * Switch back to main page content from iframe.
   */
  async switchToDefaultContent() {
    try {
      await this.driver.switchTo().defaultContent();
      this.logger.info("Switched to default content");
    } catch (err) {
      this.logger.error(`Error switching to default content: ${err.message}`);
    }
  }

  /**
   * Switch to parent frame.
   */
  async switchToParentFrame() {
    try {
      await this.driver.switchTo().parentFrame();
      this.logger.info("Switched to parent frame");
    } catch (err) {
      this.logger.error(`Error switching to parent frame: ${err.message}`);
    }
  }

  /**
   * Accept alert/confirm dialog.
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if alert was accepted, false if no alert
   */
  async acceptAlert(timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(until.alertIsPresent(), timeout);
      const alert = await this.driver.switchTo().alert();
      await alert.accept();
      this.logger.info("Alert accepted");
      return true;
    } catch (err) {
      this.logger.warn("No alert present");
      return false;
    }
  }

  /**
   * Dismiss alert/confirm dialog.
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if alert was dismissed, false if no alert
   */
  async dismissAlert(timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(until.alertIsPresent(), timeout);
      const alert = await this.driver.switchTo().alert();
      await alert.dismiss();
      this.logger.info("Alert dismissed");
      return true;
    } catch (err) {
      this.logger.warn("No alert present");
      return false;
    }
  }

  /**
   * Get text from alert.
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<string|null>} Alert text or null if no alert
   */
  async getAlertText(timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(until.alertIsPresent(), timeout);
      const alert = await this.driver.switchTo().alert();
      return await alert.getText();
    } catch (err) {
      this.logger.warn("No alert present");
      return null;
    }
  }

  /**
   * Send text to prompt dialog.
   * @param {string} text - Text to send
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if text was sent, false if no alert
   */
  async sendTextToAlert(text, timeout = null) {
    timeout = timeout || this.config.defaultTimeout;

    try {
      await this.driver.wait(until.alertIsPresent(), timeout);
      const alert = await this.driver.switchTo().alert();
      await alert.sendKeys(text);
      return true;
    } catch (err) {
      this.logger.warn("No alert present");
      return false;
    }
  }

  /**
   * Switch to window by handle.
   * @param {string} windowHandle - Window handle
   */
  async switchToWindow(windowHandle) {
    try {
      await this.driver.switchTo().window(windowHandle);
      this.logger.info(`Switched to window: ${windowHandle}`);
    } catch (err) {
      this.logger.error(`Error switching to window: ${err.message}`);
    }
  }

  /**
   * Switch to newly opened window.
   * @param {number} timeout - Custom timeout (uses config default if not provided)
   * @returns {Promise<boolean>} True if switched, false if no new window
   */
  async switchToNewWindow(timeout = null) {
    timeout = timeout || this.config.defaultTimeout;
    const originalWindows = await this.driver.getAllWindowHandles();
    const endTime = Date.now() + timeout;

    while (Date.now() < endTime) {
      const currentWindows = await this.driver.getAllWindowHandles();
      if (currentWindows.length > originalWindows.length) {
        const newWindow = currentWindows.find(
          (handle) => !originalWindows.includes(handle)
        );
        await this.driver.switchTo().window(newWindow);
        this.logger.info("Switched to new window");
        return true;
      }
      await this._sleep(500);
    }

    this.logger.warn("No new window opened");
    return false;
  }

  /**
   * Close current window.
   */
  async closeCurrentWindow() {
    try {
      await this.driver.close();
      this.logger.info("Closed current window");
    } catch (err) {
      this.logger.error(`Error closing window: ${err.message}`);
    }
  }

  /**
   * Get all window handles.
   * @returns {Promise<Array<string>>} Array of window handles
   */
  async getWindowHandles() {
    return await this.driver.getAllWindowHandles();
  }

  /**
   * Select dropdown option by value.
   * Note: Selenium WebDriver JS doesn't have Select class, so we use custom implementation
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} value - Option value
   */
  async selectDropdownByValue(locator, value) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        await element.findElement(By.css(`option[value="${value}"]`)).click();
        this.logger.info(`Selected dropdown value: ${value}`);
      }
    } catch (err) {
      this.logger.error(`Error selecting dropdown by value: ${err.message}`);
    }
  }

  /**
   * Select dropdown option by visible text.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} text - Option visible text
   */
  async selectDropdownByText(locator, text) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const options = await element.findElements(By.css("option"));
        for (let option of options) {
          const optionText = await option.getText();
          if (optionText === text) {
            await option.click();
            this.logger.info(`Selected dropdown text: ${text}`);
            return;
          }
        }
      }
    } catch (err) {
      this.logger.error(`Error selecting dropdown by text: ${err.message}`);
    }
  }

  /**
   * Select dropdown option by index.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} index - Option index
   */
  async selectDropdownByIndex(locator, index) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const options = await element.findElements(By.css("option"));
        if (options.length > index) {
          await options[index].click();
          this.logger.info(`Selected dropdown index: ${index}`);
        }
      }
    } catch (err) {
      this.logger.error(`Error selecting dropdown by index: ${err.message}`);
    }
  }

  /**
   * Get currently selected dropdown option text.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @returns {Promise<string|null>} Selected option text or null
   */
  async getSelectedDropdownOption(locator) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const selectedOption = await element.findElement(
          By.css("option:checked")
        );
        return await selectedOption.getText();
      }
      return null;
    } catch (err) {
      this.logger.error(`Error getting selected option: ${err.message}`);
      return null;
    }
  }

  /**
   * Hover over element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   */
  async hover(locator) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const actions = this.driver.actions({ async: true });
        await actions.move({ origin: element }).perform();
        this.logger.info(`Hovered over element: ${locator}`);
      }
    } catch (err) {
      this.logger.error(`Error hovering over element: ${err.message}`);
    }
  }

  /**
   * Drag and drop element.
   * @param {string|Object} sourceLocator - Source element locator
   * @param {string|Object} targetLocator - Target element locator
   */
  async dragAndDrop(sourceLocator, targetLocator) {
    try {
      const source = await this.waitForElement(sourceLocator);
      const target = await this.waitForElement(targetLocator);
      if (source && target) {
        const actions = this.driver.actions({ async: true });
        await actions.dragAndDrop(source, target).perform();
        this.logger.info(`Dragged ${sourceLocator} to ${targetLocator}`);
      }
    } catch (err) {
      this.logger.error(`Error in drag and drop: ${err.message}`);
    }
  }

  /**
   * Send keys with modifier (e.g., Ctrl+A).
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} modifier - Modifier key (e.g., 'CONTROL', 'SHIFT')
   * @param {string} key - Key to press
   */
  async sendKeysWithModifier(locator, modifier, key) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const modifierKey = Key[modifier.toUpperCase()] || modifier;
        const actions = this.driver.actions({ async: true });
        await actions
          .keyDown(modifierKey)
          .sendKeys(key)
          .keyUp(modifierKey)
          .perform();
        this.logger.info(`Sent ${modifier}+${key} to element`);
      }
    } catch (err) {
      this.logger.error(`Error sending keys with modifier: ${err.message}`);
    }
  }

  /**
   * Double click element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   */
  async doubleClick(locator) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const actions = this.driver.actions({ async: true });
        await actions.doubleClick(element).perform();
        this.logger.info(`Double clicked element: ${locator}`);
      }
    } catch (err) {
      this.logger.error(`Error double clicking: ${err.message}`);
    }
  }

  /**
   * Right click (context click) element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   */
  async rightClick(locator) {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const actions = this.driver.actions({ async: true });
        await actions.contextClick(element).perform();
        this.logger.info(`Right clicked element: ${locator}`);
      }
    } catch (err) {
      this.logger.error(`Error right clicking: ${err.message}`);
    }
  }

  /**
   * Add cookie to browser.
   * @param {Object} cookieDict - Cookie object
   */
  async addCookie(cookieDict) {
    try {
      await this.driver.manage().addCookie(cookieDict);
      this.logger.info(`Added cookie: ${cookieDict.name}`);
    } catch (err) {
      this.logger.error(`Error adding cookie: ${err.message}`);
    }
  }

  /**
   * Get cookie by name.
   * @param {string} name - Cookie name
   * @returns {Promise<Object|null>} Cookie object or null
   */
  async getCookie(name) {
    try {
      return await this.driver.manage().getCookie(name);
    } catch (err) {
      this.logger.error(`Error getting cookie: ${err.message}`);
      return null;
    }
  }

  /**
   * Get all cookies.
   * @returns {Promise<Array<Object>>} Array of cookie objects
   */
  async getAllCookies() {
    try {
      return await this.driver.manage().getCookies();
    } catch (err) {
      this.logger.error(`Error getting cookies: ${err.message}`);
      return [];
    }
  }

  /**
   * Delete cookie by name.
   * @param {string} name - Cookie name
   */
  async deleteCookie(name) {
    try {
      await this.driver.manage().deleteCookie(name);
      this.logger.info(`Deleted cookie: ${name}`);
    } catch (err) {
      this.logger.error(`Error deleting cookie: ${err.message}`);
    }
  }

  /**
   * Delete all cookies.
   */
  async deleteAllCookies() {
    try {
      await this.driver.manage().deleteAllCookies();
      this.logger.info("Deleted all cookies");
    } catch (err) {
      this.logger.error(`Error deleting all cookies: ${err.message}`);
    }
  }

  /**
   * Highlight element temporarily for debugging.
   * @param {WebElement} element - WebElement to highlight
   * @param {number} duration - How long to highlight (milliseconds)
   * @param {string} color - Highlight color
   */
  async _highlightElement(element, duration = 500, color = "red") {
    try {
      const originalStyle = await element.getAttribute("style");
      await this.driver.executeScript(
        "arguments[0].setAttribute('style', arguments[1]);",
        element,
        `border: 3px solid ${color}; background-color: yellow;`
      );
      await this._sleep(duration);
      await this.driver.executeScript(
        "arguments[0].setAttribute('style', arguments[1]);",
        element,
        originalStyle || ""
      );
    } catch (err) {
    }
  }

  /**
   * Manually highlight element for debugging.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {number} duration - How long to highlight (milliseconds)
   */
  async highlightElement(locator, duration = 1000) {
    const element = await this.waitForElement(locator);
    if (element) {
      await this._highlightElement(element, duration);
    }
  }

  /**
   * Execute JavaScript.
   * @param {string} script - JavaScript code
   * @param {...any} args - Arguments to pass to script
   * @returns {Promise<any>} Script return value
   */
  async executeScript(script, ...args) {
    try {
      return await this.driver.executeScript(script, ...args);
    } catch (err) {
      this.logger.error(`Error executing script: ${err.message}`);
      return null;
    }
  }

  /**
   * Refresh current page.
   */
  async refreshPage() {
    try {
      await this.driver.navigate().refresh();
      this.logger.info("Page refreshed");
    } catch (err) {
      this.logger.error(`Error refreshing page: ${err.message}`);
    }
  }

  /**
   * Navigate to URL.
   * @param {string} url - URL to navigate to
   */
  async navigateTo(url) {
    try {
      await this.driver.get(url);
      this.logger.info(`Navigated to: ${url}`);
    } catch (err) {
      this.logger.error(`Error navigating to URL: ${err.message}`);
    }
  }

  /**
   * Navigate back in browser history.
   */
  async goBack() {
    try {
      await this.driver.navigate().back();
      this.logger.info("Navigated back");
    } catch (err) {
      this.logger.error(`Error navigating back: ${err.message}`);
    }
  }

  /**
   * Navigate forward in browser history.
   */
  async goForward() {
    try {
      await this.driver.navigate().forward();
      this.logger.info("Navigated forward");
    } catch (err) {
      this.logger.error(`Error navigating forward: ${err.message}`);
    }
  }

  /**
   * Get current URL.
   * @returns {Promise<string>} Current URL
   */
  async getCurrentUrl() {
    return await this.driver.getCurrentUrl();
  }

  /**
   * Get page title.
   * @returns {Promise<string>} Page title
   */
  async getPageTitle() {
    return await this.driver.getTitle();
  }

  /**
   * Get page source HTML.
   * @returns {Promise<string>} Page source
   */
  async getPageSource() {
    return await this.driver.getPageSource();
  }

  /**
   * Take screenshot and save to file.
   * @param {string} name - Optional name for screenshot file
   * @returns {Promise<string>} Path to saved screenshot
   */
  async takeScreenshot(name = "") {
    try {
      const timestamp = new Date()
        .toISOString()
        .replace(/:/g, "-")
        .replace(/\./g, "-");
      const filename = name
        ? `screenshot_${name}_${timestamp}.png`
        : `screenshot_${timestamp}.png`;
      const filepath = path.join(this.config.screenshotFolder, filename);

      const data = await this.driver.takeScreenshot();
      fs.writeFileSync(filepath, data, "base64");
      this.logger.info(`Screenshot saved: ${filepath}`);
      return filepath;
    } catch (err) {
      this.logger.error(`Error taking screenshot: ${err.message}`);
      return "";
    }
  }

  /**
   * Take screenshot of specific element.
   * @param {string|Object} locator - CSS selector, XPath, or By object
   * @param {string} name - Optional name for screenshot file
   * @returns {Promise<string>} Path to saved screenshot
   */
  async takeElementScreenshot(locator, name = "") {
    try {
      const element = await this.waitForElement(locator);
      if (element) {
        const timestamp = new Date()
          .toISOString()
          .replace(/:/g, "-")
          .replace(/\./g, "-");
        const filename = name
          ? `element_${name}_${timestamp}.png`
          : `element_${timestamp}.png`;
        const filepath = path.join(this.config.screenshotFolder, filename);

        const data = await element.takeScreenshot();
        fs.writeFileSync(filepath, data, "base64");
        this.logger.info(`Element screenshot saved: ${filepath}`);
        return filepath;
      }
      return "";
    } catch (err) {
      this.logger.error(`Error taking element screenshot: ${err.message}`);
      return "";
    }
  }

  /**
   * Sleep helper function.
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise<void>}
   */
  async _sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

module.exports = { CustomSelenium, SeleniumConfig };
