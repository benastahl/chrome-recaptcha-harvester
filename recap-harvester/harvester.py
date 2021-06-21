#!/usr/bin/env python3
import os
import re
import shutil
import sys
import time
import colorama

from selenium.common.exceptions import TimeoutException, InvalidArgumentException, WebDriverException
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from PyInquirer import prompt

# Updates
version = '1.0.1'

colorama.init()
file_dividers = None
clear_method = None
chromedriver_file = None

# Operating system adaptation

Mac = os.getenv("Apple_PubSub_Socket_Render")

if not Mac:
    windows = os.getenv("HOMEDRIVE")
    clear_method = "cls"
    chromedriver_file = "chromedriver.exe"
    file_dividers = "\\"

if Mac:
    file_dividers = "/"
    clear_method = "clear"
    chromedriver_file = "chromedriver_mac"


class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


os.system("title CHROME Captcha Harvester by Volt#9540 " + 'v' + version)
os.system(clear_method)
dir_path = os.path.dirname(os.path.realpath(__file__))
browser_profile_dir = dir_path.replace('recap-harvester', 'browser-profiles' + file_dividers)
chromedriver_path = dir_path + file_dividers + chromedriver_file

# CHROME CAPTCHA V2 HARVESTER 1.0.1

localhost = True
proxy = '47.79.166.136:17102:zxeamn:dkedjj'
token_count = 2


(IPv4, Port, username, password) = proxy.split(':')

ip = IPv4 + ':' + Port

proxy_options = {
    "proxy": {
        "http": "http://" + username + ":" + password + "@" + ip,
        "https": "http://" + username + ":" + password + "@" + ip,
    }
}
if localhost:
    proxy_options = {}


def profile_arguments():
    opts = Options()
    opts.add_argument('--allow-insecure-localhost')
    opts.add_argument('--ignore-ssl-errors')
    opts.add_argument('--ignore-certificate-errors-spki-list')
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument("user-agent=Chrome")
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('--disable-extensions')
    opts.add_argument('disable-infobars')
    opts.add_argument('--window-size=500,645')
    opts.add_argument('--allow-profiles-outside-user-dir')
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    return opts


def question(web_driver, name, message, choices, q_type):
    answer = None
    questions = None

    if q_type == "list":
        questions = [
            {
                'type': q_type,
                'name': name,
                'message': message,
                "choices": choices
            }
        ]
    if q_type == "input":
        questions = [
            {
                'type': q_type,
                'name': name,
                'message': message,
            }
        ]

    try:
        answer = prompt(questions)[name]
    except KeyError:
        os.system(clear_method)
        menu(web_driver)
        pass
    return answer


def list_search(search_item, list_obj):
    for list_count in range(len(list_obj)):
        list_item = list_obj[list_count]

        if list_item == search_item:
            return True
    return False


def eop(function_driver):
    eop_answer = question(function_driver, name="End of Process", message="End of process:", choices=['Main Menu', 'Exit'],
                          q_type="list")
    if eop_answer == 'Main Menu':
        os.system(clear_method)
        # if function_driver:
        #     function_driver.close()
        menu(function_driver)
    if eop_answer == 'Exit':
        os.system(clear_method)
        if function_driver:
            function_driver.close()
        sys.exit(1)


def get_valid_token(function_driver, captcha_type):
    request = None
    for failedVerify in range(100):
        print(colors.CYAN + "Waiting for Captcha..." + colors.END)

        try:
            if captcha_type == "ReCaptcha V2":
                request = function_driver.wait_for_request(pat='/recaptcha/api2/userverify', timeout=10000)

            if captcha_type == "ReCaptcha V3":
                if failedVerify != 0:
                    time.sleep(2)
                    function_driver.refresh()
                request = function_driver.wait_for_request(pat='/recaptcha/api2/reload', timeout=10000)

            response_body = str(request.response.body).replace('"', '')
            response_list = response_body.split(',')
            recaptcha_token = response_list[1]
            invalid_token = re.findall("bgdata", response_body)
            if invalid_token:
                print(colors.FAIL + "Invalid token, looking for valid..." + colors.END)
                del function_driver.requests
                print(recaptcha_token)
                # print(colors.WARNING + "Deleted requests history and searching..." + colors.END)
            else:
                print(colors.GREEN + 'Valid token found' + colors.END)
                print(recaptcha_token)
                del function_driver.requests
                function_driver.refresh()

                return recaptcha_token
        except TimeoutError:
            os.system(clear_method)
            function_driver.close()
            print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
            menu(function_driver)
        except TimeoutException:
            os.system(clear_method)
            function_driver.close()
            print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
            menu(function_driver)
        except Exception as exc:
            os.system(clear_method)
            function_driver.close()
            print("Error occurred:", exc)
    return None


