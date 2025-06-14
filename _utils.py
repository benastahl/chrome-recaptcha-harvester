import os
import sys
import zipfile
import threading
import time

from datetime import datetime, timedelta
from termcolor import colored
from typing import Optional, Dict

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.support import expected_conditions as EC

token_lock, captcha_lock = threading.Lock(), threading.Lock()

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
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - [Captcha Harvester] - [{self.num}] - {text}",
                statuses[status]))

    @staticmethod
    def token_needed():
        global tokens
        token_lock.acquire()

        # dear god. pretty much just getting the tokens that have been inquired but not collected yet.
        inquired_tokens = [key for key, token in tokens.items() if not token.ingested]

        # if there are any inquired tokens, go grab the latest one inquired (first in, last out)
        if len(inquired_tokens) > 0:
            return inquired_tokens[0]

        return None

    def waiting(self):
        try:
            with open("harvester.html", "r", encoding="utf-8") as f:
                waiting_html = f.read()
        except FileNotFoundError:
            self.log("Missing 'harvester.html' file", "f")
            return

        # Inject dynamic values (e.g., %s placeholders)
        waiting_html = waiting_html % (self.num, self.profile_name)

        self.driver.get("data:text/html;charset=utf-8," + waiting_html)

    def open(self):
        chrome_options = profile_arguments(Options(), profile_name=self.profile_name)

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
            """ % (proxy_config(self.proxy))
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
                    self.log(f"Token in need! Grabbing one (task: {task_id})...", "p")
                    token = tokens[task_id]
                    tokens[task_id].ingested = True
                    token_lock.release()

                    self.driver.get(token.captcha_url)

                    g_recaptcha_token = self.get_valid_token(token.captcha_type)
                    with token_lock:
                        tokens[task_id].g_recaptcha_token = g_recaptcha_token
                        tokens[task_id].profile_used = self.profile_name
                        tokens[task_id].proxy_used = self.proxy
                        tokens[task_id].expiry_datetime = datetime.now() + timedelta(minutes=2)

                    self.waiting()

                    continue
                time.sleep(0.5)
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

        self.log(f'Valid token found.', "s")
        return recaptcha_token


class Token:
    """
    Represents a CAPTCHA token task, including request metadata and harvesting results.

    This class is used to track the lifecycle of a CAPTCHA-solving task, including its
    identifier, where the challenge occurred, the type of CAPTCHA, the solution token,
    and the environment used to solve it (profile and proxy).

    :param task_id: A unique identifier for the CAPTCHA request task.
    :type task_id: str
    :param captcha_url: The URL where the CAPTCHA challenge was encountered.
    :type captcha_url: str
    :param captcha_type: The type of CAPTCHA (e.g., 'recaptcha', 'hcaptcha').
    :type captcha_type: str

    :ivar task_id: The unique ID of the CAPTCHA task.
    :vartype task_id: str
    :ivar captcha_url: The URL associated with the CAPTCHA challenge.
    :vartype captcha_url: str
    :ivar captcha_type: The type of CAPTCHA (e.g., 'v2', 'v3').
    :vartype captcha_type: str
    :ivar g_recaptcha_token: The solved CAPTCHA token, if available.
    :vartype g_recaptcha_token: Optional[str]
    :ivar profile_used: The browser profile used to solve the CAPTCHA.
    :vartype profile_used: Optional[str]
    :ivar proxy_used: The proxy used for the CAPTCHA request, if any.
    :vartype proxy_used: Optional[str]
    :ivar expiry_datetime: The timestamp when the token was obtained; used to determine expiration.
    :vartype expiry_datetime: Optional[datetime]
    :ivar expired: Whether the token has expired (valid for 2 minutes after creation).
    :vartype expired: bool
    :ivar expires_in_seconds: Number of seconds remaining before the token expires (max 120).
    :vartype expires_in_seconds: Optional[int]
    """

    def __init__(self,
                 task_id: str,
                 captcha_url: str,
                 captcha_type: str):
        self.task_id = task_id
        self.captcha_url = captcha_url
        self.captcha_type = captcha_type
        self.ingested = False

        # Set later by CAPTCHA harvesting process
        self.g_recaptcha_token: Optional[str] = None
        self.profile_used: Optional[str] = None
        self.proxy_used: Optional[str] = None
        self.expiry_datetime: Optional[datetime] = None

    def __repr__(self):
        return (f"Token(task_id={self.task_id!r}, "
                f"captcha_url={self.captcha_url!r}, "
                f"captcha_type={self.captcha_type!r}, "
                f"g_recaptcha_token={self.g_recaptcha_token!r}, "
                f"profile_used={self.profile_used!r}, "
                f"proxy_used={self.proxy_used!r}, "
                f"expiry_datetime={self.expiry_datetime!r}, "
                f"expired={self.expired!r})")

    @property
    def expired(self) -> bool:
        if not self.expiry_datetime:
            return True  # No timestamp means it hasn't been set yet
        return datetime.now() > self.expiry_datetime

    @property
    def expires_in_seconds(self) -> Optional[int]:
        if not self.expiry_datetime:
            return None
        delta = self.expiry_datetime - datetime.now()
        return max(0, int(delta.total_seconds()))


harvesters = []
tokens: Dict[str, Token] = {}

if sys.platform.startswith("win"):
    clear_method = "cls"
    fd = "\\"
else:
    clear_method = "clear"
    fd = "/"


def get_profiles_path(profile_name):
    return os.getcwd() + fd + "browser-profiles" + fd + profile_name


def proxy_config(proxy):
    if not proxy:
        return {}

    try:
        (IPv4, Port, username, password) = proxy.split(':')
        return IPv4, Port, username, password
    except ValueError:
        raise ValueError("Invalid proxy.")


def profile_arguments(opts, profile_name=None):
    if profile_name:
        opts.add_argument("--user-data-dir=" + get_profiles_path(profile_name))

    args = [
        "--allow-insecure-localhost",
        "--ignore-ssl-errors",
        '--ignore-certificate-errors-spki-list',
        '--ignore-certificate-errors',
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "--disable-blink-features",
        "--disable-blink-features=AutomationControlled",
        # '--disable-extensions',
        'disable-infobars',
        '--window-size=500,645',
        '--allow-profiles-outside-user-dir'
    ]
    for arg in args:
        opts.add_argument(arg)

    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    return opts
