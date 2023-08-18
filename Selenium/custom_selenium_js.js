const { Builder, By, until, Key } = require("selenium-webdriver");
const logging = require("winston");
const fs = require("fs");
const path = require("path");

const default_timeout = 10000;

class CustomSelenium {
  constructor(driver) {
    this.driver = driver;
  }

  async findElement(locator) {
    try {
      const element = await this.driver.findElement(By.css(locator));
      return element;
    } catch (err) {
      logging.error(`No element found with locator ${locator}`);
      return null;
    }
  }

  async findElements(locator) {
    try {
      const elements = await this.driver.findElements(By.css(locator));
      return elements;
    } catch (err) {
      logging.error(`No elements found with locator ${locator}`);
      return [];
    }
  }

  async findSpecificElement(locator, index = 0) {
    try {
      const elements = await this.findElements(locator);
      return elements[index];
    } catch (err) {
      logging.error(
        `No element found with index ${index} in locator ${locator}`
      );
      return null;
    }
  }

  async waitForElement(locator, timeout = default_timeout) {
    try {
      const element = await this.driver.wait(
        until.elementLocated(By.css(locator)),
        timeout
      );
      return element;
    } catch (err) {
      logging.error(
        `Timeout while waiting for element with locator ${locator}`
      );
      return null;
    }
  }

  async waitForElements(locator, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const elements = await this.driver.findElements(By.css(locator));
        return elements.length > 0;
      }, timeout);
      const elements = await this.driver.findElements(By.css(locator));
      return elements;
    } catch (err) {
      logging.error(
        `Timeout while waiting for elements with locator ${locator}`
      );
      return [];
    }
  }

  async waitForSpecificElement(locator, index = 0, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const elements = await this.driver.findElements(By.css(locator));
        return elements.length > index;
      }, timeout);
      const elements = await this.driver.findElements(By.css(locator));
      return elements[index];
    } catch (err) {
      logging.error(
        `Timeout while waiting for element with index ${index} in locator ${locator}`
      );
      return null;
    }
  }

  async waitUntilElementInvisible(locator, timeout = default_timeout) {
    try {
      const element = await this.driver.wait(
        until.elementIsNotVisible(this.driver.findElement(By.css(locator))),
        timeout
      );
      return true;
    } catch (err) {
      logging.error(
        `Timeout while waiting for invisibility of element with locator ${locator}`
      );
      return false;
    }
  }

  async waitForTextInElement(locator, text, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const element = await this.driver.findElement(By.css(locator));
        return element.getText().then((value) => value.includes(text));
      }, timeout);
      return true;
    } catch (err) {
      logging.error(
        `Timeout while waiting for text to be present in element with locator ${locator}`
      );
      return false;
    }
  }

  async waitUntilUrlIs(url, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const currentUrl = await this.driver.getCurrentUrl();
        return currentUrl === url;
      }, timeout);
      return true;
    } catch (err) {
      logging.error(`Timeout while waiting for URL to be ${url}`);
      return false;
    }
  }

  async waitUntilUrlContains(url, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const currentUrl = await this.driver.getCurrentUrl();
        return currentUrl.includes(url);
      }, timeout);
      return true;
    } catch (err) {
      logging.error(`Timeout while waiting for URL to contain ${url}`);
      return false;
    }
  }

  async waitUntilTitleContains(title, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const currentTitle = await this.driver.getTitle();
        return currentTitle.includes(title);
      }, timeout);
      return true;
    } catch (err) {
      logging.error(`Timeout while waiting for title to contain ${title}`);
      return false;
    }
  }

  async isElementDisplayed(locator) {
    try {
      const element = await this.findElement(locator);
      return await element.isDisplayed();
    } catch (err) {
      logging.error(`No element found with locator ${locator}`);
      return false;
    }
  }

  async isElementClickable(locator, timeout = default_timeout) {
    try {
      await this.driver.wait(
        until.elementIsVisible(this.findElement(locator)),
        timeout
      );
      const element = await this.findElement(locator);
      if (element) {
        await this.driver.wait(until.elementIsEnabled(element), timeout);
        return element;
      }
    } catch (err) {
      logging.error(`No clickable element found for locator: ${locator}`);
      return null;
    }
  }

  async checkThatTitleIs(title, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const currentTitle = await this.driver.getTitle();
        return currentTitle === title;
      }, timeout);
      return true;
    } catch (err) {
      logging.error(`Timeout while checking if title is ${title}`);
      return false;
    }
  }

  async checkThatTitleDoesNotContain(text) {
    const currentTitle = await this.driver.getTitle();
    return !currentTitle.includes(text);
  }

  async areElementsVisible(locator, timeout = default_timeout) {
    try {
      await this.driver.wait(async () => {
        const elements = await this.driver.findElements(By.css(locator));
        return elements.every((element) => element.isDisplayed());
      }, timeout);
      const elements = await this.driver.findElements(By.css(locator));
      return elements;
    } catch (err) {
      logging.error(
        `Timeout while waiting for visibility of elements with locator ${locator}`
      );
      return [];
    }
  }

  async getAttributeFromElement(locator, attribute, index = 0) {
    const elements = await this.waitForElements(locator);
    if (elements) {
      return await elements[index].getAttribute(attribute);
    } else {
      return null;
    }
  }

  async moveMouse(element) {
    await this.driver.executeScript("arguments[0].scrollIntoView();", element);
  }

  async scrollToElement(locator, index = 0) {
    const elements = await this.waitForElements(locator);
    if (elements) {
      await this.driver.executeScript(
        "arguments[0].scrollIntoView();",
        elements[index]
      );
    }
  }

  async elementListToText(list_of_elements, read_hidden = false) {
    const textList = [];
    for (let i = 0; i < list_of_elements.length; i++) {
      if (read_hidden) {
        const textContent = await list_of_elements[i].getAttribute(
          "textContent"
        );
        textList.push(textContent);
      } else {
        const text = await list_of_elements[i].getText();
        textList.push(text);
      }
    }
    return textList;
  }

  async refreshPage() {
    await this.driver.navigate().refresh();
  }

  async takeScreenshot(name = "") {
    try {
      let timestamp = new Date().toISOString().replace(/:/g, "");
      let fileName = `test_${name}_${timestamp}.png`;
      let folderName = "folder_name";
      fs.mkdirSync(folderName, { recursive: true });
      let filePath = path.join(folderName, fileName);
      let data = await this.driver.takeScreenshot();
      fs.writeFileSync(filePath, data, "base64");
    } catch (err) {
      logging.error(`Failed to take screenshot: ${err}`);
    }
  }
}
