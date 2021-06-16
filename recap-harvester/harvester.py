#!/usr/bin/env python3
import os
import re
import shutil
import sys
import time

from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from PyInquirer import prompt
import colorama

colorama.init()

# Operating system adaptation
tetra_storage = False

Mac = os.getenv("Apple_PubSub_Socket_Render")
file_dividers = False

if Mac is None:
    windows = os.getenv("HOMEDRIVE")
    if windows:
        tetra_storage = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\TetraAIO"
        file_dividers = "\\"

# MAC
if Mac:
    tetra_storage = os.getenv("HOME") + "/Applications/TetraAIO"
    file_dividers = "/"

# Application additions
# todo: proxy support

# Process additions
# todo: colors on appended selection options
# todo: clean up inquirer variables

# Debugs

# TETRA AIO CAPTCHA V2 HARVESTER 1.0.1

# Updates
version = '1.0.1'
clear_method = "clear"


# -----------------


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


os.system("title Tetra AIO Captcha Harvester by Volt#9540 " + 'v' + version)
os.system(clear_method)
dir_path = os.path.dirname(os.path.realpath(__file__))
chromedriver_path = dir_path + file_dividers + "chromedriver"
proxy = '47.79.166.136:17102:zxeamn:dkedjj'


class set_proxy:
    (IPv4, Port, username, password) = proxy.split(':')

    ip = IPv4 + ':' + Port

    proxy_options = {
        "proxy": {
            "http": "http://" + username + ":" + password + "@" + ip,
            "https": "http://" + username + ":" + password + "@" + ip,
        }
    }


class profile_arguments:
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


def question(name, message, choices, q_type):
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
        menu()
        pass
    return answer


def eop(function_driver):
    eop_answer = question(name="End of Process", message="End of process:", choices=['Main Menu', 'Exit'],
                          q_type="list")
    if eop_answer == 'Main Menu':
        os.system(clear_method)
        if function_driver:
            function_driver.close()
        menu()
    if eop_answer == 'Exit':
        os.system(clear_method)
        if function_driver:
            function_driver.close()
        sys.exit(1)


def get_valid_token(function_driver, captcha_type):
    global request
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
                response_list = response_body.split(',')
                recaptcha_token = response_list[1]
                print(recaptcha_token)
                del function_driver.requests
                function_driver.refresh()

                return recaptcha_token
        except TimeoutError:
            os.system(clear_method)
            function_driver.close()
            print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
            menu()
        except TimeoutException:
            os.system(clear_method)
            function_driver.close()
            print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
            menu()
        except Exception as exc:
            os.system(clear_method)
            function_driver.close()
            print("Error occured:", exc)
    return None


# Processes
def login():
    global profile_name_input
    try:
        print(colors.WARNING + 'TETRA AIO GMAIL LOGIN' + colors.END)
        while True:
            profile_name_input = input(colors.CYAN + 'Please enter a profile name: ' + colors.END)
            try:

                print(dir_path)
                browser_storage_beta = dir_path + profile_name_input
                browser_storage = browser_storage_beta.replace('recap-harvester', 'browser-profiles' + file_dividers)

                # os.mkdir(browser_storage, 700)
                profile_arguments.opts.add_argument("user-data-dir=" + browser_storage)
                print(browser_storage)
                break
            except FileExistsError:
                print(colors.FAIL + 'That profile name already exists. Please choose another.' + colors.END)
        print(chromedriver_path)
        login_driver = webdriver.Chrome(chrome_options=profile_arguments.opts, seleniumwire_options=set_proxy.proxy_options,
                                        executable_path=chromedriver_path)
        print(colors.CYAN + "Please enter your login information." + colors.END)
        login_driver.get('https://gmail.com')
        try:
            login_wait = login_driver.wait_for_request(pat='mail/u/0', timeout=100)
        except TimeoutError:
            os.system(clear_method)
            login_driver.close()
            print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
            menu()
        except TimeoutException:
            os.system(clear_method)
            login_driver.close()
            print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
            menu()

        print(
            colors.GREEN + 'Profile Save "' + colors.BOLD + colors.UNDERLINE + profile_name_input + colors.END + colors.GREEN + '" completed!' + colors.END)

        eop(login_driver)
    except InvalidArgumentException:
        print(
            colors.FAIL + 'Please make sure you do not have any other browsers open with the same Browser Profile.' + colors.END)


