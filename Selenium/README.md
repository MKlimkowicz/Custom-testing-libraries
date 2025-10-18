# Custom Selenium Library

A comprehensive, feature-rich Selenium wrapper library designed to simplify web automation testing. Available in Python, JavaScript, and C# with full feature parity across all platforms.

## 🌟 Features

### Core Capabilities
- **Multi-Locator Strategy Support** - Auto-detect or explicitly use CSS, XPath, ID, Class Name, and more
- **Advanced Waiting Mechanisms** - Smart waits for stability, element counts, page loads, and custom conditions
- **Configurable Settings** - Customize timeouts, screenshot folders, polling intervals, and more
- **Enhanced Error Handling** - Auto-screenshots on errors, detailed logging, and performance metrics
- **Common Selenium Operations** - iframes, alerts, windows, dropdowns, cookies, and action chains
- **Developer-Friendly** - Element highlighting, fluent API support, and comprehensive documentation


## 📦 Installation

### Python
```bash
pip install selenium
```

### JavaScript
```bash
npm install selenium-webdriver winston
```

### C#
```bash
dotnet add package Selenium.WebDriver
dotnet add package Selenium.Support
```

## 🚀 Quick Start

### Python

```python
from selenium import webdriver
from custom_selenium_python import CustomSelenium, SeleniumConfig

# Basic usage
driver = webdriver.Chrome()
selenium = CustomSelenium(driver)

# With configuration
config = SeleniumConfig(
    default_timeout=15,
    screenshot_folder="test_screenshots",
    auto_screenshot_on_error=True,
    highlight_elements=True,
    log_performance=True
)
selenium = CustomSelenium(driver, config)

# Navigate and interact
selenium.navigate_to("https://example.com")
selenium.wait_for_element("#login-button").click()
selenium.wait_for_element("#username").send_keys("user@example.com")
```

### JavaScript

```javascript
const { Builder } = require("selenium-webdriver");
const { CustomSelenium, SeleniumConfig } = require("./custom_selenium_js");

// Basic usage
const driver = await new Builder().forBrowser("chrome").build();
const selenium = new CustomSelenium(driver);

// With configuration
const config = new SeleniumConfig({
  defaultTimeout: 15000,
  screenshotFolder: "test_screenshots",
  autoScreenshotOnError: true,
  highlightElements: true,
  logPerformance: true,
});
const selenium = new CustomSelenium(driver, config);

// Navigate and interact
await selenium.navigateTo("https://example.com");
const loginBtn = await selenium.waitForElement("#login-button");
await loginBtn.click();
```

### C#

```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using CustomSeleniumLibrary;

// Basic usage
IWebDriver driver = new ChromeDriver();
CustomSelenium selenium = new CustomSelenium(driver);

// With configuration
SeleniumConfig config = new SeleniumConfig
{
    DefaultTimeout = TimeSpan.FromSeconds(15),
    ScreenshotFolder = "test_screenshots",
    AutoScreenshotOnError = true,
    HighlightElements = true,
    LogPerformance = true
};
CustomSelenium selenium = new CustomSelenium(driver, config);

// Navigate and interact
selenium.NavigateTo("https://example.com");
selenium.WaitForElement("#login-button").Click();
```

## 📚 API Documentation

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_timeout` | int/TimeSpan | 10s | Default wait timeout |
| `screenshot_folder` | string | "screenshots" | Folder for screenshots |
| `auto_screenshot_on_error` | bool | false | Auto-capture on errors |
| `polling_interval` | float/TimeSpan | 0.5s | Wait polling frequency |
| `retry_count` | int | 3 | Retry attempts for flaky operations |
| `highlight_elements` | bool | false | Highlight elements when found |
| `log_performance` | bool | false | Log timing metrics |

### Multi-Locator Support

All methods accept multiple locator formats:

```python
# CSS Selector (default)
element = selenium.find_element(".my-class")
element = selenium.find_element("div > button")

# Auto-detected XPath
element = selenium.find_element("//button[@id='submit']")

# Auto-detected ID
element = selenium.find_element("#submit-button")

# Auto-detected Class
element = selenium.find_element(".btn-primary")

# Explicit By strategy (Python)
from selenium.webdriver.common.by import By
element = selenium.find_element((By.NAME, "username"))

# Explicit By strategy (JavaScript)
const { By } = require("selenium-webdriver");
element = await selenium.findElement(By.name("username"));

# Explicit By strategy (C#)
element = selenium.FindElement(By.Name("username"));
```

### Element Finding

```python
# Find single element
element = selenium.find_element("#submit")

