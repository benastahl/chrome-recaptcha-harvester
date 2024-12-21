import threading
import urllib3
import colorama
import os
import uuid
import zipfile
import chromedriver_autoinstaller

from datetime import datetime
from termcolor import colored

from selenium.common.exceptions import InvalidArgumentException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver as selenium_webdriver
import _utils

colorama.init()
chromedriver_autoinstaller.install(path=os.getcwd() + _utils.fd + "chromedrivers", no_ssl=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

token_lock, captcha_lock = threading.Lock(), threading.Lock(),

# Harvester
harvesters = []
token_inquirers = {}
tokens = {}


class Harvester:
    def __init__(self, proxy, num, profile_name):
        self.driver = None
        self.num = num
        self.proxy = proxy
        self.profile_name = profile_name

    def log(self, text, status):
        statuses = {
            "s": 'green',
            "f": "red",
            "p": "cyan",
            "d": "yellow",
        }
        if status in statuses:
            print(colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [{self.num}] - [Captcha Harvester] - {text}",
                statuses[status]))

    @staticmethod
    def token_needed():
        global tokens
        token_lock.acquire()
        if len(token_inquirers) > 0:
            return list(token_inquirers.keys())[0]
        return False

    def waiting(self):
        waiting_html = """
        <html lang="en">

            <style>
                .waiting-title {
                    margin-top: 150px;

                }
                h1 {
                text-align: center;
                font-size: 45px;
                }
                img {
                text-align: center;
                }
            </style>

            <head>
                <meta charset="UTF-8">
                <title>Chrome Captcha Harvester</title>
            </head>

            <body>
                <h1 class="waiting-title">Waiting for Captcha...</h1>
                <h1 style="font-size: 20px;">Harvester: %s</h1>
                <h1 style="font-size: 20px;">Profile: %s</h1>
                <!-- <img src="https://thumbs.gfycat.com/AgonizingDiligentHapuka-max-1mb.gif" alt="Loading..." width="500" height="300"> -->
            </body>

        </html>


                """ % (self.num, self.profile_name)
        self.driver.get("data:text/html;charset=utf-8," + waiting_html)

    def open(self):
        chrome_options = _utils.profile_arguments(Options(), profile_name=self.profile_name)

        # Proxy Setting (extension)
        if self.proxy:
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (_utils.proxy_config(self.proxy))
            pluginfile = 'proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)

        self.driver = selenium_webdriver.Chrome(chrome_options=chrome_options)
        self.waiting()

    def wait_for_captcha(self):
        try:
            self.waiting()
            while True:

                task_id = self.token_needed()
                if task_id:
                    self.log("Token in need! Grabbing one...", "p")
                    task = token_inquirers[task_id]
                    token_inquirers.pop(task_id)
                    token_lock.release()

                    self.driver.get(task["url"])
                    g_recaptcha_token = self.get_valid_token(task["type"])
                    with token_lock:
                        tokens[task_id] = g_recaptcha_token
                    self.waiting()
                    continue
                token_lock.release()
        except InvalidArgumentException:
            self.driver.quit()
            raise InvalidArgumentException('Make sure you do not have any browsers open with the same browser profile.')

    def get_valid_token(self, captcha_type):
        self.log("Waiting for Captcha...", "p")

        frame_titles = {
            "v2": "recaptcha challenge expires in two minutes",
            "v3": "reCAPTCHA"
        }
        try:
            frame = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"iframe[title='{frame_titles[captcha_type]}']")))
            self.driver.switch_to.frame(frame)
        except TimeoutError or TimeoutException:
            self.driver.refresh()
            return self.get_valid_token(captcha_type)

        recaptcha_token = None
        while not recaptcha_token:
            try:
                recaptcha_token = self.driver.find_element(By.ID, "recaptcha-token").get_attribute('value')
            except NoSuchElementException:
                self.log("no elem.", "p")
                pass

        self.log('Valid token found', "s")
        return recaptcha_token


def chrome_login(profile_name: str):
    try:
        try:
            if profile_name in os.listdir(_utils.get_profiles_path("")):
                raise AssertionError(
                    "Failed to create new browser profile. Try a different name.")

            print("Opening with new user data...")
            login_args = _utils.profile_arguments(selenium_webdriver.ChromeOptions(), profile_name=profile_name)

            driver = selenium_webdriver.Chrome(options=login_args)

        except FileExistsError:
            raise FileExistsError('That profile name already exists. Choose another.')
        # except WebDriverException:
        #     print("Chromedriver version is OUT OF DATE. Replace with latest stable version.")

        print("Enter your login information.")
        driver.get('https://gmail.com')
        input("Press enter once you have logged in: ")

        driver.quit()
        print(f'Profile Save "{profile_name}" completed.')
    except InvalidArgumentException:
        raise InvalidArgumentException(
            "Make sure you do not have any browsers open with the same browser profile.")


def open_harvester(profile_name: str, proxy=None):
    browser_profiles = os.listdir(_utils.get_profiles_path(""))
    assert profile_name in browser_profiles, "Profile not found."

    harvester = Harvester(
        num=len(harvesters) + 1,
        proxy=proxy,
        profile_name=profile_name
    )
    harvesters.append(harvester)
    harvester.open()
    threading.Thread(target=harvester.wait_for_captcha, args=()).start()


def harvest_token(captcha_type, url):
    print("In queue for captcha token...")
    global tokens
    with token_lock:
        task_id = uuid.uuid4()
        token_inquirers[task_id] = {
            "type": captcha_type,
            "url": url,
        }

    # Enter queue to get token
    with captcha_lock:
        while not tokens.get(task_id):
            continue
        g_recaptcha_token = tokens[task_id]
        print("Task received token:", g_recaptcha_token)
        with token_lock:
            tokens.pop(task_id)

    return g_recaptcha_token