using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using System;
using System.Collections.Generic;
using System.Linq;

public class CustomSelenium
{
    private IWebDriver driver;
    private WebDriverWait wait;

    public CustomSelenium(IWebDriver driver, TimeSpan timeout)
    {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, timeout);
    }

    public IWebElement FindElement(By locator)
    {
        try
        {
            return driver.FindElement(locator);
        }
        catch (NoSuchElementException)
        {
            Console.WriteLine($"No element found with locator {locator}");
            return null;
        }
    }

    public IReadOnlyCollection<IWebElement> FindElements(By locator)
    {
        try
        {
            return driver.FindElements(locator);
        }
        catch (NoSuchElementException)
        {
            Console.WriteLine($"No elements found with locator {locator}");
            return new List<IWebElement>();
        }
    }

    public IWebElement WaitForElement(By locator)
    {
        try
        {
            return wait.Until(ExpectedConditions.ElementExists(locator));
        }
        catch (WebDriverTimeoutException)
        {
            Console.WriteLine($"Timeout while waiting for element with locator {locator}");
            return null;
        }
    }

    public IReadOnlyCollection<IWebElement> WaitForElements(By locator)
    {
        try
        {
            wait.Until(ExpectedConditions.PresenceOfAllElementsLocatedBy(locator));
            return driver.FindElements(locator);
        }
        catch (WebDriverTimeoutException)
        {
            Console.WriteLine($"Timeout while waiting for elements with locator {locator}");
            return new List<IWebElement>();
        }
    }

    public bool IsElementDisplayed(By locator)
    {
        IWebElement element = FindElement(locator);
        return element != null && element.Displayed;
    }

    public bool IsElementClickable(By locator)
    {
        try
        {
            wait.Until(ExpectedConditions.ElementToBeClickable(locator));
            return true;
        }
        catch (WebDriverTimeoutException)
        {
            Console.WriteLine($"Element with locator {locator} is not clickable");
            return false;
        }
    }

    public bool CheckTitleIs(string title)
    {
        try
        {
            wait.Until(ExpectedConditions.TitleIs(title));
            return true;
        }
        catch (WebDriverTimeoutException)
        {
            Console.WriteLine($"Timeout while waiting for title to be {title}");
            return false;
        }
    }

    public bool CheckTitleDoesNotContain(string text)
    {
        return !driver.Title.Contains(text);
    }

    public IReadOnlyCollection<IWebElement> WaitUntilElementsVisible(By locator)
    {
        try
        {
            wait.Until(ExpectedConditions.VisibilityOfAllElementsLocatedBy(locator));
            return driver.FindElements(locator);
        }
        catch (WebDriverTimeoutException)
        {
            Console.WriteLine($"Timeout while waiting for visibility of elements with locator {locator}");
            return new List<IWebElement>();
        }
    }

    public string GetAttributeFromElement(By locator, string attribute, int index = 0)
    {
        IReadOnlyCollection<IWebElement> elements = WaitForElements(locator);
        return index < elements.Count ? elements.ElementAt(index).GetAttribute(attribute) : null;
    }

    public void ScrollToElement(By locator, int index = 0)
    {
        IReadOnlyCollection<IWebElement> elements = WaitForElements(locator);
        if (index < elements.Count)
        {
            ((IJavaScriptExecutor)driver).ExecuteScript("arguments[0].scrollIntoView(true);", elements.ElementAt(index));
        }
    }

    public List<string> ElementListToText(IReadOnlyCollection<IWebElement> elements, bool readHidden = false)
    {
        return elements.Select(element => readHidden ? element.GetAttribute("textContent") : element.Text).ToList();
    }

    public void RefreshPage()
    {
        driver.Navigate().Refresh();
    }

    public void TakeScreenshot(string name = "")
    {
        try
        {
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string fileName = $"test_{name}_{timestamp}.png";
            string folderName = "folder_name";

            System.IO.Directory.CreateDirectory(folderName);

            string filePath = System.IO.Path.Combine(folderName, fileName);

            ITakesScreenshot takesScreenshot = (ITakesScreenshot)this.driver;

            Screenshot screenshot = takesScreenshot.GetScreenshot();
            screenshot.SaveAsFile(filePath, ScreenshotImageFormat.Png);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to take screenshot: {ex}");
        }
    }
}