# Find multiple elements
elements = selenium.find_elements(".list-item")

# Find specific element by index
third_item = selenium.find_specific_element(".list-item", 2)
```

### Waiting Methods

```python
# Wait for element presence
element = selenium.wait_for_element("#dynamic-content")

# Wait for elements
elements = selenium.wait_for_elements(".data-row")

# Wait for specific element by index
element = selenium.wait_for_specific_element(".item", 3)

# Wait for element to be invisible
selenium.wait_until_element_invisible("#loading-spinner")

# Wait for text in element
selenium.wait_for_text_in_element("#status", "Success")

# Wait for text NOT in element
selenium.wait_for_text_not_in_element("#status", "Loading")

# Wait for URL
selenium.wait_until_url_contains("/dashboard")
selenium.wait_until_url_is("https://example.com/home")

# Wait for title
selenium.wait_until_title_contains("Dashboard")
```

### Advanced Waiting

```python
# Wait for element to stabilize (stop moving/animating)
stable_element = selenium.wait_for_element_stable("#animated-div", stability_time=1.0)

# Wait for specific element count
selenium.wait_for_element_count(".list-item", expected_count=10)

# Wait for page to fully load
selenium.wait_for_page_load()

# Check if element is clickable
clickable_btn = selenium.is_element_clickable("#submit")
```

### iframe Handling

```python
# Switch to iframe by locator
selenium.switch_to_iframe("#payment-iframe")

# Switch to iframe by index
selenium.switch_to_iframe(0)

# Switch back to main content
selenium.switch_to_default_content()

# Switch to parent frame
selenium.switch_to_parent_frame()
```

### Alert Handling

```python
# Accept alert
selenium.accept_alert()

# Dismiss alert
selenium.dismiss_alert()

# Get alert text
text = selenium.get_alert_text()

# Send text to prompt
selenium.send_text_to_alert("Hello")
selenium.accept_alert()
```

### Window Handling

```python
# Get all window handles
handles = selenium.get_window_handles()

# Switch to window by handle
selenium.switch_to_window(handles[1])

# Switch to newly opened window
selenium.switch_to_new_window()

# Close current window
selenium.close_current_window()
```

### Dropdown Handling

```python
# Select by value
selenium.select_dropdown_by_value("#country", "USA")

# Select by visible text
selenium.select_dropdown_by_text("#country", "United States")

# Select by index
selenium.select_dropdown_by_index("#country", 0)

# Get selected option
selected = selenium.get_selected_dropdown_option("#country")
```

### Action Chains

```python
# Hover over element
selenium.hover("#menu-item")

# Drag and drop
selenium.drag_and_drop("#draggable", "#droppable")

# Double click
selenium.double_click("#file-name")

# Right click (context menu)
selenium.right_click("#file-name")

# Send keys with modifier (Ctrl+A, Ctrl+C, etc.)
selenium.send_keys_with_modifier("#text-area", "CONTROL", "a")
```

### Cookie Management

```python
# Add cookie
selenium.add_cookie({"name": "session", "value": "abc123"})

# Get cookie
cookie = selenium.get_cookie("session")

# Get all cookies
cookies = selenium.get_all_cookies()

# Delete cookie
selenium.delete_cookie("session")

# Delete all cookies
selenium.delete_all_cookies()
```

### Screenshots

```python
# Take full page screenshot
path = selenium.take_screenshot("login_page")

# Take element screenshot
path = selenium.take_element_screenshot("#error-message", "error")
```

### Developer Utilities

```python
# Highlight element for debugging
selenium.highlight_element("#submit", duration=2.0)

# Execute JavaScript
result = selenium.execute_script("return document.title")

# Scroll to element
selenium.scroll_to_element("#footer")

# Get element attribute
href = selenium.get_attribute_from_element("a", "href")

# Convert element list to text
elements = selenium.find_elements(".names")
names = selenium.element_list_to_text(elements)
```

### Page Navigation

```python
# Navigate to URL
selenium.navigate_to("https://example.com")

# Refresh page
selenium.refresh_page()

# Go back
selenium.go_back()

# Go forward
selenium.go_forward()

# Get current URL
url = selenium.get_current_url()

# Get page title
title = selenium.get_page_title()

