import sys
import requests
import re
import os

import logging

from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
chromedriver_options = ChromeOptions()
chromedriver_options.add_argument('--headless')
chromedriver_options.add_argument('--disable-gpu')
#loglevel = logging.DEBUG
loglevel = logging.INFO
formatter = logging.Formatter('%(asctime)s %(module)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(loglevel)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.debug('setup logger')
url = 'http://192.168.1.101/login.html'
driver = webdriver.Chrome(service=Service(),options=chromedriver_options)
driver.get(url)
driver.save_screenshot('test.png')
driver.quit()
