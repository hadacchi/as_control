from time import sleep
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

import toml


loglevel = logging.DEBUG
#loglevel = logging.INFO
formatter = logging.Formatter('%(asctime)s %(module)s: %(levelname)s: %(message)s')

logger = logging.getLogger()
logger.setLevel(loglevel)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.debug('setup logger')

logger.debug('chromedriver setup')
chromedriver_options = ChromeOptions()
chromedriver_options.add_argument('--headless')
chromedriver_options.add_argument('--disable-gpu')

logger.debug('load toml')
config = toml.load('config.toml')

logger.debug('access url')
url = 'http://192.168.1.101/login.html'
driver = webdriver.Chrome(service=Service(),options=chromedriver_options)
driver.get(url)

logger.debug('set form')
element_username = driver.find_element(By.ID, 'form_USERNAME')
element_username.send_keys(config['username'])
element_password = driver.find_element(By.ID, 'form_PASSWORD')
element_password.send_keys(config['password'])
button = driver.find_element(By.CLASS_NAME, 'button_login')
button.click()

logger.debug('sleep')
sleep(5)

logger.debug('get screenshot')
driver.save_screenshot('test.png')

logger.debug('finished')
driver.quit()