# Get page source
html = selenium.get_page_source()
```

## 🔍 Feature Comparison Across Languages

| Feature | Python | JavaScript | C# |
|---------|--------|------------|-----|
| Multi-locator support | ✅ | ✅ | ✅ |
| Configuration system | ✅ | ✅ | ✅ |
| Advanced waits | ✅ | ✅ | ✅ |
| iframe handling | ✅ | ✅ | ✅ |
| Alert handling | ✅ | ✅ | ✅ |
| Window handling | ✅ | ✅ | ✅ |
| Dropdown helpers | ✅ | ✅ | ✅ |
| Action chains | ✅ | ✅ | ✅ |
| Cookie management | ✅ | ✅ | ✅ |
| Element highlighting | ✅ | ✅ | ✅ |
| Auto-screenshot on error | ✅ | ✅ | ✅ |
| Performance logging | ✅ | ✅ | ✅ |

## 💡 Advanced Examples

### Example 1: Complete Login Flow with Error Handling

```python
from selenium import webdriver
from custom_selenium_python import CustomSelenium, SeleniumConfig

# Configure with auto-screenshot on errors
config = SeleniumConfig(
    auto_screenshot_on_error=True,
    screenshot_folder="test_failures"
)

driver = webdriver.Chrome()
selenium = CustomSelenium(driver, config)

try:
    # Navigate to login page
    selenium.navigate_to("https://example.com/login")
    
    # Wait for page to load
    selenium.wait_for_page_load()
    
    # Fill in credentials
    selenium.wait_for_element("#username").send_keys("user@example.com")
    selenium.wait_for_element("#password").send_keys("password123")
    
    # Submit form
    selenium.wait_for_element("#login-btn").click()
    
    # Wait for redirect
    selenium.wait_until_url_contains("/dashboard")
    
    # Verify login success
    assert selenium.wait_for_text_in_element("#welcome", "Welcome")
    
finally:
    driver.quit()
```

### Example 2: Working with Dynamic Content

```python
# Wait for element to stabilize before interacting
slider = selenium.wait_for_element_stable("#animated-slider", stability_time=1.0)

# Wait for specific number of items to load
selenium.wait_for_element_count(".product-card", expected_count=20)

# Scroll element into view smoothly
selenium.scroll_to_element("#load-more-button")

# Click when stable and visible
selenium.is_element_clickable("#load-more-button").click()
```

### Example 3: Handling Multiple Windows

```javascript
// Open new window
await driver.findElement(By.id("open-window")).click();

// Switch to new window
await selenium.switchToNewWindow();

// Perform actions in new window
const title = await selenium.getPageTitle();
console.log(`New window title: ${title}`);

// Close new window and switch back
await selenium.closeCurrentWindow();
const handles = await selenium.getWindowHandles();
await selenium.switchToWindow(handles[0]);
```

### Example 4: Working with iframes

```python
# Switch to payment iframe
selenium.switch_to_iframe("#stripe-payment-iframe")

# Fill in credit card details
selenium.wait_for_element("#card-number").send_keys("4242424242424242")
selenium.wait_for_element("#expiry").send_keys("12/25")
selenium.wait_for_element("#cvc").send_keys("123")

# Switch back to main content
selenium.switch_to_default_content()

# Submit order
selenium.wait_for_element("#submit-order").click()
```

### Example 5: Debugging with Element Highlighting

```python
config = SeleniumConfig(highlight_elements=True, log_performance=True)
selenium = CustomSelenium(driver, config)

# Elements will automatically highlight when found
element = selenium.wait_for_element("#submit")  # Highlights in yellow

# Manual highlighting for specific debugging
selenium.highlight_element("#error-message", duration=3.0)
```

## 🐛 Troubleshooting

### Element Not Found
```python
# Increase timeout for slow-loading elements
element = selenium.wait_for_element("#slow-element", timeout=30)

# Use different locator strategy
element = selenium.wait_for_element("//div[@data-test='slow-element']")

# Wait for element to be stable
element = selenium.wait_for_element_stable("#animated-element")
```

### Stale Element Reference
```python
# Use wait methods that re-find elements
selenium.wait_for_text_in_element("#status", "Complete")

# Re-find element before interaction
element = selenium.wait_for_element("#dynamic-button")
element.click()
```

### Element Not Clickable
```python
# Wait for element to be clickable
clickable = selenium.is_element_clickable("#button", timeout=10)
if clickable:
    clickable.click()

# Scroll element into view first
selenium.scroll_to_element("#button")
selenium.wait_for_element("#button").click()

# Use JavaScript click as fallback
element = selenium.wait_for_element("#button")
selenium.execute_script("arguments[0].click();", element)
```

### Timeouts
```python
# Adjust global timeout
config = SeleniumConfig(default_timeout=20)