# Processes
def login(web_driver):
    try:
        print(colors.WARNING + 'CHROME GMAIL LOGIN' + colors.END)
        web_driver.close()
        while True:
            profile_name_input = input(colors.CYAN + 'Profile name: ' + colors.END)
            try:

                browser_storage = browser_profile_dir + profile_name_input
                print(colors.CYAN + "Opening with new user data..." + colors.END)
                login_args = profile_arguments()
                login_args.add_argument("user-data-dir=" + browser_storage)

                web_driver = webdriver.Chrome(options=login_args, seleniumwire_options=proxy_options,
                                              executable_path=chromedriver_path)

                break
            except FileExistsError:
                print(colors.FAIL + 'That profile name already exists. Choose another.' + colors.END)
            except WebDriverException:
                print(colors.FAIL + "Failed to create new browser profile. Try a different name." + colors.END)

        print(colors.CYAN + "Enter your login information." + colors.END)
        web_driver.get('https://gmail.com')
        try:
            web_driver.wait_for_request(pat='mail/u/0', timeout=100)
        except TimeoutError:
            os.system(clear_method)
            web_driver.close()
            print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
            menu(web_driver)
        except TimeoutException:
            os.system(clear_method)
            web_driver.close()
            print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
            menu(web_driver)

        print(
            colors.GREEN + 'Profile Save "' + colors.BOLD + colors.UNDERLINE + profile_name_input + colors.END + colors.GREEN + '" completed!' + colors.END)

        eop(web_driver)
    except InvalidArgumentException:
        print(
            colors.FAIL + 'Make sure you do not have any browsers open with the same browser profile.' + colors.END)
    except WebDriverException:
        print(colors.FAIL + "Invalid browser profile name. Enter a new name." + colors.END)


def captcha(web_driver, site, captcha_type):
    try:

        browser_profile_list = os.listdir(browser_profile_dir)
        if not browser_profile_list:
            os.system(clear_method)
            print(colors.FAIL + "Create a profile for use in 'Chrome Login'" + colors.END)
            menu(web_driver)
        browser_profile_list.extend(['quick', 'none', 'Main Menu'])

        profile_name = question(web_driver, name="Selection", message="Browser profile:",
                                choices=browser_profile_list, q_type="list")

        browser_storage = browser_profile_dir + profile_name
        profile_list = os.listdir(browser_profile_dir)

        profile_found = list_search(profile_name, profile_list)
        if profile_found:
            print(colors.GREEN + 'Browser profile located' + colors.END)
            print(colors.CYAN + "Opening with new user data..." + colors.END)
            captcha_args = profile_arguments()
            captcha_args.add_argument('--user-data-dir=' + browser_storage)
            web_driver.close()
            web_driver = webdriver.Chrome(seleniumwire_options=proxy_options, executable_path=chromedriver_path, options=captcha_args)

        elif profile_name == 'none':
            print(colors.GREEN + 'No profile selected' + colors.END)

        elif profile_name == 'quick':
            print(colors.GREEN + 'Quick login selected' + colors.END)

            print(colors.CYAN + "Enter your login information." + colors.END)

            web_driver.get('https://gmail.com')
            web_driver.wait_for_request(pat='mail/u/0', timeout=100)

        elif profile_name == 'Main Menu':
            os.system(clear_method)
            menu(web_driver)
        else:
            os.system(clear_method)
            print(
                colors.FAIL + 'Failed to locate browser profile.' + colors.END)
            menu(web_driver)

        # ReCaptcha V2 [Valid Token] Function Call

        if captcha_type == "ReCaptcha V2":

            if site == "Demo":
                web_driver.get("https://www.google.com/recaptcha/api2/demo")
            if site != "Demo":
                web_driver.get("https://%s.com/checkpoint" % site)

            v2_token_list = []
            for v2_token in range(token_count):
                g_recaptcha_token = get_valid_token(web_driver, captcha_type)
                v2_token_list.append(g_recaptcha_token)

        # ReCaptcha V3 [Valid Token] Function Call

        if captcha_type == "ReCaptcha V3":

            if site == "Demo":
                web_driver.get("https://login.wordpress.org/wp-login.php")
            if site != "Demo":
                web_driver.get("google.com")

            v3_token_list = []
            for v3_token in range(token_count):
                v3_token_list.append(get_valid_token(web_driver, captcha_type))
                print(v3_token_list)

        eop(web_driver)
    except InvalidArgumentException:
        os.system(clear_method)
        print(
            colors.FAIL + 'Make sure you do not have any browsers open with the same browser profile.' + colors.END)
        web_driver.close()
        menu(web_driver)


