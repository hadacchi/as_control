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

# make logger
#loglevel = logging.DEBUG
loglevel = logging.INFO
formatter = logging.Formatter('%(asctime)s %(module)s: %(levelname)s: %(message)s')

logger = logging.getLogger()
logger.setLevel(loglevel)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)

class AirStationWebsite():
    def __init__(self, config, url, logger=logger):
        self.config = toml.load(config)
        self.url = url
        self.logger = logger
        self.driver = None

    def _driver_setup(self):
        '''make driver instance, old driver is gone
        '''
        self.logger.info('chromedriver setup')
        chromedriver_options = ChromeOptions()
        chromedriver_options.add_argument('--headless')
        chromedriver_options.add_argument('--disable-gpu')
        del(self.driver)
        self.driver = webdriver.Chrome(service=Service(),options=chromedriver_options)

    def login(self):
        '''login to Air Station Config site
        '''
        self.logger.info('get login page')
        self._driver_setup()
        self.driver.get(self.url)
        sleep(1)

        self.logger.info('set form values')
        element_username = self.driver.find_element(By.ID, 'form_USERNAME')
        element_username.clear()
        element_username.send_keys(self.config['username'])
        element_password = self.driver.find_element(By.ID, 'form_PASSWORD')
        element_password.send_keys(self.config['password'])
        self.logger.info('click button')
        button = self.driver.find_element(By.CLASS_NAME, 'button_login')
        button.click()
        sleep(3)

        # 二重ログインの場合
        button = self.driver.find_elements(By.CLASS_NAME, 'button_login')
        if len(button) > 0:
            logger.info('dupplicate login found')
            button[0].click()
        sleep(3)

    def _home(self):
        '''go to home and transit from beginning
        '''
        self.logger.info('go to home')
        if self.driver is None:
            self.login()
        try:
            home_icon = self.driver.find_element(By.CLASS_NAME, 'status_home')
            home_icon.click()
        except:
            self.login()
            home_icon = self.driver.find_element(By.CLASS_NAME, 'status_home')
            home_icon.click()
        sleep(5)

    def advanced_setting(self):
        '''open advanced setting page
        '''
        self.logger.info('go to advanced setting page')
        self._home()
        button = self.driver.find_element(By.ID, 'panel_ADVANCED')
        button.click()
        sleep(2)

    def _menu_click(self, menu1, menu2, i=0):
        '''menu can be accessed in advanced setting page
        menu has 2 levels
        menu1 is 1st level and menu2 is 2nd level
        if menu2 is found, menu1 can be skipped
        '''
        self.logger.info(f'open setting page {menu1} > {menu2}')
        if i > 2:
            self.logger.info(f'already called {__name__} in {i} times')
            return

        if self.driver is None:
            self.advanced_setting()

        element_menu1 = self.driver.find_element(By.CLASS_NAME, menu1)
        submenu = self.driver.find_element(By.CLASS_NAME, 'MENU_' + menu1)
        if submenu.is_displayed() == False:
            self.driver.execute_script("arguments[0].style.display = 'block'", submenu)
        element_menu2 = self.driver.find_element(By.CLASS_NAME, menu2)

        element_menu2.click()
        sleep(5)

    def screenshot(self, filename):
        '''for debug, save screenshot now
        '''
        if self.driver is not None:
            self.driver.save_screenshot(filename)
    
    def tmp(self):
        self._menu_click('WIRELESS', 'FILTER')
        self.screenshot('test.png')


    def exit(self):
        if self.driver is not None:
            self.driver.quit()

config = 'config.toml'
url = 'http://192.168.1.101/login.html'

ASsite = AirStationWebsite(config, url, logger)
#ASsite.advanced_setting()
#ASsite.screenshot('test.png')
ASsite.tmp()
ASsite.exit()
