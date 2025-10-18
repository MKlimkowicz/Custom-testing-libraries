using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using OpenQA.Selenium.Interactions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Threading;

namespace CustomSeleniumLibrary
{
    /// <summary>
    /// Configuration class for CustomSelenium
    /// </summary>
    public class SeleniumConfig
    {
        public TimeSpan DefaultTimeout { get; set; } = TimeSpan.FromSeconds(10);
        public string ScreenshotFolder { get; set; } = "screenshots";
        public bool AutoScreenshotOnError { get; set; } = false;
        public TimeSpan PollingInterval { get; set; } = TimeSpan.FromMilliseconds(500);
        public int RetryCount { get; set; } = 3;
        public bool HighlightElements { get; set; } = false;
        public bool LogPerformance { get; set; } = false;
    }

    public class CustomSelenium
    {
        private readonly IWebDriver driver;
        private readonly SeleniumConfig config;

        /// <summary>
        /// Initialize CustomSelenium wrapper.
        /// </summary>
        /// <param name="driver">Selenium WebDriver instance</param>
        /// <param name="config">Optional SeleniumConfig for custom settings</param>
        public CustomSelenium(IWebDriver driver, SeleniumConfig config = null)
        {
            this.driver = driver;
            this.config = config ?? new SeleniumConfig();

            // Create screenshot folder
            if (!Directory.Exists(this.config.ScreenshotFolder))
            {
                Directory.CreateDirectory(this.config.ScreenshotFolder);
            }
        }

        // ====================== LOCATOR UTILITIES ======================

        /// <summary>
        /// Parse locator and auto-detect strategy.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <returns>By locator</returns>
        private By ParseLocator(object locator)
        {
            if (locator is By byLocator)
            {
                return byLocator;
            }

            string locatorString = locator.ToString();

            // Auto-detect locator type
            if (locatorString.StartsWith("//") || locatorString.StartsWith("(//"))
            {
                return By.XPath(locatorString);
            }
            else if (locatorString.StartsWith("#") && !locatorString.Contains(" "))
            {
                return By.Id(locatorString.Substring(1));
            }
            else if (locatorString.StartsWith(".") && !locatorString.Contains(" "))
            {
                return By.ClassName(locatorString.Substring(1));
            }
            else
            {
                return By.CssSelector(locatorString);
            }
        }

        // ====================== ELEMENT FINDING ======================

        /// <summary>
        /// Find a single element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <returns>WebElement or null if not found</returns>
        public IWebElement FindElement(object locator)
        {
            try
            {
                By by = ParseLocator(locator);
                IWebElement element = driver.FindElement(by);
                if (element != null && config.HighlightElements)
                {
                    HighlightElementInternal(element);
                }
                return element;
            }
            catch (NoSuchElementException)
            {
                Console.WriteLine($"No element found with locator {locator}");
                return null;
            }
        }

        /// <summary>
        /// Find multiple elements.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <returns>List of WebElements (empty if none found)</returns>
        public IReadOnlyCollection<IWebElement> FindElements(object locator)
        {
            try
            {
                By by = ParseLocator(locator);
                IReadOnlyCollection<IWebElement> elements = driver.FindElements(by);
                return elements ?? new List<IWebElement>();
            }
            catch (NoSuchElementException)
            {
                Console.WriteLine($"No elements found with locator {locator}");
                return new List<IWebElement>();
            }
        }

        /// <summary>
        /// Find a specific element from a list by index.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="index">Zero-based index</param>
        /// <returns>WebElement or null if not found</returns>
        public IWebElement FindSpecificElement(object locator, int index = 0)
        {
            try
            {
                IReadOnlyCollection<IWebElement> elements = FindElements(locator);
                if (elements != null && elements.Count > index)
                {
                    IWebElement element = elements.ElementAt(index);
                    if (config.HighlightElements)
                    {
                        HighlightElementInternal(element);
                    }
                    return element;
                }
                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"No element found with index {index} in locator {locator}: {ex.Message}");
                return null;
            }
        }

        // ====================== WAITING METHODS ======================

