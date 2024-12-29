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



def get_url(host, page):
    return '/'.join(['http:/',host,page])


# make logger
#loglevel = logging.DEBUG
loglevel = logging.INFO
formatter = logging.Formatter('%(asctime)s %(module)s: %(levelname)s: %(message)s')

logger = logging.getLogger()
logger.setLevel(loglevel)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)


#
logger.info('chromedriver setup')
chromedriver_options = ChromeOptions()
chromedriver_options.add_argument('--headless')
chromedriver_options.add_argument('--disable-gpu')

#
logger.info('load toml')
config = toml.load('config.toml')

#
logger.info('setup access url')
url = 'http://192.168.1.101/login.html'

#
logger.info('get login page')
driver = webdriver.Chrome(service=Service(),options=chromedriver_options)
driver.get(url)

logger.info('set form values')
element_username = driver.find_element(By.ID, 'form_USERNAME')
element_username.clear()
element_username.send_keys(config['username'])
element_password = driver.find_element(By.ID, 'form_PASSWORD')
element_password.send_keys(config['password'])

logger.info('click button')
button = driver.find_element(By.CLASS_NAME, 'button_login')
button.click()

sleep(1)

logger.info('go to advanced setting page')
button = driver.find_element(By.ID, 'panel_ADVANCED')
button.click()

sleep(1)

logger.info('open WIERLESS menu')
element_menu = driver.find_element(By.CLASS_NAME, 'WIRELESS')
element_menu.click()

sleep(1)

logger.info('open FILTER setting page')
element_menu = driver.find_element(By.CLASS_NAME, 'FILTER')
element_menu.click()

sleep(1)

logger.info('go into iframe')
#iframe = driver.find_element(By.CSS_SELECTOR, '#content_load_area > iframe')
iframe = driver.find_element(By.ID, 'content_main')
driver.switch_to.frame(iframe)

sleep(1)

logger.info('push edit button')
button = driver.find_element(By.ID, 'label_t19_mac')
button.click()

sleep(5)

# textarea
textarea = driver.find_element(By.ID, 'id_wificontrollist')
button = driver.find_element(By.ID, 'label_t7_mac_reg')

logger.info('get mac addr')
mac_list = []
for td in driver.find_elements(By.CSS_SELECTOR, '#id_reg_list > tbody > tr > td'):
    #logger.info(td.text.rstrip())
    mac_list.append(td.text.rstrip())

fix_button = driver.find_element(By.CSS_SELECTOR, '#mac_status0 > input[value="修正"]')
fix_button.click()

sleep(5)
driver.save_screenshot('latest.png')

logger.info('finished')
driver.switch_to.parent_frame()
driver.find_element(By.CLASS_NAME, 'status_logout').click()
sleep(2)
driver.quit()
