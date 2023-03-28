import os
import sys

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