def captcha(site, captcha_type, token_count):
    global driver

    try:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        browser_storage = dir_path.replace('recap-harvester', 'browser-profiles' + file_dividers)
        browser_profile_list = os.listdir(browser_storage)
        if not browser_profile_list:
            os.system(clear_method)
            print(colors.FAIL + "Please create a profile for use in 'Chrome Login'" + colors.END)
            menu()
        browser_profile_list.append('quick')
        browser_profile_list.append('none')
        browser_profile_list.append("Main Menu")
        profile_name = question(name="Selection", message="Please select a Google Profile:",
                                choices=browser_profile_list, q_type="list")

        browser_storage_beta = dir_path + profile_name
        browser_storage_base = dir_path.replace('recap-harvester', 'browser-profiles' + file_dividers)
        browser_storage = browser_storage_beta.replace('recap-harvester', 'browser-profiles' + file_dividers)
        profile_list = str(os.listdir(browser_storage_base))

        profile_found = re.findall(profile_name, profile_list)
        if profile_found:
            print(colors.GREEN + 'Browser profile Located' + colors.END)
            profile_arguments.opts.add_argument('user-data-dir=' + browser_storage)
            driver = webdriver.Chrome(seleniumwire_options=set_proxy.proxy_options, executable_path=chromedriver_path,
                                      options=profile_arguments.opts)

        elif profile_name == 'none':
            print(colors.GREEN + 'No profile selected' + colors.END)
            driver = webdriver.Chrome(seleniumwire_options=set_proxy.proxy_options, executable_path=chromedriver_path,
                                      options=profile_arguments.opts)

        elif profile_name == 'quick':
            print(colors.GREEN + 'Quick login selected' + colors.END)

            print(colors.CYAN + "Please enter your login information." + colors.END)

            driver = webdriver.Chrome(seleniumwire_options=set_proxy.proxy_options, executable_path='chromedriver',
                                      options=profile_arguments.opts)

            driver.get('https://gmail.com')
            driver.wait_for_request(pat='mail/u/0', timeout=100)

        elif profile_name == 'Main Menu':
            os.system(clear_method)
            menu()
        else:
            os.system(clear_method)
            print(
                colors.FAIL + 'Browser profile could not be located. Please make sure you typed in the correct name' + colors.END)
            menu()

        # ReCaptcha V2 [Valid Token] Function Call

        if captcha_type == "ReCaptcha V2":

            if site == "Demo":
                driver.get("https://www.google.com/recaptcha/api2/demo")
            if site != "Demo":
                driver.get("https://%s.com/checkpoint" % site)

            v2_token_list = []
            for v2_token in range(token_count):
                v2_token_list.append(get_valid_token(driver, captcha_type))

        # ReCaptcha V3 [Valid Token] Function Call

        if captcha_type == "ReCaptcha V3":

            if site == "Demo":
                driver.get("https://login.wordpress.org/wp-login.php")
            if site != "Demo":
                driver.get("google.com")

            v3_token_list = []
            for v3_token in range(token_count):
                v3_token_list.append(get_valid_token(driver, captcha_type))

        eop(driver)
    except InvalidArgumentException:
        os.system(clear_method)
        print(
            colors.FAIL + 'Please make sure you do not have any other browsers open with the same Browser Profile.' + colors.END)
        driver.close()
        menu()


