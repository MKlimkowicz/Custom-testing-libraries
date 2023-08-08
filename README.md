# Custom Selenium Library

The Custom Selenium Library is a collection of utilities designed to simplify automation testing with Selenium. It provides convenient methods for common actions and assertions, making it easier to write clean and efficient test scripts. This library has been implemented in Python, JavaScript, and C# with the same functionalities across all platforms.

## Features

- **Finding Elements**: Easily find single or multiple elements by CSS selector.
- **Waiting for Elements**: Various waiting functions, including waiting for an element to be visible, invisible, clickable, etc.
- **Working with Text**: Waiting for specific text to be present or absent in elements.
- **URL and Title Assertions**: Verifying the current URL or title of the page.
- **Visibility Checks**: Check if elements are displayed or clickable.
- **Mouse Movement**: Move the mouse to specific elements.
- **Scrolling**: Scroll to specific elements.
- **Converting Elements to Text**: Convert a list of elements to text.
- **Refreshing Pages**: Easily refresh the current page.
- **Screenshot Capturing**: Capture and save screenshots of the current state of the webpage.

## Getting Started

To get started, simply import the `CustomSelenium` class into your test file and initialize it with a Selenium WebDriver instance.

```python
from custom_selenium_python import CustomSelenium

custom_selenium = CustomSelenium(driver)

## Finding and Clicking an Element
element = custom_selenium.find_element('#button')
element.click()

## Waiting for an Element to be Visible
element = custom_selenium.wait_for_element('#loading-element')

## Taking a Screenshot
custom_selenium.take_screenshot('screenshot_name')

```javascript
const { Builder } = require("selenium-webdriver");
const CustomSelenium = require("./custom_selenium_js"); 

const driver = new Builder().forBrowser('chrome').build();  
const customSelenium = new CustomSelenium(driver);

## Finding and Interacting with an Element
const element = await customSelenium.findElement('#button');
await element.click();

## Finding Multiple Elements
const elements = await customSelenium.findElements('.class-name');

## Finding a Specific Element from a List
const thirdElement = await customSelenium.findSpecificElement('.items', 2);  // 0-based index

## Waiting for an Element to be Located
const element = await customSelenium.waitForElement('#loading-element');

## Taking a Screenshot
await customSelenium.takeScreenshot('screenshot_name');

```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;

IWebDriver driver = new ChromeDriver(); 
TimeSpan timeout = TimeSpan.FromSeconds(10); 

CustomSelenium customSelenium = new CustomSelenium(driver, timeout);

## Finding an Element
var element = customSelenium.FindElement(By.Id("button"));

## Waiting for an Element to be Located
var element = customSelenium.WaitForElement(By.Id("loading-element"));

## Checking if an Element is Displayed
bool isDisplayed = customSelenium.IsElementDisplayed(By.Id("element-id"));

## Taking a Screenshot
customSelenium.TakeScreenshot("screenshot_name");