        /// <summary>
        /// Wait for element to be present in DOM.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>WebElement or null if timeout occurs</returns>
        public IWebElement WaitForElement(object locator, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;
            DateTime startTime = DateTime.Now;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                IWebElement element = wait.Until(ExpectedConditions.ElementExists(by));

                if (config.LogPerformance)
                {
                    TimeSpan elapsed = DateTime.Now - startTime;
                    Console.WriteLine($"Element found in {elapsed.TotalSeconds:F2}s: {locator}");
                }

                if (element != null && config.HighlightElements)
                {
                    HighlightElementInternal(element);
                }
                return element;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for element: {locator}");
                if (config.AutoScreenshotOnError)
                {
                    TakeScreenshot($"timeout_{locator.ToString().Substring(0, Math.Min(30, locator.ToString().Length))}");
                }
                return null;
            }
        }

        /// <summary>
        /// Wait for elements to be present in DOM.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>List of WebElements (empty if timeout occurs)</returns>
        public IReadOnlyCollection<IWebElement> WaitForElements(object locator, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                wait.Until(ExpectedConditions.PresenceOfAllElementsLocatedBy(by));
                return driver.FindElements(by);
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for elements: {locator}");
                return new List<IWebElement>();
            }
        }

        /// <summary>
        /// Wait for specific element by index.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="index">Zero-based index</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>WebElement or null if timeout occurs</returns>
        public IWebElement WaitForSpecificElement(object locator, int index = 0, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };

                wait.Until(driver =>
                {
                    var elements = driver.FindElements(by);
                    return elements.Count > index;
                });

                var foundElements = driver.FindElements(by);
                return foundElements.Count > index ? foundElements.ElementAt(index) : null;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for element at index {index}: {locator}");
                return null;
            }
        }

        /// <summary>
        /// Wait until element becomes invisible or removed from DOM.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if element became invisible, false if timeout</returns>
        public bool WaitUntilElementInvisible(object locator, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.InvisibilityOfElementLocated(by));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for invisibility: {locator}");
                return false;
            }
        }

        /// <summary>
        /// Wait for text to be present in element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="text">Expected text</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if text appears, false if timeout</returns>
        public bool WaitForTextInElement(object locator, string text, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.TextToBePresentInElementLocated(by, text));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for text '{text}' in element: {locator}");
                return false;
            }
        }

        /// <summary>
        /// Wait for text to NOT be present in element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="text">Text that should not be present</param>
        /// <param name="index">Element index if multiple elements match</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if text is not present, false if timeout or error</returns>
        public bool WaitForTextNotInElement(object locator, string text, int index = 0, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };

                return wait.Until(driver =>
                {
                    var elements = driver.FindElements(by);
                    if (elements.Count > index)
                    {
                        return elements.ElementAt(index).Text != text;
                    }
                    return false;
                });
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for text '{text}' to disappear from: {locator}");
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in WaitForTextNotInElement: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Wait until URL matches exactly.
        /// </summary>
        /// <param name="url">Expected URL</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if URL matches, false if timeout</returns>
        public bool WaitUntilUrlIs(string url, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.UrlToBe(url));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for URL to be: {url}");
                return false;
            }
        }

        /// <summary>
        /// Wait until URL contains substring.
        /// </summary>
        /// <param name="url">Expected URL substring</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if URL contains substring, false if timeout</returns>
        public bool WaitUntilUrlContains(string url, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.UrlContains(url));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for URL to contain: {url}");
                return false;
            }
        }

        /// <summary>
        /// Wait until page title contains substring.
        /// </summary>
        /// <param name="title">Expected title substring</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if title contains substring, false if timeout</returns>
        public bool WaitUntilTitleContains(string title, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.TitleContains(title));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for title to contain: {title}");
                return false;
            }
        }

        // ====================== ADVANCED WAITING ======================

        /// <summary>
        /// Wait for element to be stable (not moving/animating).
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="stabilityTime">Time element must remain stable (milliseconds)</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>WebElement or null if timeout</returns>
        public IWebElement WaitForElementStable(object locator, int stabilityTime = 500, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;
            DateTime endTime = DateTime.Now.Add(timeout.Value);

            IWebElement element = WaitForElement(locator, timeout);
            if (element == null)
            {
                return null;
            }

            try
            {
                System.Drawing.Point? lastLocation = null;
                DateTime? stableStart = null;

                while (DateTime.Now < endTime)
                {
                    try
                    {
                        System.Drawing.Point currentLocation = element.Location;

                        if (lastLocation.HasValue && currentLocation == lastLocation.Value)
                        {
                            if (!stableStart.HasValue)
                            {
                                stableStart = DateTime.Now;
                            }
                            else if ((DateTime.Now - stableStart.Value).TotalMilliseconds >= stabilityTime)
                            {
                                Console.WriteLine($"Element stable: {locator}");
                                return element;
                            }
                        }
                        else
                        {
                            stableStart = null;
                        }

                        lastLocation = currentLocation;
                        Thread.Sleep(100);
                    }
                    catch (StaleElementReferenceException)
                    {
                        element = WaitForElement(locator, TimeSpan.FromSeconds(5));
                        if (element == null)
                        {
                            return null;
                        }
                        lastLocation = null;
                        stableStart = null;
                    }
                }

                Console.WriteLine($"Element did not stabilize: {locator}");
                return element;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error waiting for stable element: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Wait for specific number of elements.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="expectedCount">Expected number of elements</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if count matches, false if timeout</returns>
        public bool WaitForElementCount(object locator, int expectedCount, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };

                return wait.Until(driver =>
                {
                    var elements = driver.FindElements(by);
                    return elements.Count == expectedCount;
                });
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for {expectedCount} elements: {locator}");
                return false;
            }
        }

        /// <summary>
        /// Wait for page to fully load (document ready state).
        /// </summary>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if page loaded, false if timeout</returns>
        public bool WaitForPageLoad(TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };

                return wait.Until(driver =>
                {
                    IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
                    return js.ExecuteScript("return document.readyState").ToString() == "complete";
                });
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine("Timeout waiting for page load");
                return false;
            }
        }

        // ====================== ELEMENT STATE CHECKS ======================

        /// <summary>
        /// Check if element is displayed.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <returns>True if element is displayed</returns>
        public bool IsElementDisplayed(object locator)
        {
            IWebElement element = FindElement(locator);
            return element != null && element.Displayed;
        }

        /// <summary>
        /// Wait for element to be clickable.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>Clickable WebElement or null if timeout</returns>
        public IWebElement IsElementClickable(object locator, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                IWebElement element = wait.Until(ExpectedConditions.ElementToBeClickable(by));
                if (element != null && config.HighlightElements)
                {
                    HighlightElementInternal(element);
                }
                return element;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Element not clickable: {locator}");
                return null;
            }
        }

        /// <summary>
        /// Check if page title matches exactly.
        /// </summary>
        /// <param name="title">Expected title</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if title matches, false if timeout</returns>
        public bool CheckThatTitleIs(string title, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                return wait.Until(ExpectedConditions.TitleIs(title));
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Title does not match '{title}', current: {driver.Title}");
                return false;
            }
        }

        /// <summary>
        /// Check if page title does not contain text.
        /// </summary>
        /// <param name="text">Text that should not be in title</param>
        /// <returns>True if title doesn't contain text</returns>
        public bool CheckThatTitleDoesNotContain(string text)
        {
            return !driver.Title.Contains(text);
        }

        /// <summary>
        /// Wait for all matching elements to be visible.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>List of visible WebElements (empty if timeout)</returns>
        public IReadOnlyCollection<IWebElement> WaitUntilElementsVisible(object locator, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                By by = ParseLocator(locator);
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value)
                {
                    PollingInterval = config.PollingInterval
                };
                wait.Until(ExpectedConditions.VisibilityOfAllElementsLocatedBy(by));
                return driver.FindElements(by);
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine($"Timeout waiting for elements visibility: {locator}");
                return new List<IWebElement>();
            }
        }

        // ====================== ELEMENT INTERACTIONS ======================

        /// <summary>
        /// Get attribute value from element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="attribute">Attribute name</param>
        /// <param name="index">Element index if multiple elements match</param>
        /// <returns>Attribute value or null</returns>
        public string GetAttributeFromElement(object locator, string attribute, int index = 0)
        {
            IReadOnlyCollection<IWebElement> elements = WaitForElements(locator);
            return elements.Count > index ? elements.ElementAt(index).GetAttribute(attribute) : null;
        }

        /// <summary>
        /// Move mouse to element using Actions.
        /// </summary>
        /// <param name="element">WebElement to move mouse to</param>
        public void MoveMouse(IWebElement element)
        {
            try
            {
                Actions actions = new Actions(driver);
                actions.MoveToElement(element).Perform();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error moving mouse to element: {ex.Message}");
            }
        }

        /// <summary>
        /// Scroll element into view.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="index">Element index if multiple elements match</param>
        public void ScrollToElement(object locator, int index = 0)
        {
            IReadOnlyCollection<IWebElement> elements = WaitForElements(locator);
            if (elements.Count > index)
            {
                IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
                js.ExecuteScript(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    elements.ElementAt(index)
                );
                Thread.Sleep(300); // Allow scroll to complete
            }
        }

        /// <summary>
        /// Convert list of elements to list of text values.
        /// </summary>
        /// <param name="elements">List of WebElements</param>
        /// <param name="readHidden">If true, gets textContent (includes hidden text)</param>
        /// <returns>List of text values</returns>
        public List<string> ElementListToText(IReadOnlyCollection<IWebElement> elements, bool readHidden = false)
        {
            return elements.Select(element =>
                readHidden ? element.GetAttribute("textContent") : element.Text
            ).ToList();
        }

        // ====================== IFRAME HANDLING ======================

        /// <summary>
        /// Switch to iframe by locator or index.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, By object, or integer index</param>
        public void SwitchToIframe(object locator)
        {
            try
            {
                if (locator is int index)
                {
                    driver.SwitchTo().Frame(index);
                }
                else
                {
                    IWebElement iframe = WaitForElement(locator);
                    if (iframe != null)
                    {
                        driver.SwitchTo().Frame(iframe);
                    }
                    else
                    {
                        throw new NoSuchElementException($"Iframe not found: {locator}");
                    }
                }
                Console.WriteLine($"Switched to iframe: {locator}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error switching to iframe: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Switch back to main page content from iframe.
        /// </summary>
        public void SwitchToDefaultContent()
        {
            try
            {
                driver.SwitchTo().DefaultContent();
                Console.WriteLine("Switched to default content");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error switching to default content: {ex.Message}");
            }
        }

        /// <summary>
        /// Switch to parent frame.
        /// </summary>
        public void SwitchToParentFrame()
        {
            try
            {
                driver.SwitchTo().ParentFrame();
                Console.WriteLine("Switched to parent frame");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error switching to parent frame: {ex.Message}");
            }
        }

        // ====================== ALERT HANDLING ======================

        /// <summary>
        /// Accept alert/confirm dialog.
        /// </summary>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if alert was accepted, false if no alert</returns>
        public bool AcceptAlert(TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value);
                wait.Until(ExpectedConditions.AlertIsPresent());
                IAlert alert = driver.SwitchTo().Alert();
                alert.Accept();
                Console.WriteLine("Alert accepted");
                return true;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine("No alert present");
                return false;
            }
        }

        /// <summary>
        /// Dismiss alert/confirm dialog.
        /// </summary>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if alert was dismissed, false if no alert</returns>
        public bool DismissAlert(TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value);
                wait.Until(ExpectedConditions.AlertIsPresent());
                IAlert alert = driver.SwitchTo().Alert();
                alert.Dismiss();
                Console.WriteLine("Alert dismissed");
                return true;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine("No alert present");
                return false;
            }
        }

        /// <summary>
        /// Get text from alert.
        /// </summary>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>Alert text or null if no alert</returns>
        public string GetAlertText(TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value);
                wait.Until(ExpectedConditions.AlertIsPresent());
                IAlert alert = driver.SwitchTo().Alert();
                return alert.Text;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine("No alert present");
                return null;
            }
        }

        /// <summary>
        /// Send text to prompt dialog.
        /// </summary>
        /// <param name="text">Text to send</param>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if text was sent, false if no alert</returns>
        public bool SendTextToAlert(string text, TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;

            try
            {
                WebDriverWait wait = new WebDriverWait(driver, timeout.Value);
                wait.Until(ExpectedConditions.AlertIsPresent());
                IAlert alert = driver.SwitchTo().Alert();
                alert.SendKeys(text);
                return true;
            }
            catch (WebDriverTimeoutException)
            {
                Console.WriteLine("No alert present");
                return false;
            }
        }

        // ====================== WINDOW HANDLING ======================

        /// <summary>
        /// Switch to window by handle.
        /// </summary>
        /// <param name="windowHandle">Window handle</param>
        public void SwitchToWindow(string windowHandle)
        {
            try
            {
                driver.SwitchTo().Window(windowHandle);
                Console.WriteLine($"Switched to window: {windowHandle}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error switching to window: {ex.Message}");
            }
        }

        /// <summary>
        /// Switch to newly opened window.
        /// </summary>
        /// <param name="timeout">Custom timeout (uses config default if null)</param>
        /// <returns>True if switched, false if no new window</returns>
        public bool SwitchToNewWindow(TimeSpan? timeout = null)
        {
            timeout = timeout ?? config.DefaultTimeout;
            var originalWindows = driver.WindowHandles;
            DateTime endTime = DateTime.Now.Add(timeout.Value);

            while (DateTime.Now < endTime)
            {
                var currentWindows = driver.WindowHandles;
                if (currentWindows.Count > originalWindows.Count)
                {
                    string newWindow = currentWindows.Except(originalWindows).FirstOrDefault();
                    if (newWindow != null)
                    {
                        driver.SwitchTo().Window(newWindow);
                        Console.WriteLine("Switched to new window");
                        return true;
                    }
                }
                Thread.Sleep(500);
            }

            Console.WriteLine("No new window opened");
            return false;
        }

        /// <summary>
        /// Close current window.
        /// </summary>
        public void CloseCurrentWindow()
        {
            try
            {
                driver.Close();
                Console.WriteLine("Closed current window");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error closing window: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all window handles.
        /// </summary>
        /// <returns>List of window handles</returns>
        public IReadOnlyCollection<string> GetWindowHandles()
        {
            return driver.WindowHandles;
        }

        // ====================== DROPDOWN HANDLING ======================

        /// <summary>
        /// Select dropdown option by value.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="value">Option value</param>
        public void SelectDropdownByValue(object locator, string value)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    SelectElement select = new SelectElement(element);
                    select.SelectByValue(value);
                    Console.WriteLine($"Selected dropdown value: {value}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error selecting dropdown by value: {ex.Message}");
            }
        }

        /// <summary>
        /// Select dropdown option by visible text.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="text">Option visible text</param>
        public void SelectDropdownByText(object locator, string text)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    SelectElement select = new SelectElement(element);
                    select.SelectByText(text);
                    Console.WriteLine($"Selected dropdown text: {text}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error selecting dropdown by text: {ex.Message}");
            }
        }

        /// <summary>
        /// Select dropdown option by index.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="index">Option index</param>
        public void SelectDropdownByIndex(object locator, int index)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    SelectElement select = new SelectElement(element);
                    select.SelectByIndex(index);
                    Console.WriteLine($"Selected dropdown index: {index}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error selecting dropdown by index: {ex.Message}");
            }
        }

        /// <summary>
        /// Get currently selected dropdown option text.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <returns>Selected option text or null</returns>
        public string GetSelectedDropdownOption(object locator)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    SelectElement select = new SelectElement(element);
                    return select.SelectedOption.Text;
                }
                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting selected option: {ex.Message}");
                return null;
            }
        }

        // ====================== ACTION CHAINS ======================

        /// <summary>
        /// Hover over element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        public void Hover(object locator)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    Actions actions = new Actions(driver);
                    actions.MoveToElement(element).Perform();
                    Console.WriteLine($"Hovered over element: {locator}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error hovering over element: {ex.Message}");
            }
        }

        /// <summary>
        /// Drag and drop element.
        /// </summary>
        /// <param name="sourceLocator">Source element locator</param>
        /// <param name="targetLocator">Target element locator</param>
        public void DragAndDrop(object sourceLocator, object targetLocator)
        {
            try
            {
                IWebElement source = WaitForElement(sourceLocator);
                IWebElement target = WaitForElement(targetLocator);
                if (source != null && target != null)
                {
                    Actions actions = new Actions(driver);
                    actions.DragAndDrop(source, target).Perform();
                    Console.WriteLine($"Dragged {sourceLocator} to {targetLocator}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in drag and drop: {ex.Message}");
            }
        }

        /// <summary>
        /// Double click element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        public void DoubleClick(object locator)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    Actions actions = new Actions(driver);
                    actions.DoubleClick(element).Perform();
                    Console.WriteLine($"Double clicked element: {locator}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error double clicking: {ex.Message}");
            }
        }

        /// <summary>
        /// Right click (context click) element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        public void RightClick(object locator)
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    Actions actions = new Actions(driver);
                    actions.ContextClick(element).Perform();
                    Console.WriteLine($"Right clicked element: {locator}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error right clicking: {ex.Message}");
            }
        }

        // ====================== COOKIE MANAGEMENT ======================

        /// <summary>
        /// Add cookie to browser.
        /// </summary>
        /// <param name="cookie">Cookie object</param>
        public void AddCookie(Cookie cookie)
        {
            try
            {
                driver.Manage().Cookies.AddCookie(cookie);
                Console.WriteLine($"Added cookie: {cookie.Name}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error adding cookie: {ex.Message}");
            }
        }

        /// <summary>
        /// Get cookie by name.
        /// </summary>
        /// <param name="name">Cookie name</param>
        /// <returns>Cookie object or null</returns>
        public Cookie GetCookie(string name)
        {
            try
            {
                return driver.Manage().Cookies.GetCookieNamed(name);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting cookie: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get all cookies.
        /// </summary>
        /// <returns>List of cookie objects</returns>
        public IReadOnlyCollection<Cookie> GetAllCookies()
        {
            try
            {
                return driver.Manage().Cookies.AllCookies;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting cookies: {ex.Message}");
                return new List<Cookie>();
            }
        }

        /// <summary>
        /// Delete cookie by name.
        /// </summary>
        /// <param name="name">Cookie name</param>
        public void DeleteCookie(string name)
        {
            try
            {
                driver.Manage().Cookies.DeleteCookieNamed(name);
                Console.WriteLine($"Deleted cookie: {name}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deleting cookie: {ex.Message}");
            }
        }

        /// <summary>
        /// Delete all cookies.
        /// </summary>
        public void DeleteAllCookies()
        {
            try
            {
                driver.Manage().Cookies.DeleteAllCookies();
                Console.WriteLine("Deleted all cookies");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deleting all cookies: {ex.Message}");
            }
        }

        // ====================== DEVELOPER UTILITIES ======================

        /// <summary>
        /// Highlight element temporarily for debugging.
        /// </summary>
        /// <param name="element">WebElement to highlight</param>
        /// <param name="duration">How long to highlight (milliseconds)</param>
        /// <param name="color">Highlight color</param>
        private void HighlightElementInternal(IWebElement element, int duration = 500, string color = "red")
        {
            try
            {
                IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
                string originalStyle = element.GetAttribute("style");
                js.ExecuteScript(
                    "arguments[0].setAttribute('style', arguments[1]);",
                    element,
                    $"border: 3px solid {color}; background-color: yellow;"
                );
                Thread.Sleep(duration);
                js.ExecuteScript(
                    "arguments[0].setAttribute('style', arguments[1]);",
                    element,
                    originalStyle ?? ""
                );
            }
            catch
            {
                // Silently ignore highlighting errors
            }
        }

        /// <summary>
        /// Manually highlight element for debugging.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="duration">How long to highlight (milliseconds)</param>
        public void HighlightElement(object locator, int duration = 1000)
        {
            IWebElement element = WaitForElement(locator);
            if (element != null)
            {
                HighlightElementInternal(element, duration);
            }
        }

        /// <summary>
        /// Execute JavaScript.
        /// </summary>
        /// <param name="script">JavaScript code</param>
        /// <param name="args">Arguments to pass to script</param>
        /// <returns>Script return value</returns>
        public object ExecuteScript(string script, params object[] args)
        {
            try
            {
                IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
                return js.ExecuteScript(script, args);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error executing script: {ex.Message}");
                return null;
            }
        }

        // ====================== PAGE UTILITIES ======================

        /// <summary>
        /// Refresh current page.
        /// </summary>
        public void RefreshPage()
        {
            try
            {
                driver.Navigate().Refresh();
                Console.WriteLine("Page refreshed");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error refreshing page: {ex.Message}");
            }
        }

        /// <summary>
        /// Navigate to URL.
        /// </summary>
        /// <param name="url">URL to navigate to</param>
        public void NavigateTo(string url)
        {
            try
            {
                driver.Navigate().GoToUrl(url);
                Console.WriteLine($"Navigated to: {url}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error navigating to URL: {ex.Message}");
            }
        }

        /// <summary>
        /// Navigate back in browser history.
        /// </summary>
        public void GoBack()
        {
            try
            {
                driver.Navigate().Back();
                Console.WriteLine("Navigated back");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error navigating back: {ex.Message}");
            }
        }

        /// <summary>
        /// Navigate forward in browser history.
        /// </summary>
        public void GoForward()
        {
            try
            {
                driver.Navigate().Forward();
                Console.WriteLine("Navigated forward");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error navigating forward: {ex.Message}");
            }
        }

        /// <summary>
        /// Get current URL.
        /// </summary>
        /// <returns>Current URL</returns>
        public string GetCurrentUrl()
        {
            return driver.Url;
        }

        /// <summary>
        /// Get page title.
        /// </summary>
        /// <returns>Page title</returns>
        public string GetPageTitle()
        {
            return driver.Title;
        }

        /// <summary>
        /// Get page source HTML.
        /// </summary>
        /// <returns>Page source</returns>
        public string GetPageSource()
        {
            return driver.PageSource;
        }

        // ====================== SCREENSHOT UTILITIES ======================

        /// <summary>
        /// Take screenshot and save to file.
        /// </summary>
        /// <param name="name">Optional name for screenshot file</param>
        /// <returns>Path to saved screenshot</returns>
        public string TakeScreenshot(string name = "")
        {
            try
            {
                string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                string filename = !string.IsNullOrEmpty(name)
                    ? $"screenshot_{name}_{timestamp}.png"
                    : $"screenshot_{timestamp}.png";
                string filepath = Path.Combine(config.ScreenshotFolder, filename);

                ITakesScreenshot takesScreenshot = (ITakesScreenshot)driver;
                Screenshot screenshot = takesScreenshot.GetScreenshot();
                screenshot.SaveAsFile(filepath, ScreenshotImageFormat.Png);
                
                Console.WriteLine($"Screenshot saved: {filepath}");
                return filepath;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error taking screenshot: {ex.Message}");
                return "";
            }
        }

        /// <summary>
        /// Take screenshot of specific element.
        /// </summary>
        /// <param name="locator">CSS selector, XPath, or By object</param>
        /// <param name="name">Optional name for screenshot file</param>
        /// <returns>Path to saved screenshot</returns>
        public string TakeElementScreenshot(object locator, string name = "")
        {
            try
            {
                IWebElement element = WaitForElement(locator);
                if (element != null)
                {
                    string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                    string filename = !string.IsNullOrEmpty(name)
                        ? $"element_{name}_{timestamp}.png"
                        : $"element_{timestamp}.png";
                    string filepath = Path.Combine(config.ScreenshotFolder, filename);

                    Screenshot screenshot = ((ITakesScreenshot)element).GetScreenshot();
                    screenshot.SaveAsFile(filepath, ScreenshotImageFormat.Png);
                    
                    Console.WriteLine($"Element screenshot saved: {filepath}");
                    return filepath;
                }
                return "";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error taking element screenshot: {ex.Message}");
                return "";
            }
        }
    }
}