def profiles():
    try:
        print("Select a Browser Profile to edit.")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        browser_storage = dir_path.replace('recap-harvester',
                                           'browser-profiles' + file_dividers)
        browser_profile_list = os.listdir(browser_storage)
        browser_profile_list.append('Main Menu')
        browser_profile_list.append('Exit')

        # Choose browser profile to edit list

        profile_answer = question(name="Browser Profile List", message="Select a browser profile:",
                                  choices=browser_profile_list, q_type="list")
        if not profile_answer:
            os.system(clear_method)
            menu()
        if profile_answer == colors.CYAN + 'Main Menu' + colors.END:
            os.system(clear_method)
            menu()
        if profile_answer == colors.CYAN + 'Exit' + colors.END:
            os.system(clear_method)
            sys.exit(1)

        os.system(clear_method)
        print(colors.WARNING + colors.BOLD + colors.UNDERLINE + profile_answer + colors.END)

        # Edit options
        edit_answer = question(name="EditOptions", message="Select an edit option:",
                               choices=['Change Name', colors.FAIL + 'Delete' + colors.END,
                                        colors.CYAN + 'Go back' + colors.END], q_type="list")

        if edit_answer == colors.CYAN + 'Go back' + colors.END:
            os.system(clear_method)
            profiles()
        if edit_answer == 'Change Name':
            os.system(clear_method)
            print(colors.WARNING + profile_answer + colors.END)
            for RenameRetry in range(100):
                try:
                    Rename_input = input(colors.CYAN + 'Please enter a new name for the browser profile: ' + colors.END)

                    OG_path = browser_storage + profile_answer
                    Rename_path = browser_storage + Rename_input

                    # Rename
                    os.rename(OG_path, Rename_path)

                    print(
                        colors.GREEN + 'Browser Profile: "' + profile_answer + '" has been renamed to: "' + Rename_input + '"' + colors.END)
                    break

                except FileExistsError:
                    print(colors.FAIL + 'That profile name already exists. Please choose another.' + colors.END)
                    continue
        if edit_answer == colors.FAIL + 'Delete' + colors.END:
            shutil.rmtree(browser_storage + profile_answer)
            print(colors.GREEN + 'Browser Profile: "' + profile_answer + '" has been deleted.' + colors.END)

        eop(None)
    except InvalidArgumentException:
        print(
            colors.FAIL + 'Please make sure you do not have any other browsers open with the same Browser Profile.' + colors.END)
    except TimeoutError:
        os.system(clear_method)
        print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
        menu()
    except TimeoutException:
        os.system(clear_method)
        print(colors.FAIL + 'Tetra Harvester timed out. Please restart and try again.' + colors.END)
        menu()


def menu():
    global site_list
    menu_answer = question(name="Selection", message="Main Menu", choices=['Captcha Harvester', 'Chrome Login', 'Your Browser Profiles', 'Exit'], q_type="list")

    if menu_answer == "Chrome Login":
        os.system(clear_method)
        login()

    if menu_answer == "Captcha Harvester":

        # os.system(clear_method)

        recaptcha_answer = question(name="ReCaptcha", message="Select a ReCaptcha type:", choices=["ReCaptcha V2", "ReCaptcha V3", "Main Menu", "Exit"], q_type="list")

        if recaptcha_answer == "ReCaptcha V2":
            site_list = ['Kith', 'DTLR', 'Demo', 'Main Menu', 'Exit']

        if recaptcha_answer == "ReCaptcha V3":
            site_list = ["Demo"]

        if recaptcha_answer == 'Main Menu':
            os.system(clear_method)
            menu()
        elif recaptcha_answer == 'Exit':
            os.system(clear_method)
            sys.exit(1)

        # os.system(clear_method)

        site_answer = question(name="Site", message="Select a site:", choices=site_list, q_type="list")

        if site_answer == 'Main Menu':
            os.system(clear_method)
            menu()
        elif site_answer == 'Exit':
            os.system(clear_method)
            sys.exit(1)
        # os.system(clear_method)

        # Call Captcha Function
        captcha(site_answer, recaptcha_answer, 2)

    if menu_answer == 'Your Browser Profiles':
        os.system(clear_method)
        profiles()

    if menu_answer == 'Exit':
        os.system(clear_method)
        sys.exit(1)


if __name__ == '__main__':
    os.system(clear_method)
    print(colors.CYAN + colors.BOLD + 'WELCOME TO THE TETRA AIO CAPTCHA HARVESTER' + colors.END)
    menu()
