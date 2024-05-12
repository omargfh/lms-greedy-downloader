
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import os
import time
import json

import pickle

from console import info, error, success, warning, cprint
from constants import ENDL
from canvas_helpers import ellipsis

# Selenium driver helpers
def get_executable_path():
    return ChromeDriverManager().install()

def get_driver(options, executable_path=None):
    service = ChromeService(executable_path=ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    return browser

def login(driver, loginURL):
    driver.get(loginURL)
    time.sleep(5)
    input("Press Enter to continue...")
    return driver

def request(driver, url, timeout=2):
    driver.get(url)
    time.sleep(timeout)
    return driver.page_source

def request_json(driver, url, timeout=2):
    try:
        response = request(driver, url, timeout)
        inner_text = response.split("<pre>")[1].split("</pre>")[0]
        return json.loads(inner_text)
    except Exception as e:
        error(f"Failed to request JSON at {url}")
        return []

def download(driver, domain, url, path, use_cookies=False, override_cookies=None):
    # We simulate the request using cURL as if it was from Selenium to
    # control the download location
    # Get all cookies related to the domain
    cookies = []
    if use_cookies:
        driver.get(domain)
        time.sleep(3)
        try:
            cookies = driver.get_cookies()
        except Exception as e:
            error("XXX - " + e)
            cookies = []

    if override_cookies:
        cookies = override_cookies

    cURL = f"curl -L -b '"
    for cookie in cookies:
        cURL += f"{cookie['name']}={cookie['value']};"
    cURL += f"' -o '{path}' {url}"
    os.system(cURL)

    return cookies


def download_multiple(driver, entries):
    failed = 0

    info(f"> Downloading {len(entries)} files...")
    cookies = None
    for (i, (domain, url, path)) in enumerate(entries):
        try:
            info(f"~~~ Downloading {ellipsis(url, 20)} to {ellipsis(path, 20)}")
            if i == 0:
                cookies = download(driver, domain, url, path, True)
            else:
                download(driver, domain, url, path, False, cookies)
            success(f"--- Downloaded {ellipsis(url, 20)} to {ellipsis(path, 20)}. Queue length: {len(entries)-i-1}", end=ENDL)
        except Exception as e:
            failed += 1
            error(f"XXX - Failed to download {ellipsis(url)} to {ellipsis(path)}")
            error(f"URL: {url}")
            error(f"Path: {path}")
            error(f"Error Message: {e}")

    success(f"> Downloaded {len(entries)-failed}/{len(entries)} (success: {(len(entries)-failed)/len(entries)*100:.2f}%)")


def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver, path):
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie)