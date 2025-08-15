import platform
from shutil import which
import os
import time
import fitz
from PIL import Image, ImageChops
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml.html.clean as clean
import lxml.html as LH
from fastmcp import FastMCP

url_mcp = FastMCP("URL Extractor MCP")


# Import tesseract
system = platform.system()
tesseract_path = which('tesseract')
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    if system == 'Windows':
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
    elif system == 'Darwin':  # macOS
        common_paths = [
            '/opt/homebrew/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/usr/bin/tesseract'
        ]
    else:  # Linux and others
        common_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]

    for path in common_paths:
        if os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path


@url_mcp.tool()
def read_url(url: str, screenshot: bool) -> str:
    """
    Extract data from web page given URL by reading html content, also taking screenshots and using pytesseract
    :param url: URL string to web page
    :param screenshot: whether to take screenshots for OCR
    Send the input as {'url': 'url_value', screenshot: screenshot_bool_value}
    :return: content of the URL page
    """
    try:
        options = webdriver.ChromeOptions()  # Use ChromeOptions for Chrome
        options.add_argument('--headless=new')
        options.add_argument('--incognito')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        # Navigate to the web page
        driver.get(url)
        # Wait for the page to fully load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        text = []
        if screenshot:  # taking screenshots
            scroll_height = 540
            screenshots = []
            last_image = None
            while True:
                # Take a screenshot of the current viewport
                driver.save_screenshot(f'screenshot_{len(screenshots) + 1}.png')
                current_image = Image.open(f'screenshot_{len(screenshots) + 1}.png')
                if last_image:  # Avoid loops
                    images_are_identical = ImageChops.difference(last_image, current_image).getbbox() is None
                    if images_are_identical:
                        os.remove(f'screenshot_{len(screenshots) + 1}.png')
                        break
                screenshots.append(f'screenshot_{len(screenshots) + 1}.png')
                last_image = current_image.copy()
                # Scroll the web page
                driver.execute_script(f'window.scrollTo(0, {(len(screenshots) + 1) * scroll_height});')
                time.sleep(1)
                # Break when reach the end
                if driver.execute_script("return window.scrollY + window.innerHeight >= document.body.scrollHeight"):
                    break
            for screenshot in screenshots:
                # Extract text and remove screenshots
                image = Image.open(screenshot)
                page_text = pytesseract.image_to_string(image)
                text.append(page_text)
                os.remove(screenshot)
        # reading and filtering html tags and contents
        content = driver.page_source
        cleaner = clean.Cleaner()
        content = cleaner.clean_html(content)
        doc = LH.fromstring(content)
        for elt in doc.iterdescendants():
            if elt.tag in ('script', 'noscript', 'style'): continue
            txt = elt.text or ''
            tail = elt.tail or ''
            text.append(' '.join((txt, tail)).strip())
        driver.quit()
        text =". ".join(text)
        return text
    except Exception as e:
        return (f"Error happened during read_url call: {e}"
                f"Check the error and if possible, try again.")


if __name__ == "__main__":
    url_mcp.run(transport="stdio")