# Adjust specific wait timeout
element = selenium.wait_for_element("#slow", timeout=30)

# Adjust polling interval for faster checks
config = SeleniumConfig(polling_interval=0.1)
```

## 🔧 Best Practices

### 1. Use Configuration Objects
```python
# Create reusable configuration
test_config = SeleniumConfig(
    default_timeout=15,
    auto_screenshot_on_error=True,
    highlight_elements=False,  # Disable in CI/CD
    log_performance=True
)
```

### 2. Prefer Waiting Over Sleeping
```python
# ❌ Bad
time.sleep(5)
element.click()

# ✅ Good
selenium.wait_for_element("#button").click()

# ✅ Even Better
selenium.is_element_clickable("#button").click()
```

### 3. Use Smart Locators
```python
# ❌ Fragile - relies on structure
selenium.find_element("div > div > span:nth-child(3)")

# ✅ Better - use semantic attributes
selenium.find_element("[data-testid='submit-button']")
selenium.find_element("#submit-btn")
```

### 4. Handle Errors Gracefully
```python
# Use auto-screenshot for debugging
config = SeleniumConfig(auto_screenshot_on_error=True)

# Check element existence before interaction
if selenium.wait_for_element("#optional-button", timeout=5):
    selenium.find_element("#optional-button").click()
```

### 5. Clean Up Resources
```python
try:
    selenium.navigate_to("https://example.com")
    # Test code here
finally:
    driver.quit()
```

## 📋 Method Reference

### Element Finding
- `find_element(locator)` - Find single element
- `find_elements(locator)` - Find multiple elements
- `find_specific_element(locator, index)` - Find element by index

### Basic Waiting
- `wait_for_element(locator, timeout)` - Wait for presence
- `wait_for_elements(locator, timeout)` - Wait for multiple
- `wait_for_specific_element(locator, index, timeout)` - Wait for specific
- `wait_until_element_invisible(locator, timeout)` - Wait for invisibility
- `wait_for_text_in_element(locator, text, timeout)` - Wait for text
- `wait_for_text_not_in_element(locator, text, index, timeout)` - Wait for text absence
- `wait_until_url_is(url, timeout)` - Wait for exact URL
- `wait_until_url_contains(url, timeout)` - Wait for URL substring
- `wait_until_title_contains(title, timeout)` - Wait for title substring

### Advanced Waiting
- `wait_for_element_stable(locator, stability_time, timeout)` - Wait for stability
- `wait_for_element_count(locator, count, timeout)` - Wait for element count
- `wait_for_page_load(timeout)` - Wait for page ready

### State Checks
- `is_element_displayed(locator)` - Check visibility
- `is_element_clickable(locator, timeout)` - Check clickability
- `check_that_title_is(title, timeout)` - Verify title
- `check_that_title_does_not_contain(text)` - Verify title absence
- `are_elements_visible(locator, timeout)` - Wait for multiple visible

### Interactions
- `get_attribute_from_element(locator, attribute, index)` - Get attribute
- `move_mouse(element)` - Move mouse to element
- `scroll_to_element(locator, index)` - Scroll into view
- `element_list_to_text(elements, read_hidden)` - Extract text

### Navigation
- `navigate_to(url)` - Go to URL
- `refresh_page()` - Reload page
- `go_back()` - Browser back
- `go_forward()` - Browser forward
- `get_current_url()` - Get URL
- `get_page_title()` - Get title
- `get_page_source()` - Get HTML

### Screenshots
- `take_screenshot(name)` - Full page screenshot
- `take_element_screenshot(locator, name)` - Element screenshot

### Utilities
- `highlight_element(locator, duration)` - Highlight for debugging
- `execute_script(script, *args)` - Run JavaScript

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all three language implementations stay in sync
5. Submit a pull request

## 📄 License

This library is provided as-is for educational and testing purposes.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the examples for common patterns

## 🔄 Changelog

### v2.0.0 (Current)
- ✅ Fixed critical bugs in all three implementations
- 🚀 Added multi-locator strategy support
- 🚀 Added configuration system
- 🚀 Added 50+ new methods for complete Selenium coverage
- 🚀 Added advanced waiting mechanisms
- 🚀 Added iframe, alert, window, dropdown, and cookie support
- 🚀 Added action chains (hover, drag-drop, double-click, etc.)
- 🚀 Added developer utilities (highlighting, performance logging)
- 📚 Comprehensive documentation with examples
- ✨ Full feature parity across Python, JavaScript, and C#

### v1.0.0
- Initial release with basic Selenium wrapper functionality
