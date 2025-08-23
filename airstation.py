from time import sleep
import sys
import re
import os
import csv

import logging

from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import toml

# make logger
logger = logging.getLogger(__name__)

config = 'config.toml'

class AirStationWebsite():
    labels = ['unknown', 'allow', 'deny', 'limit']

    def __init__(self, config, logger=logger):
        tomlobj = toml.load(config)
        self.config = tomlobj['AirStation']
        self.devlist = tomlobj['Devices']['devlist']
        self.logger = logger
        self.driver = None
        self.device_dict = None
        self.device_reverse_dict = None

    def _driver_setup(self):
        '''make driver instance, old driver is gone
        '''
        self.logger.debug('chromedriver setup')
        chromedriver_options = ChromeOptions()
        chromedriver_options.add_argument('--headless')
        chromedriver_options.add_argument('--disable-gpu')
        del(self.driver)
        #self.driver = webdriver.Chrome(service=Service(),options=chromedriver_options)
        self.driver = webdriver.Remote(command_executor=os.environ['SELENIUM_URL'], options=chromedriver_options)

    def _is_enabled(self):
        '''driver is exists or not
        '''
        self.logger.debug('is enabled ???')
        return True if self.driver is not None else False

    def _is_logged_in(self):
        '''this class is logged in or not
        '''
        self.logger.debug('is logged in ???')
        if not self._is_enabled():
            return False
        login_base = self.driver.find_elements(By.ID, 'login_base')
        self.logger.debug(f'login_base length is {len(login_base)}')
        return False if len(login_base) > 0 else True

    def check_macaddr(self, macaddr):
        '''check macaddr is a MAC address or not
        '''
        # MACアドレスの正規表現パターン
        pattern = r'^([0-9A-Fa-f]{2}[:]){5}[0-9A-Fa-f]{2}$'

        # 正規表現で判定
        return bool(re.match(pattern, macaddr))

    def login(self):
        '''login to Air Station Config site
        '''
        self.logger.debug('get login page')
        if not self._is_enabled():
            self._driver_setup()

        try:
            self.driver.get(self.config['url'])
        except:
            raise Exception('cannot access AirStation')
        sleep(1)

        self.logger.debug('set ID/PW')
        try:
            element_username = self.driver.find_element(By.ID, 'form_USERNAME')
            element_username.clear()
            element_username.send_keys(self.config['username'])
            element_password = self.driver.find_element(By.ID, 'form_PASSWORD')
            element_password.send_keys(self.config['password'])

            button = self.driver.find_element(By.CLASS_NAME, 'button_login')
            button.click()
        except:
            raise Exception('cannot find login form')
        sleep(3)

        # 二重ログインの場合
        button = self.driver.find_elements(By.CLASS_NAME, 'button_login')
        if len(button) > 0:
            logger.debug('dupplicate login found')
            button[0].click()
        sleep(3)

    def _home(self):
        '''go to home and transit from beginning
        '''
        self.logger.debug('go to home')
        if not self._is_logged_in():
            self.login()
        try:
            home_icon = self.driver.find_element(By.CLASS_NAME, 'status_home')
            home_icon.click()
        except:
            self.screenshot('dump.png')
            raise Exception('cannot go to home')
        sleep(5)

    def logout(self):
        '''logout
        '''
        self.logger.info('logout')
        if not self._is_logged_in():
            return
        try:
            logout_icon = self.driver.find_element(By.CLASS_NAME, 'status_logout')
            logout_icon.click()
        except:
            self.screenshot('dump.png')
            raise Exception('cannot logout')

    def _kids_timer(self):
        '''open kids timer page
        '''
        self.logger.debug('open kids timer page')
        self._home()
        try:
            button = self.driver.find_element(By.ID, 'panel_CHILD_TIMER')
            button.click()
        except:
            raise Exception('cannot find child timer page')
        sleep(2)

    def get_device_list(self):
        '''get device name and mac addr from kids timer
        '''
        self.logger.debug('get_device_list')
        self._kids_timer()
        all_devices = []  # flat list of unknown, allow, deny, limit
        for j in range(4):
            for i in range(128):
                try:
                    panel = self.driver.find_element(By.ID, f'dev{j}_{i}')
                except:
                    raise Exception(f'cannot find dev{j}_{i} info')
                if not panel.is_displayed():
                    continue
                self.logger.debug(f'open dev{j}_{i} info')
                panel.click()
                devname = self.driver.find_element(By.ID, 'form_ct_name').get_attribute('value')
                mac = self.driver.find_element(By.ID, 'form_ct_mac').get_attribute('value')
                all_devices.append([i, f'dev{j}_{i}', devname, mac])
                buttons = self.driver.find_elements(By.CSS_SELECTOR, '#devctrl_ct_setting > .button_area > .button2')
                if len(buttons) < 2:
                    raise Exception('there is no return button')
                buttons[1].click()
        return all_devices

    def save_device_list(self):
        '''save devlist
        '''
        devlist = self.get_device_list()
        with open(self.devlist, 'w') as fobj:
            cobj = csv.writer(fobj)
            cobj.writerows(devlist)
        return devlist

    def load_device_list(self):
        '''load devlist from file or AirStation config site
        '''
        if os.path.isfile(self.devlist):
            with open(self.devlist, 'r') as fobj:
                cobj = csv.reader(fobj.read().rstrip().splitlines())
            all_devices = [row for row in cobj]
        else:
            all_devices = self.save_device_list()

        device_dict = {device[2]: device for device in all_devices}
        device_reverse_dict = {device[3]: device for device in all_devices}
        for key, device in device_dict.items():
            label_num = int(device[1][3])
            device_dict[key].append(self.labels[label_num])
        self.device_dict = device_dict
        self.device_reverse_dict = device_reverse_dict

    def _advanced_setting(self):
        '''open advanced setting page
        '''
        self.logger.debug('go to advanced setting page')
        self._home()
        try:
            button = self.driver.find_element(By.ID, 'panel_ADVANCED')
            button.click()
        except:
            self.screenshot('dump.png')
            raise Exception('cannot go to advanced setting page')
        sleep(2)

    def _menu_click(self, menu1, menu2):
        '''menu can be accessed in advanced setting page
        menu has 2 levels
        menu1 is 1st level and menu2 is 2nd level
        if menu2 is found, menu1 can be skipped
        '''
        self.logger.debug(f'open setting page {menu1} > {menu2}')

        self._advanced_setting()
        element_menu1 = self.driver.find_element(By.CLASS_NAME, menu1)
        submenu = self.driver.find_element(By.CLASS_NAME, 'MENU_' + menu1)
        if submenu.is_displayed() == False:
            self.driver.execute_script("arguments[0].style.display = 'block'", submenu)
        element_menu2 = self.driver.find_element(By.CLASS_NAME, menu2)
        element_menu2.click()
        sleep(5)

    def get_registered_devices(self):
        '''get registered device from mac filter page
        '''
        self._menu_click('WIRELESS', 'FILTER')
        iframe = self.driver.find_element(By.ID, 'content_main')
        self.driver.switch_to.frame(iframe)
        mac_list = []
        for td in self.driver.find_elements(By.CSS_SELECTOR, '#id_reg_list > tbody > tr > td'):
            buf = td.text.rstrip()
            if len(buf)>10:
                mac_list.append(buf)
        self.driver.switch_to.parent_frame()
        with open('latest_registered_list.csv', 'w') as fobj:
            fobj.write('\n'.join(mac_list))
        return mac_list

    def _edit_mac_list(self):
        '''push edit button
        '''
        logger.info('push edit button')
        button = self.driver.find_element(By.ID, 'label_t19_mac')
        button.click()
        sleep(5)

    def add_mac_addr(self, macaddr):
        '''add device mac addr
        '''
        if not self.check_macaddr(macaddr):
            raise Exception(f'{macaddr} is not MAC address')
        registered_list = self.get_registered_devices()  # to check dupplicate
        if macaddr in registered_list:
            raise Exception(f'{macaddr} has been already registered')
        else:
            self.logger.debug(f'{macaddr} is not registered')
        self.logger.info('push edit button')
        iframe = self.driver.find_element(By.ID, 'content_main')
        self.driver.switch_to.frame(iframe)
        button = self.driver.find_element(By.ID, 'label_t19_mac')
        button.click()
        sleep(5)

        textarea = self.driver.find_element(By.ID, 'id_wificontrollist')
        textarea.send_keys(macaddr)
        button = self.driver.find_element(By.ID, 'label_t7_mac_reg')
        button.click()
        sleep(5)
        self.driver.switch_to.parent_frame()
        return True

    def del_mac_addr(self, macaddr):
        '''del device mac addr
        '''
        if not self.check_macaddr(macaddr):
            raise Exception(f'{macaddr} is not MAC address')
        registered_list = self.get_registered_devices()  # to check dupplicate
        if macaddr in registered_list:
            self.logger.debug(f'{macaddr} has been registered')
            idx = registered_list.index(macaddr)
        else:
            raise Exception(f'{macaddr} is not registered')
        self.logger.info('push edit button')
        iframe = self.driver.find_element(By.ID, 'content_main')
        self.driver.switch_to.frame(iframe)
        button = self.driver.find_element(By.ID, 'label_t19_mac')
        button.click()
        sleep(5)

        if self.driver.find_element(By.ID, f'mac_text{idx}').text == macaddr:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, f'#mac_status{idx} > input')
            for button in buttons:
                if button.get_attribute('value') == '削除':
                    button.click()
                    sleep(5)
                    break
            else:
                raise Exception(f'{macaddr} button is strange!!!')
        else:
            raise Exception(f'{macaddr} is not found in edit page')
            #buttons = self.driver.find_elements(By.CSS_SELECTOR, f'#id_reg_list > tbody > tr > td > input')
            #for button in buttons:
            #    self.logger.warning(button.get_attribute('value'))
        self.driver.switch_to.parent_frame()
        return True

    def add_device(self, devname):
        '''add devname from mac addr config
        '''
        if self.device_dict is None:
            self.load_device_list()
        if devname not in self.device_dict:
            raise Exception(f'device {devname} is not found in device list')
        else:
            macaddr = self.device_dict[devname][3]
        return self.add_mac_addr(macaddr)

    def del_device(self, devname):
        '''del devname from mac addr config
        '''
        if self.device_dict is None:
            self.load_device_list()
        if devname not in self.device_dict:
            raise Exception(f'device {devname} is not found in device list')
        else:
            macaddr = self.device_dict[devname][3]
        return self.del_mac_addr(macaddr)

    def screenshot(self, filename):
        '''for debug, save screenshot now
        '''
        if self.driver is not None:
            self.driver.save_screenshot(filename)

    def exit(self):
        self.logout()
        if self._is_enabled():
            self.driver.quit()

if __name__ == '__main__':
    ASsite = AirStationWebsite(config, logger)
    ASsite.save_device_list()
    ASsite.exit()
