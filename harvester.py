import threading
import urllib3
import colorama
import os
import uuid
import chromedriver_autoinstaller
import time

import _utils
from _utils import Token, Harvester, token_lock, captcha_lock, harvesters, tokens

from selenium.common.exceptions import InvalidArgumentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

colorama.init()
chromedriver_autoinstaller.install(path=os.getcwd() + _utils.fd + "chromedrivers", no_ssl=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Harvester

def chrome_login(profile_name: str) -> None:
    """
    Opens a Chrome browser with a new user profile for manual login (e.g., Gmail).
    Saves the profile after login for future automated use.

    :param profile_name: The name of the browser profile to create and save.
    :return: None
    :raises AssertionError: If the profile already exists in the profile directory.
    :raises FileExistsError: If a conflicting profile name is found.
    :raises InvalidArgumentException: If Chrome fails to launch due to profile conflicts.
    """
    try:
        try:
            if profile_name in os.listdir(_utils.get_profiles_path("")):
                raise AssertionError(
                    "Failed to create new browser profile. Try a different name.")

            print("Opening with new user data...")
            login_args = _utils.profile_arguments(
                selenium_webdriver.ChromeOptions(),
                profile_name=profile_name
            )

            driver = selenium_webdriver.Chrome(options=login_args)

        except FileExistsError:
            raise FileExistsError('That profile name already exists. Choose another.')

        print("Enter your login information.")
        driver.get('https://gmail.com')

        try:
            WebDriverWait(driver, 120).until(
                EC.url_contains('mail.google.com/mail')
            )
        except TimeoutException:
            driver.quit()
            raise TimeoutException("Login timed out.")

        driver.quit()
        print(f'Profile Save "{profile_name}" completed.')

    except InvalidArgumentException:
        raise InvalidArgumentException(
            "Make sure you do not have any browsers open with the same browser profile.")

def open_harvester(profile_name: str, proxy: Optional[str] = None) -> None:
    """
    Launches a CAPTCHA harvester using the given browser profile and optional proxy.

    :param profile_name: The name of the browser profile to use.
    :param proxy: An optional proxy address to route the harvester traffic through.
    :return: None
    :raises AssertionError: If the specified profile name is not found.
    """
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

def harvest_token(captcha_type: str, captcha_url: str, task_id: str = str(uuid.uuid4())) -> Token:
    """
    Handles the process of acquiring a CAPTCHA token in a thread-safe manner.

    This function registers a task (identified by `task_id`) that requires a CAPTCHA
    token, enters a synchronized queue to wait for the token to be generated,
    and returns the token once it's available.

    :param captcha_type: The type of CAPTCHA to be solved (e.g., 'recaptcha', 'hcaptcha').
    :param captcha_url: The URL for which the CAPTCHA token is being requested.
    :param task_id: (optional) A unique identifier for the token request task. Defaults to a new UUID.

    :return: The acquired CAPTCHA token associated with the task.
    """

    global tokens

    # Register this token request under a thread-safe token_inquirers dictionary
    with token_lock:
        tokens[task_id] = Token(
            task_id=task_id,
            captcha_type=captcha_type,
            captcha_url=captcha_url
        )

    # Wait for token availability in a thread-safe way using captcha_lock
    with captcha_lock:

        # Busy-wait loop until a token is assigned for this task_id
        token = tokens.get(task_id)
        while not token.g_recaptcha_token:
            time.sleep(0.5)  # let's not kill your computer
            continue  # This is a spinlock; could be optimized with sleep or event

        # Optional cleanup: remove the token from the dictionary if no longer needed
        # with token_lock:
        #     tokens.pop(task_id)

    return token

def token_ready(task_id: str) -> bool:
    """
    Checks whether a CAPTCHA token has been set for a given task.

    Thread-safe access to the global tokens dictionary.

    :param task_id: The ID of the CAPTCHA task to check.
    :type task_id: str
    :return: True if a token is present, False otherwise.
    :rtype: bool
    :raises KeyError: If the task_id is not found in the tokens dictionary.
    """
    global tokens
    with token_lock:
        token = tokens.get(task_id)
        return bool(token and token.g_recaptcha_token)

def get_token_safely(task_id: str) -> Token:
    """
    Safely retrieves a Token object associated with the given task_id from the global tokens dictionary.

    Access is thread-safe using a lock to prevent race conditions.

    :param task_id: The ID of the CAPTCHA task whose token is being retrieved.
    :type task_id: str
    :return: The Token object associated with the given task_id.
    :rtype: Token
    :raises KeyError: If no token is found for the given task_id.
    """
    global tokens
    with token_lock:
        token = tokens.get(task_id)  # May raise KeyError if task_id not present

    return token