def profiles(web_driver):
    try:
        print("Select a browser profile to edit.")
        browser_profile_list = os.listdir(browser_profile_dir)
        browser_profile_list.extend(['Main Menu', 'Exit'])

        # Choose browser profile to edit list

        profile_answer = question(web_driver, name="Browser Profile List", message="Select a browser profile:",
                                  choices=browser_profile_list, q_type="list")
        if not profile_answer:
            os.system(clear_method)
            menu(web_driver)
        if profile_answer == 'Main Menu':
            os.system(clear_method)
            menu(web_driver)
        if profile_answer == 'Exit':
            os.system(clear_method)
            sys.exit(1)

        os.system(clear_method)
        print(colors.WARNING + colors.BOLD + colors.UNDERLINE + profile_answer + colors.END)

        # Edit options
        edit_answer = question(web_driver, name="EditOptions", message="Select an edit option:",
                               choices=['Change name', 'Delete', 'Go back'], q_type="list")

        if edit_answer == 'Go back':
            os.system(clear_method)
            profiles(web_driver)
        if edit_answer == 'Change name':
            os.system(clear_method)
            print(colors.WARNING + profile_answer + colors.END)
            while True:
                try:
                    Rename_input = input(colors.CYAN + 'Enter a new name for the browser profile: ' + colors.END)

                    og_path = browser_profile_dir + profile_answer
                    rename_path = browser_profile_dir + Rename_input

                    # Rename
                    os.rename(og_path, rename_path)

                    print(
                        colors.GREEN + 'Browser Profile: "' + profile_answer + '" has been renamed to: "' + Rename_input + '"' + colors.END)
                    break

                except FileExistsError:
                    print(colors.FAIL + 'That profile name already exists. Choose another.' + colors.END)
                    continue
        if edit_answer == 'Delete':
            shutil.rmtree(browser_profile_dir + profile_answer)
            print(colors.GREEN + 'Browser profile: "' + profile_answer + '" has been deleted.' + colors.END)

        eop(web_driver)
    except InvalidArgumentException:
        print(
            colors.FAIL + 'Make sure you do not have any browsers open with the same browser profile.' + colors.END)
    except TimeoutError:
        os.system(clear_method)
        print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
        menu(web_driver)
    except TimeoutException:
        os.system(clear_method)
        print(colors.FAIL + 'Chrome Harvester timed out. Restart and try again.' + colors.END)
        menu(web_driver)


def menu(web_driver):
    web_driver.close()
    web_driver = webdriver.Chrome(options=profile_arguments(), seleniumwire_options=proxy_options, executable_path=chromedriver_path)
    web_driver.get("http://127.0.0.1:8000")
    site_list = None

    menu_answer = question(web_driver, name="Selection", message="Main Menu",
                           choices=['Captcha Harvester', 'Chrome Login', 'Your Browser Profiles', 'Exit'],
                           q_type="list")

    if menu_answer == "Chrome Login":
        os.system(clear_method)
        login(web_driver)

    if menu_answer == "Captcha Harvester":

        recaptcha_answer = question(web_driver, name="ReCaptcha", message="ReCaptcha type:",
                                    choices=["ReCaptcha V2", "ReCaptcha V3", "Main Menu", "Exit"], q_type="list")

        if recaptcha_answer == "ReCaptcha V2":
            site_list = ['Kith', 'DTLR', 'Demo', 'Main Menu', 'Exit']

        if recaptcha_answer == "ReCaptcha V3":
            site_list = ["Demo"]

        if recaptcha_answer == 'Main Menu':
            os.system(clear_method)
            menu(web_driver)
        elif recaptcha_answer == 'Exit':
            os.system(clear_method)
            sys.exit(1)

        site_answer = question(web_driver, name="Site", message="Site:", choices=site_list, q_type="list")

        if site_answer == 'Main Menu':
            os.system(clear_method)
            menu(web_driver)
        elif site_answer == 'Exit':
            os.system(clear_method)
            sys.exit(1)

        # Call Captcha Function
        captcha(web_driver, site_answer, recaptcha_answer)

    if menu_answer == 'Your Browser Profiles':
        os.system(clear_method)
        profiles(web_driver)

    if menu_answer == 'Exit':
        os.system(clear_method)
        sys.exit(1)


if __name__ == '__main__':
    os.system(clear_method)
    print(colors.CYAN + colors.BOLD + 'WELCOME TO THE CHROME CAPTCHA HARVESTER' + colors.END)
    driver = webdriver.Chrome(options=profile_arguments(), seleniumwire_options=proxy_options, executable_path=chromedriver_path)
    driver.get("http://127.0.0.1:8000/loading")
    menu(driver)
