"""
This is the main file. Run this file after providing the credentials in 'info.properties' file.
"""

import datetime
import os
import platform
import random as rn
import sys
import time

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import FacebookPostType as fb_post_type
import PublicPage as public_page
import mongodb
from PropertiesReader import properties
from debug import debug


def element(driver, xpath):
    while True:
        try:
            elem = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            return elem
        except Exception as e:
            print("Timeout: ", e)


def image_video_exclude(flag=False, chromeOptions=webdriver.ChromeOptions):
    if flag:
        prefs = {'profile.managed_default_content_settings.images': 2}
        chromeOptions.add_experimental_option("prefs", prefs)
    return chromeOptions


class FacebookScraper:

    def __init__(self):
        self.dbag = debug(name=self.__class__, flag=True)
        self.driver = self.driver_settings()

    def login(self, username=properties().email, password=properties().password):
        """

        :param username: your facebook username or email
        :param password: your facebook password
        Logging into our own profile
        """
        driver = self.driver
        try:

            driver.get("https://en-gb.facebook.com")
            driver.maximize_window()

            # filling the form
            driver.find_element_by_name('email').send_keys(username)
            driver.implicitly_wait(20)
            driver.find_element_by_name('pass').send_keys(password)
            # clicking on login button
            driver.find_element_by_id('loginbutton').click()
            self.dbag.debug_print("Function login\nLogin Successful...")
            time.sleep(3)
            return driver
        except Exception as e:
            self.dbag.debug_print("There's some error in log in. " + str(e))
            self.dbag.debug_print(sys.exc_info()[0])
            exit()

    def public_page_data_scrape(self, login=False, page_name=properties().pagename):
        """

        :param login: if true then prog will login to facebook,else scrape data without loging
        :param page_name: name of the public page that you want to scrape
        """
        if login:
            self.driver = self.login(properties().email, properties().password)
        driver = self.driver
        driver.get('https://www.facebook.com/pg/' + page_name + '/posts/?ref=page_internal')
        time.sleep(3)
        facebook_post_type = fb_post_type.FacebookPostType(
            post_type="Public Page")  # here default post type is public page

        div_counter = 1
        local_count = 0
        total_post = 1

        post_path = facebook_post_type.public_page_div_path_generator(counter=div_counter)
        main_div = driver.find_elements_by_xpath(post_path)
        connection = mongodb.Connection(db_name="Newspaper", db_col=page_name + "_news_data")
        while main_div:
            div_html = main_div[local_count].get_attribute("innerHTML")
            post_info = public_page.PostParser(div_html)
            post_title, post_summary, post_date = post_info.public_post_title(), post_info.public_post_subtitle(), post_info.date()
            post_like, post_comment, post_share = post_info.likes_count(), post_info.comments_count(), post_info.share_count()
            post_url = post_info.public_post_url()

            if post_title != 0:
                data = {"id": str(total_post), "title": post_title, "summary": post_summary,
                        "likes": post_like, "share": post_share, "comment": post_comment,
                        "date": post_date, "url": post_url}
                self.dbag.debug_print(str(data).encode("utf-8").decode())
                connection.insert(data)
                total_post += 1

            if total_post % 50 == 0:
                self.dbag.debug_print("Total post: " + str(total_post))
                self.dbag.debug_print("Going to sleep...")
                time.sleep(rn.randint(10, 40))
                process = psutil.Process(os.getpid())
                self.dbag.debug_print("Memory info: " + str(process.memory_percent()))

            if local_count == main_div.__len__() - 1:
                div_counter += 1
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight-" + str(rn.randint(300, 700)) + ");")
                driver.implicitly_wait(rn.randint(10, 43))
                post_path = facebook_post_type.public_page_div_path_generator(counter=div_counter)
                main_div = element(driver, post_path)
                self.dbag.debug_print("Current Post in Queue: " + str(main_div.__len__()))
                local_count = -1
            local_count += 1

            if total_post == properties().TOTAL_POST_NUMBER:
                break

    def write_in_friends_wall(self, friendId, msg, wishtime=properties().wishtime):
        self.driver = self.login(properties().email, properties().password)
        driver = self.driver
        driver.get('https://www.facebook.com/' + friendId)
        driver.find_element_by_class_name("_3nd0").click()
        div = driver.find_element_by_xpath("//div[@class='_5rp7']")
        actions = ActionChains(driver)
        actions.move_to_element(div).send_keys(msg).perform()
        while True:
            date = datetime.datetime.now()
            # set the time here
            if date.strftime("%Y-%m-%d %H:%M:%S") == wishtime:
                driver.find_element_by_xpath("//button[@class='_1mf7 _4jy0 _4jy3 _4jy1 _51sy selected _42ft']").click()
                break
        driver.close()
        exit()

    def send_private_msg(self, friendId, msg):
        self.driver = self.login(properties().email, properties().password)
        driver = self.driver
        for id in friendId:
            try:
                driver.get('https://www.facebook.com/messages/t/' + id)
                while True:
                    date = datetime.datetime.now()
                    if date.strftime("%Y-%m-%d %H:%M:%S") == properties().wishtime:
                        driver.find_element_by_class_name("_5rpb").click()
                        div = driver.find_element_by_xpath("//div[@class='_1mf _1mj']")
                        actions = ActionChains(driver)
                        actions.move_to_element(div).send_keys(msg).send_keys(Keys.ENTER).perform()
                        break
            except Exception as e:
                # if self.usesSharedContainer():
                #    # Can happen when sharing the driver across tests,
                #    # e.g. when test ended on page the causes a refresh alert
                #    # This simplifies handling the alert
                print("Automatically accepting alert: {0}".format(str(e)))
                Alert(self.driver).accept()

    def driver_settings(self):
        # all the setting regarding the browser and os is here
        # make sure that  your browser driver is in the correct path

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("headless")
        # if flag=True
        options = image_video_exclude(flag=True, chromeOptions=options)
        try:
            platform_ = platform.system().lower()
            if platform_ in ['linux', 'darwin']:
                driver = webdriver.Chrome(executable_path="./chromedriver", options=options)  # driver path for linux os
            else:
                driver = webdriver.Chrome(executable_path="chromedriver.exe",
                                          options=options)  # driver path for windows
            return driver
        except Exception as e:
            self.dbag.debug_print("Kindly replace the Chrome Web Driver with the latest one from"
                                  "http://chromedriver.chromium.org/downloads"
                                  "\nYour OS: {}".format(platform_) + ", Error: " + str(e))
            exit()


if __name__ == '__main__':
    FBS = FacebookScraper()
    # FBS.public_page_data_scrape(login=True)
    wishtime = properties().wishtime # define a time in the properties file
    FBS.send_private_msg(["You fb friend id"],
                         "Your msg here")
